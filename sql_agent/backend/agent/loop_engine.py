"""Agent Loop Engine — Token Budget + 自适应终止 + 失败自愈 + 缓存 + 反思 (Phase 1)"""
import json
import time
import re
import difflib
import logging
from typing import Optional
from dataclasses import dataclass, field
from typing import List, Dict

logger = logging.getLogger("db_agent.loop")


# ══════════════════════════════════════════════════════
# Token Budget 经济模型
# ══════════════════════════════════════════════════════

class TokenBudget:
    """Agent Token 预算管理器 —— 追踪每轮 LLM 消耗，超预算自动降级"""

    def __init__(self, max_total_tokens: int = 30000, warning_threshold: float = 0.8):
        self.max_total = max_total_tokens
        self.warning_threshold = warning_threshold
        self.total_consumed = 0
        self.round_consumptions: list = []
        self._degraded = False

    def record_round(self, prompt_tokens: int, completion_tokens: int) -> dict:
        consumed = prompt_tokens + completion_tokens
        self.round_consumptions.append({
            "round": len(self.round_consumptions) + 1,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total": consumed,
        })
        self.total_consumed += consumed
        logger.debug(f"[Budget] 第{len(self.round_consumptions)}轮: {consumed} tokens (累计 {self.total_consumed})")
        return self.get_status()

    def get_status(self) -> dict:
        ratio = self.total_consumed / self.max_total if self.max_total else 0
        status = (
            "exceeded" if ratio >= 1.0
            else "critical" if ratio > 0.95
            else "warning" if ratio > self.warning_threshold
            else "normal"
        )
        return {
            "total_consumed": self.total_consumed,
            "remaining": self.max_total - self.total_consumed,
            "usage_ratio": round(ratio, 3),
            "status": status,
            "degraded": self._degraded,
        }

    def should_degrade(self) -> bool:
        if self._degraded:
            return True
        if self.get_status()["usage_ratio"] > self.warning_threshold:
            self._degraded = True
            logger.warning("[Budget] 进入降级模式（精简 System Prompt）")
            return True
        return False


# ══════════════════════════════════════════════════════
# Adaptive Loop Controller — 五维信号联合判断
# ══════════════════════════════════════════════════════

class AdaptiveLoopController:
    """自适应循环终止控制器 —— 五维信号联合判断"""

    def __init__(self, max_rounds: int = 8, staleness_window: int = 3):
        self.max_rounds = max_rounds
        self.staleness_window = staleness_window
        self.tool_call_fingerprints: list = []
        self.info_gain_history: list = []
        self.successive_failures = 0

    def _fingerprint(self, tool_calls: list) -> str:
        if not tool_calls:
            return ""
        keys = sorted([
            f"{tc.get('function', {}).get('name', '')}:{tc.get('function', {}).get('arguments', '')}"
            for tc in tool_calls
        ])
        return str(hash(tuple(keys)))

    def _info_gain(self, results: list) -> float:
        gain = 0.0
        for r in results:
            if not r.get("success"):
                continue
            rows = max(r.get("row_count", 0), 1)
            tables_count = max(len(r.get("tables", [])), 1)
            cols_count = max(len(r.get("columns", [])), 1)
            gain += min(rows / 100.0, 1.0) + min(tables_count / 5.0, 1.0) + min(cols_count / 20.0, 1.0)
        return gain

    def evaluate(self, round_num: int, tool_calls: list, results: list) -> tuple:
        # 维度 1：绝对硬上限
        if round_num >= self.max_rounds:
            return False, f"达到最大轮次 {self.max_rounds}"

        # 维度 2：冗余检测
        fp = self._fingerprint(tool_calls)
        if tool_calls and fp and fp in self.tool_call_fingerprints:
            return False, "检测到重复工具调用序列"
        if fp:
            self.tool_call_fingerprints.append(fp)

        # 维度 3：连续失败检测
        all_failed = all(not r.get("success", True) for r in results) if results else False
        if all_failed:
            self.successive_failures += 1
            if self.successive_failures >= 3:
                return False, "连续 3 轮工具调用全部失败"
        else:
            self.successive_failures = 0

        # 维度 4：停滞检测
        gain = self._info_gain(results)
        self.info_gain_history.append(gain)
        if len(self.info_gain_history) >= self.staleness_window:
            recent = self.info_gain_history[-self.staleness_window:]
            if all(g == 0 for g in recent):
                return False, f"连续 {self.staleness_window} 轮无新信息"

        # 维度 5：数据充分
        total_rows = sum(r.get("row_count", 0) for r in results)
        if total_rows > 200 and len(self.tool_call_fingerprints) >= 2:
            return False, f"已获取 {total_rows} 行数据，信息充分"

        return True, ""


# ══════════════════════════════════════════════════════
# Self-Healing Tool Executor — 失败自愈矩阵
# ══════════════════════════════════════════════════════

class SelfHealingToolExecutor:
    """带自愈能力的工具执行器 —— 策略矩阵驱动"""

    HEALING_PATTERNS = [
        (r"Table .* doesn't exist", "_fix_table_not_found", 1),
        (r"Unknown column", "_fix_column_not_found", 1),
        (r"syntax error", "_fix_sql_syntax", 1),
        (r"connect timeout|connection refused", "_retry_with_backoff", 2),
        (r"permission denied|access denied", None, 0),
    ]

    def __init__(self, tool_dispatch: dict, get_metadata_func):
        self._dispatch = tool_dispatch
        self._get_metadata = get_metadata_func

    def execute(self, func_name: str, args: dict, session_id: str) -> dict:
        """主入口：执行工具，失败时自愈重试"""
        handler = self._dispatch.get(func_name)
        if not handler:
            return {"success": False, "error": f"未知工具: {func_name}"}

        result = self._raw_call(handler, args)

        if result.get("success"):
            return result

        error_msg = result.get("error", "")

        for pattern, fix_method, max_retries in self.HEALING_PATTERNS:
            if not re.search(pattern, error_msg, re.IGNORECASE):
                continue
            if fix_method is None:
                return result

            for attempt in range(max_retries):
                fixed_args = getattr(self, fix_method)(args, error_msg, session_id)
                if fixed_args is None:
                    break
                logger.info(f"[Healing] {func_name} 自动修复重试 {attempt + 1}/{max_retries}")
                result = self._raw_call(handler, fixed_args)
                if result.get("success"):
                    result["_auto_fixed"] = True
                    result["_fix_method"] = fix_method
                    return result
            break

        return result

    def _raw_call(self, handler, args: dict) -> dict:
        try:
            return handler(**args)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fix_table_not_found(self, args: dict, error: str, session_id: str) -> Optional[dict]:
        match = re.search(r"Table '.*?\.(\w+)' doesn't exist", error)
        if not match:
            return None
        wrong_table = match.group(1)

        metadata = self._get_metadata(args.get("database", ""))
        all_tables = [t.get("table_name", "") for t in metadata.get("tables", [])]
        if not all_tables:
            return None

        matches = difflib.get_close_matches(wrong_table.lower(), [t.lower() for t in all_tables], n=1, cutoff=0.5)
        if matches:
            corrected = all_tables[[t.lower() for t in all_tables].index(matches[0])]
            new_args = args.copy()
            new_args["sql"] = re.sub(r'\b' + wrong_table + r'\b', corrected, args.get("sql", ""), flags=re.IGNORECASE)
            logger.info(f"[Healing] 表名修正: {wrong_table} → {corrected}")
            return new_args
        return None

    def _fix_sql_syntax(self, args: dict, error: str, session_id: str) -> Optional[dict]:
        sql = args.get("sql", "")
        if not sql:
            return None
        formatter = self._dispatch.get("format_sql")
        if not formatter:
            return None
        formatted = formatter(sql)
        if formatted.get("success") and formatted.get("formatted_sql"):
            new_args = args.copy()
            new_args["sql"] = formatted["formatted_sql"]
            return new_args
        return None

    def _retry_with_backoff(self, args: dict, error: str, session_id: str) -> Optional[dict]:
        time.sleep(1)
        return args

    def _fix_column_not_found(self, args: dict, error: str, session_id: str) -> Optional[dict]:
        """基于 Levenshtein 编辑距离 + 元数据约束的智能列名修正"""
        try:
            from Levenshtein import ratio as levenshtein_ratio
        except ImportError:
            logger.warning("[Healing] python-Levenshtein 未安装，使用 difflib 回退")
            levenshtein_ratio = lambda a, b: difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

        match = re.search(r"Unknown column '(.+?)'", error)
        if not match:
            return None
        wrong_col = match.group(1)

        metadata = self._get_metadata(args.get("database", ""))
        all_columns = []
        for table in metadata.get("tables", []):
            for col in table.get("columns", []):
                all_columns.append({
                    "name": col.get("name", col) if isinstance(col, dict) else str(col),
                    "table": table.get("table_name", ""),
                    "type": col.get("type", "") if isinstance(col, dict) else "",
                })

        if not all_columns:
            logger.warning("[Healing] 无元数据可用，无法修正列名")
            return None

        # Step 1: Levenshtein 编辑距离排序
        scored = [(levenshtein_ratio(wrong_col.lower(), c["name"].lower()), c)
                  for c in all_columns]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Step 2: 约束校验 — 候选列名必须在 SQL 涉及的表范围内
        sql_tables = re.findall(r'FROM\s+`?(\w+)`?', args.get("sql", ""), re.IGNORECASE)
        if not sql_tables:
            # 也匹配 JOIN 之后的表
            sql_tables = re.findall(r'JOIN\s+`?(\w+)`?', args.get("sql", ""), re.IGNORECASE)
        if not sql_tables:
            sql_tables = [args.get("database", "")]

        valid_candidates = [(s, c) for s, c in scored
                            if c["table"].lower() in [t.lower() for t in sql_tables]]

        if valid_candidates:
            best_score, best_col = valid_candidates[0]
            if best_score > 0.4:
                corrected_sql = re.sub(
                    r'\b' + re.escape(wrong_col) + r'\b',
                    best_col["name"],
                    args.get("sql", ""),
                    flags=re.IGNORECASE,
                )
                logger.info(f"[Healing] 列名修正 (编辑距离={best_score:.2f}): "
                            f"{wrong_col} → {best_col['name']} (表 {best_col['table']}, 类型 {best_col['type']})")
                return {**args, "sql": corrected_sql}

        logger.warning(f"[Healing] 未找到合适的列名修正候选 for '{wrong_col}' (最高分: {scored[0][0]:.2f})")
        return None


# ══════════════════════════════════════════════════════
# Tool Result Cache — 30 秒 TTL
# ══════════════════════════════════════════════════════

class ToolResultCache:
    """工具调用结果缓存 —— 同一会话内避免重复查询，session 隔离"""

    def __init__(self, ttl_seconds: int = 30):
        self._cache: dict = {}
        self.ttl = ttl_seconds

    def _make_key(self, func_name: str, args: dict, session_id: str = "") -> Optional[str]:
        if func_name not in ("get_table_metadata", "execute_readonly_sql"):
            return None
        key_args = {k: v for k, v in sorted(args.items()) if k not in ("limit",)}
        payload = json.dumps(key_args, sort_keys=True)
        return f"{session_id}:{func_name}:{hash(payload)}"

    def get(self, func_name: str, args: dict, session_id: str = "") -> Optional[dict]:
        key = self._make_key(func_name, args, session_id)
        if key is None:
            return None
        if key in self._cache:
            ts, result = self._cache[key]
            if time.time() - ts < self.ttl:
                logger.debug(f"[Cache] 命中 (session={session_id[:8]}): {func_name}")
                return {**result, "_cached": True}
            del self._cache[key]
        return None

    def set(self, func_name: str, args: dict, result: dict, session_id: str = ""):
        key = self._make_key(func_name, args, session_id)
        if key and result.get("success"):
            self._cache[key] = (time.time(), result)


# ══════════════════════════════════════════════════════
# Result Completeness Checker — Reflection Step
# ══════════════════════════════════════════════════════

class ResultCompletenessChecker:
    """反思步骤：对比 work_state 中的 plan 与实际 explored_tables"""

    def check(self, working_state: 'AgentWorkingState') -> dict:
        plan_targets = set()
        for step in working_state.plan:
            for word in re.findall(r'\w+', step.get("goal", "")):
                if word.isalpha() and len(word) > 2:
                    plan_targets.add(word.lower())

        explored = set(t.lower() for t in working_state.explored_tables)

        if not plan_targets:
            return {"complete": len(explored) > 0, "missing": [], "should_continue": len(explored) == 0}

        missing = [t for t in plan_targets if t not in explored]
        return {
            "complete": len(missing) == 0,
            "missing_tables": missing,
            "should_continue": len(missing) > 0 and working_state.tool_call_count < 5,
            "suggestion": f"还需要查询: {', '.join(missing[:3])}" if missing else "",
        }


# ══════════════════════════════════════════════════════
# Agent Working State — 工作记忆 (Phase 2)
# ══════════════════════════════════════════════════════

@dataclass
class AgentWorkingState:
    """Agent 工作记忆 —— 代码层维护，LLM 只读取"""

    plan: List[Dict] = field(default_factory=list)
    current_step: int = 0
    current_database: Optional[str] = None
    explored_tables: List[str] = field(default_factory=list)
    explored_columns: Dict[str, List[str]] = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)
    last_query_sql: Optional[str] = None
    last_query_row_count: int = 0
    tool_call_count: int = 0
    last_tool_errors: List[str] = field(default_factory=list)

    def record_tool_result(self, func_name: str, result: dict):
        self.tool_call_count += 1
        if not result.get("success"):
            self.last_tool_errors.append(result.get("error", "")[:200])
            return

        tables = result.get("tables", [])
        for t in tables:
            tname = t.get("table_name", "") if isinstance(t, dict) else str(t)
            if tname and tname not in self.explored_tables:
                self.explored_tables.append(tname)

        columns = result.get("columns", [])
        if columns:
            last_table = self.explored_tables[-1] if self.explored_tables else "unknown"
            for c in columns:
                cname = c if isinstance(c, str) else c.get("name", "")
                if cname:
                    self.explored_columns.setdefault(last_table, []).append(cname)

        if func_name == "execute_readonly_sql" and result.get("sql"):
            self.last_query_sql = result["sql"]
            self.last_query_row_count = result.get("row_count", 0)

        if self.last_query_row_count > 0:
            self.findings.append(f"查询返回 {self.last_query_row_count} 行数据")

    def to_prompt_context(self) -> str:
        lines = ["## 📋 当前任务状态（工作记忆）"]
        if self.plan:
            lines.append(f"执行计划 ({len(self.plan)} 步，当前第 {self.current_step + 1} 步):")
            for i, step in enumerate(self.plan):
                marker = "← 当前" if i == self.current_step else ("✓" if step.get("done") else "○")
                lines.append(f"  {marker} 步骤{i + 1}: {step.get('goal', '')}")
        if self.current_database:
            lines.append(f"当前数据库: {self.current_database}")
        if self.explored_tables:
            lines.append(f"已探索表: {', '.join(self.explored_tables[:10])}")
        if self.findings:
            lines.append(f"关键发现: {'; '.join(self.findings[-5:])}")
        if self.last_tool_errors:
            lines.append(f"最近错误: {self.last_tool_errors[-1][:100]}")
        lines.append(f"已调用工具 {self.tool_call_count} 次")
        return "\n".join(lines)

    def detect_plan_from_user_message(self, message: str):
        if re.search(r'(?:找出|查询|查看).+的.+然后|再|并', message):
            self.plan = [
                {"goal": "获取表元数据", "done": False},
                {"goal": "执行数据查询", "done": False},
                {"goal": "汇总分析结果", "done": False},
            ]
            self.current_step = 0


# ══════════════════════════════════════════════════════
# Optimization Trigger — SQL 智能优化检测
# ══════════════════════════════════════════════════════

class OptimizationTrigger:
    """SQL 优化触发器 —— 第三章(明星功能)的核心组件"""

    THRESHOLDS = {
        "min_rows_for_optimization": 5000,
        "problematic_types": ("ALL", "index"),
    }

    def should_trigger(self, explain_result: dict, working_state: AgentWorkingState,
                       token_budget: TokenBudget) -> bool:
        if explain_result.get("type") not in self.THRESHOLDS["problematic_types"]:
            return False
        if explain_result.get("rows", 0) < self.THRESHOLDS["min_rows_for_optimization"]:
            return False
        if token_budget.total_consumed > token_budget.max_total * 0.7:
            return False
        if any("优化建议" in f for f in working_state.findings):
            return False
        return True


