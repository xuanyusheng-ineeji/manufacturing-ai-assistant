from app.services.knowledge_service import (
    answer_knowledge_question,
)


def main() -> None:
    print("Manufacturing Knowledge Assistant")
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

        try:
            result = answer_knowledge_question(
                question
            )

            print("\nAnswer:")
            print(result.answer)

            print("\nRetrieved sources:")

            if not result.sources:
                print("No source found.")

            for index, source in enumerate(
                result.sources,
                start=1,
            ):
                print(
                    f"{index}. {source.source} "
                    f"(score={source.score:.4f})"
                )

        except Exception as exc:
            print(f"\nError: {exc}")

        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()