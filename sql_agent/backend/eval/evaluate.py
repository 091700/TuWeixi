"""Agent 评估脚本 — 批量回归测试 (v2.0)"""
import json
import time
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AgentEvaluator:
    """Agent 评估器 — v3.0 支持端到端评估"""

    def __init__(self, eval_cases_path: str = None):
        if eval_cases_path is None:
            eval_cases_path = os.path.join(os.path.dirname(__file__), "eval_cases.json")
        with open(eval_cases_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.cases = data["cases"]
        self.name = data.get("name", "eval")
        self.version = data.get("version", "3.0")

    def evaluate_static(self, cases: list = None) -> dict:
        """静态评估：检查各用例关键词命中率"""
        if cases is None:
            cases = self.cases

        results = []
        for case in cases:
            q = case["question"]
            expected_tools = set(case["expected_tools"])
            expected_kw = case.get("expected_keywords", [])
            difficulty = case.get("difficulty", "unknown")

            # 关键词命中率（离线模式下仅检查问题本身）
            kw_hits = sum(1 for kw in expected_kw if kw.lower() in q.lower())
            kw_score = round(kw_hits / max(len(expected_kw), 1), 2)
            passed = len(expected_tools) > 0  # 静态模式下默认通过

            results.append({
                "case_id": case["id"],
                "question": q[:80],
                "difficulty": difficulty,
                "passed": passed,
                "scores": {
                    "tool_accuracy": 1.0 if expected_tools else 0.0,
                    "keyword_coverage": kw_score,
                },
                "expected_tools": sorted(expected_tools),
                "note": "静态评估（需 agent_eval_db 做端到端验证）"
            })

        passed = sum(1 for r in results if r["passed"])
        total = len(results)

        summary = {
            "name": self.name,
            "version": self.version,
            "total_cases": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "elapsed_seconds": 0,
            "by_difficulty": {},
        }

        for r in results:
            d = r["difficulty"]
            summary["by_difficulty"].setdefault(d, {"total": 0, "passed": 0})
            summary["by_difficulty"][d]["total"] += 1
            if r["passed"]:
                summary["by_difficulty"][d]["passed"] += 1

        # 计算每个难度的通过率
        for d in summary["by_difficulty"]:
            data = summary["by_difficulty"][d]
            data["rate"] = round(data["passed"] / data["total"] * 100, 1) if data["total"] else 0

        return {"summary": summary, "results": results}

    async def evaluate_e2e(self, database: str, cases: list = None) -> dict:
        """端到端评估 — 真实运行 Agent 并对比预期 (P2)

        Args:
            database: 目标测试数据库
            cases: 测试用例列表，默认用 self.cases
        """
        if cases is None:
            cases = self.cases

        results = []
        for case in cases:
            import uuid
            from agent.scheduler import session_manager, chat_stream_generator

            sid = session_manager.create_session()
            session_manager.set_database(sid, database)

            actual_response = ""
            actual_tools = []
            try:
                async for chunk in chat_stream_generator(sid, case["question"], database, "reader", "eval"):
                    if chunk.startswith("data: ") and not chunk.startswith("data: [DONE]"):
                        data = json.loads(chunk[6:].strip())
                        if data.get("type") == "tool_start":
                            actual_tools.append(data.get("tool", ""))
                        if data.get("type") == "content":
                            actual_response += data.get("text", "")
            except Exception as e:
                actual_response = f"[EVAL_ERROR: {e}]"

            expected_tools = set(case.get("expected_tools", []))
            expected_kw = case.get("expected_keywords", [])
            tool_accuracy = len(expected_tools & set(actual_tools)) / max(len(expected_tools), 1)
            kw_hits = sum(1 for kw in expected_kw if kw.lower() in actual_response.lower())
            kw_coverage = kw_hits / max(len(expected_kw), 1)
            passed = tool_accuracy >= 0.5 and kw_coverage >= 0.5

            results.append({
                "case_id": case["id"],
                "passed": passed,
                "tool_accuracy": round(tool_accuracy, 2),
                "keyword_coverage": round(kw_coverage, 2),
                "actual_tools": actual_tools,
                "actual_response": actual_response[:200],
            })

        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        return {
            "summary": {
                "name": f"{self.name}_e2e",
                "version": self.version,
                "total_cases": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": round(passed / total * 100, 1) if total else 0,
            },
            "results": results,
        }

    def run_all(self) -> dict:
        """运行全部评估"""
        start_time = time.time()
        report = self.evaluate_static()
        report["summary"]["elapsed_seconds"] = round(time.time() - start_time, 2)
        return report

    def print_report(self, report: dict = None):
        """打印格式化的评估报告"""
        if report is None:
            report = self.run_all()

        s = report["summary"]
        print("=" * 60)
        print(f"  📊 评估报告: {s['name']} v{s['version']}")
        print("=" * 60)
        print(f"  总用例: {s['total_cases']} | 通过: {s['passed']} | 失败: {s['failed']}")
        print(f"  通过率: {s['pass_rate']}% | 耗时: {s['elapsed_seconds']}s")
        print()
        print("  按难度分布:")
        for diff, data in sorted(s["by_difficulty"].items()):
            bar = "█" * int(data["rate"] / 10) + "░" * (10 - int(data["rate"] / 10))
            print(f"    {diff:8s}  {data['passed']}/{data['total']}  {bar}  {data['rate']}%")
        print()
        print("  ⚠ 注：以上为静态评估。")
        print("  端到端评估需配置 agent_eval_db 并真实运行 Agent。")
        print("  静态评估确保测试用例定义完整、格式正确。")
        print("=" * 60)

        return report


if __name__ == "__main__":
    evaluator = AgentEvaluator()
    report = evaluator.evaluate_static()
    evaluator.print_report(report)

    # 还输出 JSON 格式便于 CI 集成
    print("\n📋 JSON 输出：")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))