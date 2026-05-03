from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from backend.agents.base import BaseAgent
from backend.schemas import AgentResult


class RAGAgent(BaseAgent):
    name = "rag_knowledge_agent"

    def __init__(self, knowledge_dir: str | Path | None = None) -> None:
        self.knowledge_dir = Path(knowledge_dir or Path(__file__).resolve().parents[1] / "sample_data" / "knowledge")

    def run(self, query: str) -> AgentResult:
        docs = self._load_docs()
        scored: List[Tuple[int, Dict[str, str]]] = []
        for doc in docs:
            score = self.score_overlap(query, doc["content"] + " " + doc["title"])
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:3]
        references = [{"title": d["title"], "source": d["source"], "snippet": self._snippet(query, d["content"])} for _, d in top]
        if not references and docs:
            references = [{"title": docs[0]["title"], "source": docs[0]["source"], "snippet": docs[0]["content"][:180]}]
        items = [{"recommendation": f"参考《{ref['title']}》中的规范，将对应检查项纳入 Agent 输出。", "source": ref["source"], "evidence": ref["snippet"]} for ref in references]
        summary = f"检索本地知识库 {len(docs)} 篇文档，命中 {len(references)} 条可引用内容。"
        return AgentResult(agent=self.name, summary=summary, items=items, references=references, metrics={"doc_count": len(docs), "reference_count": len(references)})

    def _load_docs(self) -> List[Dict[str, str]]:
        docs: List[Dict[str, str]] = []
        for path in sorted(self.knowledge_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            title = path.stem.replace("_", " ")
            for line in content.splitlines():
                if line.startswith("#"):
                    title = line.strip("# ").strip() or title
                    break
            docs.append({"title": title, "source": str(path.relative_to(self.knowledge_dir.parent.parent)), "content": content})
        return docs

    def _snippet(self, query: str, content: str) -> str:
        query_words = self.keywords(query, 8)
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in lines:
            if any(word in line.lower() for word in query_words):
                return line[:220]
        return " ".join(lines[:2])[:220]
