from app.services.retrieval_service import (
    retrieve_documents,
)


def main() -> None:
    print("Manufacturing Knowledge Retrieval")
    print("Type 'exit' to quit.\n")

    while True:
        question = input(
            "Question: "
        ).strip()

        if question.lower() in {
            "exit",
            "quit",
        }:
            break

        results = retrieve_documents(
            question=question,
            top_k=4,
        )

        if not results:
            print(
                "\nNo relevant document found.\n"
            )
            continue

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print("\n" + "=" * 70)
            print(f"Rank: {rank}")
            print(f"Source: {result.source}")
            print(f"Page: {result.page}")
            print(f"Score: {result.score:.4f}")
            print("\nText:")
            print(result.text)


if __name__ == "__main__":
    main()