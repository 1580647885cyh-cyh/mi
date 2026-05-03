from __future__ import annotations

from typing import Any, Dict, List

from backend.agents.base import BaseAgent
from backend.schemas import AgentResult


class TestGeneratorAgent(BaseAgent):
    name = "test_generator_agent"

    def run(self, requirement_result: AgentResult, task_result: AgentResult) -> AgentResult:
        features = []
        for item in requirement_result.items:
            if item.get("type") == "feature":
                features = list(item.get("values", []))
        test_cases: List[Dict[str, Any]] = []
        for idx, feature in enumerate(features[:6] or ["多 Agent 工作流"], start=1):
            test_cases.extend([
                {
                    "id": f"TC-{idx:02d}-HAPPY",
                    "type": "happy_path",
                    "title": f"正常输入时完成：{feature[:32]}",
                    "steps": ["准备包含明确目标和功能点的需求文本", "调用 /api/run", "检查对应 Agent 输出"],
                    "expected": "返回 200，results 中包含结构化 summary、items 或 findings。",
                },
                {
                    "id": f"TC-{idx:02d}-EDGE",
                    "type": "edge_case",
                    "title": f"边界输入覆盖：{feature[:32]}",
                    "steps": ["输入空白、超长文本、中文英文混合文本", "重复调用 workflow"],
                    "expected": "系统不崩溃，给出可解释的兜底结果和待澄清问题。",
                },
            ])
        test_cases.append({
            "id": "TC-PYTEST-SKELETON",
            "type": "automation",
            "title": "pytest 自动化测试骨架",
            "code": self._pytest_template(),
            "expected": "执行 python -m pytest tests 后通过核心工作流测试。",
        })
        summary = f"生成 {len(test_cases)} 个测试建议，覆盖正常路径、边界输入和自动化回归。"
        return AgentResult(agent=self.name, summary=summary, items=test_cases, metrics={"test_case_count": len(test_cases), "automation_ready": True})

    def _pytest_template(self) -> str:
        return (
            "from backend.workflow import AgentWorkflow\n\n"
            "def test_workflow_returns_structured_results():\n"
            "    workflow = AgentWorkflow()\n"
            "    result = workflow.run({\n"
            "        'project_name': 'demo',\n"
            "        'requirement': '做一个研发提效 Agent，支持需求拆解、代码审查和测试生成。',\n"
            "        'repository_snapshot': {'app.py': \"print('debug')\"},\n"
            "    })\n"
            "    assert result['run_id']\n"
            "    assert 'requirement_agent' in result['results']\n"
        )
