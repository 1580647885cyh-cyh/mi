from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class JsonRunStorage:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir or Path(__file__).resolve().parent / "data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, run: Dict[str, Any]) -> Path:
        path = self.data_dir / f"run_{run['run_id']}.json"
        path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def list_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        runs = []
        for path in sorted(self.data_dir.glob("run_*.json"), reverse=True):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                runs.append({
                    "run_id": data.get("run_id"),
                    "project_name": data.get("project_name"),
                    "created_at": data.get("created_at"),
                    "executive_summary": data.get("executive_summary"),
                })
            except Exception:
                continue
            if len(runs) >= limit:
                break
        return runs
