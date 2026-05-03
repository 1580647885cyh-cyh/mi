from __future__ import annotations

import re
from typing import Dict, List

from backend.agents.base import BaseAgent
from backend.schemas import AgentResult, Finding


class CodeReviewAgent(BaseAgent):
    name = "code_review_agent"

    SECRET_PATTERNS = [
        re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{8,}['\"]"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ]

    def run(self, repository_snapshot: Dict[str, str]) -> AgentResult:
        findings: List[Finding] = []
        file_count = len(repository_snapshot)
        total_lines = 0
        has_tests = any("test" in path.lower() for path in repository_snapshot)
        for path, content in repository_snapshot.items():
            lines = content.splitlines()
            total_lines += len(lines)
            findings.extend(self._scan_file(path, lines))
        if file_count and not has_tests:
            findings.append(Finding(
                title="缺少测试文件",
                detail="仓库快照中未发现 test/tests/spec 文件，建议补充核心 Agent 和 API 的单元测试。",
                severity="medium",
                recommendation="新增 tests/test_workflow.py，至少覆盖需求解析、代码扫描和风险评估。",
            ))
        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        findings.sort(key=lambda f: severity_rank.get(f.severity, 0), reverse=True)
        issue_count = len(findings)
        summary = f"扫描 {file_count} 个文件、{total_lines} 行代码，发现 {issue_count} 个潜在问题。"
        if issue_count == 0:
            summary = f"扫描 {file_count} 个文件、{total_lines} 行代码，未发现明显规则问题。"
        return AgentResult(
            agent=self.name,
            summary=summary,
            findings=findings,
            metrics={
                "file_count": file_count,
                "line_count": total_lines,
                "finding_count": issue_count,
                "critical_or_high": sum(1 for f in findings if f.severity in {"critical", "high"}),
            },
        )

    def _scan_file(self, path: str, lines: List[str]) -> List[Finding]:
        findings: List[Finding] = []
        lower_path = path.lower()
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if "TODO" in line or "FIXME" in line:
                findings.append(Finding("遗留 TODO/FIXME", stripped[:160], "low", path, i, "将 TODO 转成明确任务，或在上线前关闭。"))
            if re.search(r"\bprint\(", line) and lower_path.endswith(".py"):
                findings.append(Finding("生产代码中存在 print 调试语句", stripped[:160], "low", path, i, "替换为结构化日志，并设置合适日志级别。"))
            if re.search(r"except\s+Exception\s*:", line) or re.search(r"except\s*:", line):
                findings.append(Finding("异常捕获过宽", stripped[:160], "medium", path, i, "捕获具体异常类型，并记录上下文，避免吞掉真实错误。"))
            if re.search(r"SELECT .*\+|f['\"].*SELECT|execute\(.+%", line, re.I):
                findings.append(Finding("可能存在 SQL 拼接风险", stripped[:160], "high", path, i, "使用参数化查询或 ORM 绑定变量，避免注入风险。"))
            if any(p.search(line) for p in self.SECRET_PATTERNS):
                findings.append(Finding("疑似硬编码密钥", "检测到疑似 token/secret/password 字段。", "critical", path, i, "立即迁移到环境变量或密钥管理系统，并轮换已暴露密钥。"))
        if lower_path.endswith((".py", ".ts", ".js")) and len(lines) > 350:
            findings.append(Finding("单文件过长", f"文件共有 {len(lines)} 行，后续维护成本较高。", "medium", path, None, "按职责拆分模块，保持 Agent、路由、存储和工具函数边界清晰。"))
        return findings
