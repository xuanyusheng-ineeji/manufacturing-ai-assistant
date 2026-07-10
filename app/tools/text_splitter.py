from dataclasses import dataclass

from app.tools.document_loader import Document


@dataclass
class DocumentChunk:
    chunk_id: str
    source: str
    text: str
    page: int | None
    chunk_index: int


def split_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[str]:
    cleaned_text = "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )

    if not cleaned_text:
        return []

    paragraphs = cleaned_text.split("\n")

    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = (
            f"{current_chunk}\n{paragraph}".strip()
        )

        if (
            len(candidate) <= chunk_size
            or not current_chunk
        ):
            current_chunk = candidate
            continue

        chunks.append(current_chunk)

        overlap_text = current_chunk[
            -chunk_overlap:
        ]

        current_chunk = (
            f"{overlap_text}\n{paragraph}".strip()
        )

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def split_documents(
    documents: list[Document],
) -> list[DocumentChunk]:
    document_chunks: list[DocumentChunk] = []

    for document_index, document in enumerate(
        documents
    ):
        text_chunks = split_text(
            document.text
        )

        for chunk_index, chunk_text in enumerate(
            text_chunks
        ):
            chunk_id = (
                f"doc_{document_index:04d}_"
                f"chunk_{chunk_index:04d}"
            )

            document_chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    source=document.source,
                    text=chunk_text,
                    page=document.page,
                    chunk_index=chunk_index,
                )
            )

    return document_chunks