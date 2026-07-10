import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sentence_transformers import (
    SentenceTransformer,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"

EMBEDDING_PATH = (
    KNOWLEDGE_DIR / "embeddings.npy"
)

METADATA_PATH = (
    KNOWLEDGE_DIR / "chunks.json"
)

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


@dataclass
class RetrievalResult:
    chunk_id: str
    source: str
    text: str
    page: int | None
    score: float


_model: SentenceTransformer | None = None
_embeddings: np.ndarray | None = None
_chunks: list[dict] | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(
            MODEL_NAME
        )

    return _model


def load_knowledge_index() -> tuple[
    np.ndarray,
    list[dict],
]:
    global _embeddings
    global _chunks

    if (
        not EMBEDDING_PATH.exists()
        or not METADATA_PATH.exists()
    ):
        raise FileNotFoundError(
            "Knowledge index does not exist. "
            "Run scripts/build_knowledge_index.py first."
        )

    if _embeddings is None:
        _embeddings = np.load(
            EMBEDDING_PATH
        )

    if _chunks is None:
        _chunks = json.loads(
            METADATA_PATH.read_text(
                encoding="utf-8",
            )
        )

    if len(_embeddings) != len(_chunks):
        raise ValueError(
            "Embedding and metadata counts "
            "do not match."
        )

    return _embeddings, _chunks


def retrieve_documents(
    question: str,
    top_k: int = 4,
    minimum_score: float = 0.25,
) -> list[RetrievalResult]:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError(
            "Question cannot be empty."
        )

    embeddings, chunks = load_knowledge_index()
    model = get_embedding_model()

    query_embedding = model.encode(
        [cleaned_question],
        normalize_embeddings=True,
    )[0]

    scores = embeddings @ query_embedding

    ranked_indices = np.argsort(
        scores
    )[::-1]

    results: list[RetrievalResult] = []

    for index in ranked_indices[:top_k]:
        score = float(scores[index])

        if score < minimum_score:
            continue

        chunk = chunks[index]

        results.append(
            RetrievalResult(
                chunk_id=chunk["chunk_id"],
                source=chunk["source"],
                page=chunk.get("page"),
                text=chunk["text"],
                score=score,
            )
        )

    return results