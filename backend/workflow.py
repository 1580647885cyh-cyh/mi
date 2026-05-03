from __future__ import annotations

from typing import Any, Dict

from backend.agents.code_review_agent import CodeReviewAgent
from backend.agents.rag_agent import RAGAgent
from backend.agents.release_risk_agent import ReleaseRiskAgent
from backend.agents.requirement_agent import RequirementAgent
from backend.agents.task_agent import TaskPlannerAgent
from backend.agents.test_agent import TestGeneratorAgent
from backend.schemas import WorkflowInput, WorkflowOutput, new_run_id, utc_now_iso
from backend.storage import JsonRunStorage


class AgentWorkflow:
    def __init__(self, storage: JsonRunStorage | None = None) -> None:
        self.requirement_agent = RequirementAgent()
        self.task_agent = TaskPlannerAgent()
        self.code_review_agent = CodeReviewAgent()
        self.test_agent = TestGeneratorAgent()
        self.rag_agent = RAGAgent()
        self.risk_agent = ReleaseRiskAgent()
        self.storage = storage or JsonRunStorage()

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        workflow_input = WorkflowInput.from_payload(payload)
        if not workflow_input.requirement:
            raise ValueError("requirement 不能为空")
        requirement_result = self.requirement_agent.run(workflow_input.requirement)
        task_result = self.task_agent.run(requirement_result)
        code_result = self.code_review_agent.run(workflow_input.repository_snapshot)
        test_result = self.test_agent.run(requirement_result, task_result)
        rag_result = self.rag_agent.run(workflow_input.requirement)
        risk_result = self.risk_agent.run(requirement_result, code_result)
        results = {
            requirement_result.agent: requirement_result.to_dict(),
            task_result.agent: task_result.to_dict(),
            code_result.agent: code_result.to_dict(),
            test_result.agent: test_result.to_dict(),
            rag_result.agent: rag_result.to_dict(),
            risk_result.agent: risk_result.to_dict(),
        }
        estimated_impact = self._estimate_impact(results, workflow_input.requirement)
        executive_summary = self._executive_summary(results, estimated_impact)
        output = WorkflowOutput(
            run_id=new_run_id(),
            project_name=workflow_input.project_name,
            created_at=utc_now_iso(),
            input_preview=workflow_input.requirement[:240],
            results=results,
            executive_summary=executive_summary,
            estimated_impact=estimated_impact,
        )
        data = output.to_dict()
        self.storage.save(data)
        return data

    def _estimate_impact(self, results: Dict[str, Dict[str, Any]], requirement: str) -> Dict[str, Any]:
        task_count = results["task_planner_agent"]["metrics"].get("task_count", 0)
        test_count = results["test_generator_agent"]["metrics"].get("test_case_count", 0)
        finding_count = results["code_review_agent"]["metrics"].get("finding_count", 0)
        minutes_saved = task_count * 8 + test_count * 10 + finding_count * 20
        manual_minutes = max(60, minutes_saved + 80)
        efficiency_gain = round(minutes_saved / manual_minutes * 100, 1)
        estimated_tokens = sum(r.get("metrics", {}).get("estimated_input_tokens", 0) for r in results.values()) + len(requirement) // 2
        return {
            "estimated_minutes_saved_per_run": minutes_saved,
            "manual_baseline_minutes": manual_minutes,
            "efficiency_gain_percent": efficiency_gain,
            "estimated_tokens_processed": estimated_tokens,
            "suggested_success_metrics": [
                "需求拆解耗时下降 30%-50%",
                "Review 和测试准备时间下降 35%-60%",
                "高风险问题上线前发现率提升 20%+",
                "团队知识检索时间下降 40%+",
            ],
        }

    def _executive_summary(self, results: Dict[str, Dict[str, Any]], impact: Dict[str, Any]) -> str:
        req = results["requirement_agent"]
        tasks = results["task_planner_agent"]["metrics"]
        code = results["code_review_agent"]["metrics"]
        risk = results["release_risk_agent"]["metrics"]
        return (
            f"本次多 Agent 工作流完成需求理解、任务拆解、代码审查、测试生成、知识库检索和上线风险评估。"
            f"系统识别 {req['metrics'].get('feature_count', 0)} 个核心功能点，拆解 {tasks.get('task_count', 0)} 个任务，"
            f"扫描 {code.get('file_count', 0)} 个代码文件并发现 {code.get('finding_count', 0)} 个潜在问题，"
            f"上线风险分为 {risk.get('risk_score', 0)}/100。"
            f"按规则估算，单次运行可节省约 {impact['estimated_minutes_saved_per_run']} 分钟，"
            f"效率提升约 {impact['efficiency_gain_percent']}%。"
        )
