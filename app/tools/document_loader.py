from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"

SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt",
    ".pdf",
}


@dataclass
class Document:
    source: str
    text: str
    page: int | None = None


def load_text_file(
    file_path: Path,
) -> list[Document]:
    text = file_path.read_text(
        encoding="utf-8",
    )

    return [
        Document(
            source=file_path.name,
            text=text,
            page=None,
        )
    ]


def load_pdf_file(
    file_path: Path,
) -> list[Document]:
    reader = PdfReader(str(file_path))

    documents: list[Document] = []

    for page_index, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append(
            Document(
                source=file_path.name,
                text=text,
                page=page_index,
            )
        )

    return documents


def load_documents() -> list[Document]:
    if not DOCS_DIR.exists():
        raise FileNotFoundError(
            f"Document directory not found: {DOCS_DIR}"
        )

    documents: list[Document] = []

    for file_path in sorted(DOCS_DIR.iterdir()):
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            continue

        if extension in {
            ".md",
            ".txt",
        }:
            documents.extend(
                load_text_file(file_path)
            )

        elif extension == ".pdf":
            documents.extend(
                load_pdf_file(file_path)
            )

    if not documents:
        raise ValueError(
            "No supported documents were found "
            f"in {DOCS_DIR}"
        )

    return documents


if __name__ == "__main__":
    loaded_documents = load_documents()

    for document in loaded_documents:
        print("=" * 70)
        print("Source:", document.source)
        print("Page:", document.page)
        print("Characters:", len(document.text))
        print(document.text[:300])