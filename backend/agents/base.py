from __future__ import annotations

import re
from collections import Counter
from typing import List


class BaseAgent:
    name = "base_agent"

    def normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def split_sentences(self, text: str) -> List[str]:
        parts = re.split(r"(?<=[。！？.!?])\s+|[\n\r]+", text or "")
        return [p.strip(" -•\t") for p in parts if p.strip(" -•\t")]

    def keywords(self, text: str, top_k: int = 12) -> List[str]:
        text = (text or "").lower()
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]{2,}|[\u4e00-\u9fff]{2,}", text)
        stop = {
            "the", "and", "for", "with", "this", "that", "from", "into", "支持", "需要", "通过", "进行", "一个", "我们",
            "系统", "用户", "项目", "可以", "自动", "生成", "实现", "功能", "agent",
        }
        counts = Counter(t for t in tokens if t not in stop)
        return [w for w, _ in counts.most_common(top_k)]

    def score_overlap(self, query: str, doc: str) -> int:
        q = set(self.keywords(query, top_k=50))
        d = set(self.keywords(doc, top_k=100))
        return len(q & d)

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
        other = len(re.sub(r"[\u4e00-\u9fff\s]", "", text))
        return chinese + max(1, other // 4)
