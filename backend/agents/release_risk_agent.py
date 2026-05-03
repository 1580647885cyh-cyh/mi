from __future__ import annotations

from typing import Any, Dict, List

from backend.agents.base import BaseAgent
from backend.schemas import AgentResult, Finding


class ReleaseRiskAgent(BaseAgent):
    name = "release_risk_agent"

    def run(self, requirement_result: AgentResult, code_review_result: AgentResult) -> AgentResult:
        text = " ".join(str(item) for item in requirement_result.items).lower()
        findings: List[Finding] = []
        checklist: List[Dict[str, Any]] = []

        def add_risk(title: str, detail: str, severity: str, recommendation: str) -> None:
            findings.append(Finding(title=title, detail=detail, severity=severity, recommendation=recommendation))

        if "权限" in text or "用户" in text or "客服" in text or "工单" in text:
            add_risk("权限和数据隔离风险", "涉及用户、工单或团队角色时，Agent 可能看到不应访问的数据。", "high", "按角色过滤知识库与工单数据，输出中脱敏用户隐私。")
        if "自动" in text or "同步" in text or "ci" in text or "cd" in text:
            add_risk("自动化误操作风险", "自动创建任务、同步状态或触发流水线时，错误建议可能放大影响。", "high", "高风险操作采用 human-in-the-loop，默认只生成草稿而非直接执行。")
        if "知识库" in text or "rag" in text:
            add_risk("知识库过期风险", "RAG 命中旧规范可能导致建议不准确。", "medium", "为知识库增加更新时间、版本号和引用来源，在输出中展示证据。")
        if code_review_result.metrics.get("critical_or_high", 0):
            add_risk("代码高危问题未关闭", "代码扫描发现 critical/high 级别问题。", "critical", "阻断上线，要求修复后重新扫描并留存结果。")

        standard_checks = [
            ("灰度发布", "先对 5%-10% 用户或单个团队开放，观察 Agent 建议质量。"),
            ("回滚方案", "保留关闭 Agent 建议、恢复人工流程的开关。"),
            ("可观测性", "记录每次运行的输入摘要、Agent 耗时、命中规则和用户反馈。"),
            ("安全合规", "敏感字段脱敏；禁止输出密钥、身份证、手机号等隐私信息。"),
            ("质量评估", "抽样检查建议准确率、误报率和人工采纳率。"),
        ]
        for name, desc in standard_checks:
            checklist.append({"item": name, "description": desc, "required": True})
        risk_score = min(100, 20 + len(findings) * 15 + code_review_result.metrics.get("critical_or_high", 0) * 20)
        summary = f"生成 {len(checklist)} 项上线检查，识别 {len(findings)} 个风险，综合风险分 {risk_score}/100。"
        return AgentResult(agent=self.name, summary=summary, items=checklist, findings=findings, metrics={"risk_score": risk_score, "risk_count": len(findings), "checklist_count": len(checklist)})
