from __future__ import annotations

from typing import Any, Dict, List

from backend.agents.base import BaseAgent
from backend.schemas import AgentResult


class TaskPlannerAgent(BaseAgent):
    name = "task_planner_agent"

    def run(self, requirement_result: AgentResult) -> AgentResult:
        features = []
        for item in requirement_result.items:
            if item.get("type") == "feature":
                features = list(item.get("values", []))
        if not features:
            features = ["需求理解", "任务拆解", "代码审查", "测试生成", "上线风险检查"]
        tasks: List[Dict[str, Any]] = []
        for idx, feature in enumerate(features, start=1):
            tasks.extend(self._tasks_for_feature(idx, feature))
        tasks.append({
            "id": f"DEVOPS-{len(tasks)+1:03d}",
            "role": "DevOps",
            "title": "接入 CI/CD 并持久化 Agent 运行结果",
            "description": "提供 API、CLI 和 Web 入口，将运行结果保存为 JSON，便于后续报表统计。",
            "estimate_hours": 8,
            "priority": "P1",
            "acceptance": "提交一次 Demo 输入后，可在页面和本地数据文件中查看完整多 Agent 输出。",
        })
        total_hours = sum(int(t["estimate_hours"]) for t in tasks)
        summary = f"已生成 {len(tasks)} 个交付任务，预计 {total_hours} 小时，覆盖产品、后端、前端、测试和 DevOps。"
        return AgentResult(agent=self.name, summary=summary, items=tasks, metrics={"task_count": len(tasks), "estimated_hours": total_hours})

    def _tasks_for_feature(self, idx: int, feature: str) -> List[Dict[str, Any]]:
        base_id = f"F{idx:02d}"
        return [
            {
                "id": f"{base_id}-PM-001",
                "role": "PM/Tech Lead",
                "title": f"澄清并冻结功能范围：{feature[:30]}",
                "description": "明确输入、输出、异常场景、成功指标和上线边界。",
                "estimate_hours": 2,
                "priority": "P0" if idx <= 2 else "P1",
                "acceptance": "形成包含验收标准、样例输入和样例输出的任务说明。",
            },
            {
                "id": f"{base_id}-BE-001",
                "role": "Backend",
                "title": f"实现 Agent 能力：{feature[:30]}",
                "description": "封装为独立 Agent 类，输出结构化 JSON，并提供可单测的 run() 方法。",
                "estimate_hours": 6,
                "priority": "P0" if idx <= 2 else "P1",
                "acceptance": "Agent 在空输入、正常输入和异常输入下均返回可解析结果。",
            },
            {
                "id": f"{base_id}-QA-001",
                "role": "QA",
                "title": f"补充测试场景：{feature[:30]}",
                "description": "覆盖 happy path、边界条件、空输入、长文本和中文/英文混合输入。",
                "estimate_hours": 3,
                "priority": "P1",
                "acceptance": "核心测试通过，失败时能定位到具体 Agent。",
            },
        ]
