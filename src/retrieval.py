"""Dynamic KB and historical-ticket retrieval."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import settings
from src.data_loader import load_raw_tickets
from src.exceptions import RetrievalError


ERROR_CODE_RE = re.compile(
    r"\b(?:ERR|AUTH|SCHEMA|PIPELINE|RATE|SAML|SSO|AUDIENCE|"
    r"QUOTA|TOKEN|CIRCUIT|WEBHOOK|HTTP)[A-Z0-9_:-]{3,}\b"
)


@dataclass(frozen=True)
class KBChunk:
    chunk_id: str
    document_path: str
    section_title: str
    content: str
    product: str | None
    error_codes: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalResult:
    chunk: KBChunk
    score: float
    is_exact_error_match: bool


@dataclass(frozen=True)
class HistoricalTicketResult:
    ticket: dict[str, Any]
    similarity: float


def extract_error_codes(text: str) -> tuple[str, ...]:
    return tuple(sorted(set(ERROR_CODE_RE.findall(text.upper()))))


def _extract_product(first_heading: str) -> str | None:
    if not first_heading.startswith("# "):
        return None

    title = first_heading[2:].strip()
    if " — " in title:
        title = title.split(" — ", 1)[0].strip()
    return title or None


def _split_markdown(path: Path) -> list[KBChunk]:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    heading = next((line.strip() for line in lines if line.strip()), "")
    product = _extract_product(heading)
    relative = path.relative_to(settings.paths.kb_dir).as_posix()

    chunks: list[KBChunk] = []
    current_title = heading.lstrip("# ").strip() or "Document"
    current_lines: list[str] = []

    def flush() -> None:
        text = "\n".join(current_lines).strip()
        if not text:
            return

        chunks.append(
            KBChunk(
                chunk_id=f"{relative}::{len(chunks)}",
                document_path=relative,
                section_title=current_title,
                content=text,
                product=product,
                error_codes=extract_error_codes(text),
            )
        )
        current_lines.clear()

    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            flush()
            continue

        if stripped.startswith("## ") or stripped.startswith("### "):
            flush()
            current_title = stripped.lstrip("#").strip()

        current_lines.append(line)

    flush()
    return chunks


class KnowledgeBaseRetriever:
    def __init__(self, kb_dir: Path | None = None) -> None:
        self.kb_dir = kb_dir or settings.paths.kb_dir
        self.chunks: list[KBChunk] = []
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
        )
        self.matrix = None
        self.refresh()

    def refresh(self) -> None:
        files = sorted(self.kb_dir.glob("**/*.md"))
        if not files:
            raise RetrievalError(f"No Markdown KB files found under {self.kb_dir}")

        chunks: list[KBChunk] = []
        for path in files:
            try:
                chunks.extend(_split_markdown(path))
            except OSError as exc:
                raise RetrievalError(f"Unable to read KB document: {path}") from exc

        if not chunks:
            raise RetrievalError("Knowledge base has no usable content.")

        self.chunks = chunks
        self.matrix = self.vectorizer.fit_transform(
            [chunk.content for chunk in chunks]
        )

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        if not isinstance(query, str) or not query.strip():
            return []

        if self.matrix is None:
            raise RetrievalError("KB index is not initialized.")

        limit = top_k or settings.retrieval.top_k
        scores = cosine_similarity(
            self.vectorizer.transform([query]), self.matrix
        )[0]

        query_errors = set(extract_error_codes(query))
        results: list[RetrievalResult] = []

        for index, chunk in enumerate(self.chunks):
            exact = bool(query_errors.intersection(chunk.error_codes))
            score = float(scores[index])

            if exact:
                score = min(
                    1.0,
                    score + settings.retrieval.exact_error_boost,
                )

            results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=score,
                    is_exact_error_match=exact,
                )
            )

        results.sort(
            key=lambda result: (
                result.score,
                result.is_exact_error_match,
                result.chunk.document_path,
                result.chunk.section_title,
                result.chunk.chunk_id,
            ),
            reverse=True,
        )
        return results[:limit]


class HistoricalTicketRetriever:
    """Nearest-neighbour index over the supplied labeled support tickets."""

    def __init__(self) -> None:
        self.tickets = list(load_raw_tickets())
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
        )

        texts = [
            f"{ticket.get('subject', '')}\n{ticket.get('body', '')}".strip()
            for ticket in self.tickets
        ]
        self.matrix = self.vectorizer.fit_transform(texts) if texts else None

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[HistoricalTicketResult]:
        if not isinstance(query, str) or not query.strip() or self.matrix is None:
            return []

        limit = top_k or settings.retrieval.historical_ticket_neighbors
        scores = cosine_similarity(
            self.vectorizer.transform([query]), self.matrix
        )[0]

        ranked = sorted(
            range(len(self.tickets)),
            key=lambda idx: (
                float(scores[idx]),
                str(self.tickets[idx].get("ticket_id", "")),
            ),
            reverse=True,
        )

        return [
            HistoricalTicketResult(
                ticket=self.tickets[idx],
                similarity=round(float(scores[idx]), 6),
            )
            for idx in ranked[:limit]
        ]


kb_retriever = KnowledgeBaseRetriever()
historical_ticket_retriever = HistoricalTicketRetriever()
