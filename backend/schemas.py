from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Finding:
    title: str
    detail: str
    severity: str = "medium"
    file: Optional[str] = None
    line: Optional[int] = None
    recommendation: Optional[str] = None


@dataclass
class AgentResult:
    agent: str
    summary: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    findings: List[Finding] = field(default_factory=list)
    references: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["findings"] = [asdict(f) for f in self.findings]
        return data


@dataclass
class WorkflowInput:
    requirement: str
    repository_snapshot: Dict[str, str] = field(default_factory=dict)
    project_name: str = "AI Dev Agent Demo"

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "WorkflowInput":
        return cls(
            requirement=str(payload.get("requirement", "")).strip(),
            repository_snapshot=dict(payload.get("repository_snapshot", {}) or {}),
            project_name=str(payload.get("project_name", "AI Dev Agent Demo")).strip() or "AI Dev Agent Demo",
        )


@dataclass
class WorkflowOutput:
    run_id: str
    project_name: str
    created_at: str
    input_preview: str
    results: Dict[str, Dict[str, Any]]
    executive_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def new_run_id() -> str:
    return uuid4().hex[:12]
