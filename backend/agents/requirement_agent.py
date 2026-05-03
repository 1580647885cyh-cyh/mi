from __future__ import annotations

import re
from typing import Dict, List

from backend.agents.base import BaseAgent
from backend.schemas import AgentResult


class RequirementAgent(BaseAgent):
    name = "requirement_agent"

    DOMAIN_HINTS = {
        "工单": "客服/工单自动化",
        "客服": "客服/工单自动化",
        "代码": "研发提效",
        "review": "研发提效",
        "测试": "质量工程",
        "数据": "数据分析",
        "指标": "数据分析",
        "知识库": "企业知识管理",
        "rag": "企业知识管理",
        "jira": "项目管理",
        "需求": "项目管理",
    }

    def run(self, requirement: str) -> AgentResult:
        sentences = self.split_sentences(requirement)
        keywords = self.keywords(requirement)
        domain = self._infer_domain(requirement)
        goals = self._extract_goals(sentences, keywords)
        features = self._extract_features(sentences, keywords)
        acceptance = self._extract_acceptance(requirement, features)
        ambiguities = self._detect_ambiguities(requirement)

        items: List[Dict[str, object]] = [
            {"type": "domain", "value": domain},
            {"type": "goal", "values": goals},
            {"type": "feature", "values": features},
            {"type": "acceptance_criteria", "values": acceptance},
            {"type": "open_questions", "values": ambiguities},
        ]
        first_goal = goals[0] if goals else "提升效率与质量"
        summary = f"识别为「{domain}」场景，核心目标是：{first_goal}。已抽取 {len(features)} 个功能点和 {len(acceptance)} 条验收标准。"
        return AgentResult(
            agent=self.name,
            summary=summary,
            items=items,
            metrics={
                "keyword_count": len(keywords),
                "feature_count": len(features),
                "acceptance_count": len(acceptance),
                "estimated_input_tokens": self.estimate_tokens(requirement),
            },
        )

    def _infer_domain(self, requirement: str) -> str:
        lower = requirement.lower()
        for key, value in self.DOMAIN_HINTS.items():
            if key.lower() in lower:
                return value
        return "通用研发提效"

    def _extract_goals(self, sentences: List[str], keywords: List[str]) -> List[str]:
        goal_markers = ["目标", "为了", "提升", "降低", "减少", "缩短", "解决", "痛点"]
        goals = [s for s in sentences if any(m in s for m in goal_markers)]
        if not goals and keywords:
            goals = [f"围绕 {', '.join(keywords[:4])} 提升流程自动化与交付质量"]
        return goals[:3]

    def _extract_features(self, sentences: List[str], keywords: List[str]) -> List[str]:
        features: List[str] = []
        markers = ["支持", "需要", "能够", "可以", "自动", "生成", "识别", "同步", "检索", "审查", "拆解"]
        for s in sentences:
            if any(m in s for m in markers):
                features.append(s)
        if not features:
            default_map = {
                "代码": "自动扫描代码变更并生成 Review 建议",
                "测试": "根据需求生成测试用例和边界场景",
                "知识库": "检索项目文档并给出引用来源",
                "工单": "自动识别工单意图并完成分流",
            }
            for k, v in default_map.items():
                if k in " ".join(keywords) or k in "".join(sentences):
                    features.append(v)
        if not features:
            features = ["需求理解与信息抽取", "任务自动拆解", "质量检查与风险提示", "结果结构化输出"]
        return features[:8]

    def _extract_acceptance(self, requirement: str, features: List[str]) -> List[str]:
        acceptance = []
        explicit = re.findall(r"(?:验收|成功标准|指标|SLA|目标值)[：:，,]?([^。\n]+)", requirement, flags=re.I)
        acceptance.extend([e.strip() for e in explicit if e.strip()])
        for f in features[:4]:
            acceptance.append(f"功能「{f[:28]}」具备可演示输入、输出和异常处理。")
        acceptance.append("所有 Agent 输出结构化 JSON，便于接入 CI/CD、工单或报表系统。")
        return acceptance[:6]

    def _detect_ambiguities(self, requirement: str) -> List[str]:
        questions = []
        if not re.search(r"(指标|提升|降低|减少|%|分钟|小时|天|token)", requirement, re.I):
            questions.append("缺少明确量化指标，建议补充节省时间、覆盖率、准确率或缺陷下降比例。")
        if not re.search(r"(用户|角色|团队|研发|测试|运营|客服|产品)", requirement, re.I):
            questions.append("缺少目标用户角色，建议说明使用者和主要流程入口。")
        if not re.search(r"(接入|同步|CI|CD|Jira|Git|飞书|Slack|企业微信|知识库)", requirement, re.I):
            questions.append("缺少系统集成方式，建议明确接入代码仓库、工单系统或知识库。")
        return questions or ["当前需求描述较完整，可进入原型设计。"]
