from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from backend.workflow import AgentWorkflow


def load_repo_snapshot(repo_dir: str | None) -> Dict[str, str]:
    if not repo_dir:
        return {}
    root = Path(repo_dir)
    snapshot: Dict[str, str] = {}
    allowed = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".sql"}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in allowed and ".venv" not in path.parts and "node_modules" not in path.parts:
            try:
                snapshot[str(path.relative_to(root))] = path.read_text(encoding="utf-8")[:20000]
            except UnicodeDecodeError:
                continue
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AI Dev Agent Suite from command line")
    parser.add_argument("--input", help="JSON payload file")
    parser.add_argument("--requirement", help="Requirement text")
    parser.add_argument("--repo-dir", help="Directory to scan as repository snapshot")
    parser.add_argument("--output", help="Output JSON path")
    args = parser.parse_args()
    if args.input:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        payload = {
            "project_name": "CLI Demo",
            "requirement": args.requirement or "构建一个研发提效多 Agent 系统，支持需求拆解、代码审查、测试生成和上线风险检查。",
        }
    if args.repo_dir:
        payload["repository_snapshot"] = load_repo_snapshot(args.repo_dir)
    result = AgentWorkflow().run(payload)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Saved result to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
