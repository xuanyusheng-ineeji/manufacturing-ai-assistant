import json
from pathlib import Path

import numpy as np
from sentence_transformers import (
    SentenceTransformer,
)

from app.tools.document_loader import (
    load_documents,
)
from app.tools.text_splitter import (
    split_documents,
)


BASE_DIR = Path(__file__).resolve().parent.parent
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


def main() -> None:
    KNOWLEDGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents = load_documents()
    chunks = split_documents(documents)

    if not chunks:
        raise ValueError(
            "No document chunks were generated."
        )

    print(
        f"Loaded {len(documents)} document sections."
    )

    print(
        f"Generated {len(chunks)} chunks."
    )

    print(
        f"Loading embedding model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embeddings_array = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    np.save(
        EMBEDDING_PATH,
        embeddings_array,
    )

    metadata = [
        {
            "chunk_id": chunk.chunk_id,
            "source": chunk.source,
            "page": chunk.page,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
        }
        for chunk in chunks
    ]

    METADATA_PATH.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Embeddings saved: {EMBEDDING_PATH}"
    )

    print(
        f"Metadata saved: {METADATA_PATH}"
    )

    print(
        "Knowledge index build completed."
    )


if __name__ == "__main__":
    main()