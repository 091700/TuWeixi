"""工具依赖分析与并行调度模块 (P1 新增)

对单个 LLM 返回的多个工具调用，分析它们之间的依赖关系，
用 Kahn 算法进行拓扑排序，生成可并行执行的批次。

判断规则：
- execute_readonly_sql / explain_sql 依赖 get_table_metadata（需先知道表结构）
- 独立的 get_table_metadata 调用互不依赖，可以并行

面试话术：
"我实现了基于 Kahn 算法的工具调用并行调度——把 LLM 返回的多
个工具调用构建成 DAG 依赖图，拓扑排序分层后同层并行执行。
参考了编译原理中的指令级并行调度思想。"
"""

import logging
from collections import deque

logger = logging.getLogger("db_agent.tool_scheduler")


class ToolDependencyAnalyzer:
    """分析工具调用间的依赖关系，生成并行批次

    用途：在 chat_stream_generator 中替代原有的串行 for 循环，
    让多个互不依赖的工具调用可以并发执行（asyncio.gather）。
    """

    @staticmethod
    def analyze(tool_calls: list) -> list:
        """返回并行批次 [[batch1_indices], [batch2_indices], ...]

        Args:
            tool_calls: LLM 返回的 tool_calls 列表
                        [{"function": {"name": "...", "arguments": "..."}}, ...]

        Returns:
            批次索引列表，如 [[0, 1], [2]] 表示第 0、1 个工具可并行，第 2 个等待

        Algorithm:
            1. 构建依赖图 DAG
            2. Kahn 算法拓扑排序分层
            3. 循环节点追加为最后一层（处理环形依赖，理论上不应出现）
        """
        # 单工具调用，不需要并行
        if len(tool_calls) <= 1:
            return [[i for i in range(len(tool_calls))]] if tool_calls else []

        # ── Step 1: 提取工具调用信息 ──
        tc_data = []
        for idx, tc in enumerate(tool_calls):
            func_name = tc.get("function", {}).get("name", "")
            args = tc.get("function", {}).get("arguments", "")
            tc_data.append({"index": idx, "name": func_name, "args": args})

        # ── Step 2: 构建依赖图 ──
        # 依赖规则：SQL 查询和 EXPLAIN 依赖元数据
        deps = {i: set() for i in range(len(tc_data))}
        for i, tci in enumerate(tc_data):
            for j, tcj in enumerate(tc_data):
                if i == j:
                    continue
                if (tci["name"] in ("execute_readonly_sql", "explain_sql")
                        and tcj["name"] == "get_table_metadata"):
                    deps[i].add(j)

        # ── Step 3: Kahn 拓扑排序分层 ──
        in_degree = {i: len(deps[i]) for i in range(len(tc_data))}
        queue = deque([i for i, d in in_degree.items() if d == 0])
        batches = []

        while queue:
            batch_size = len(queue)
            batch = [queue.popleft() for _ in range(batch_size)]
            batches.append(batch)

            # 更新后继节点的入度
            for bid in batch:
                for other in range(len(tc_data)):
                    if bid in deps.get(other, set()):
                        in_degree[other] -= 1
                        if in_degree[other] == 0:
                            queue.append(other)

        # ── Step 4: 处理残留节点（环形依赖，理论上不应出现）──
        all_in_batches = {i for b in batches for i in b}
        remaining = set(range(len(tc_data))) - all_in_batches
        if remaining:
            batches.append(list(remaining))
            logger.warning(f"[Dependency] 检测到环形依赖节点: {remaining}")

        logger.debug(f"[Dependency] {len(tc_data)} 工具 → {len(batches)} 批次")
        return batches if batches else [[i for i in range(len(tc_data))]]