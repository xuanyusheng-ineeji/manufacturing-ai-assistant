from app.services.unified_assistant_service import (
    ask_unified_assistant,
)


def main() -> None:
    print("Manufacturing AI Assistant")
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

        if not question:
            print(
                "Please enter a question.\n"
            )
            continue

        try:
            response = ask_unified_assistant(
                question
            )

            print("\nRoute:")
            print(
                response.route.intent,
                f"({response.route.confidence:.2f})",
            )

            print("\nAnswer:")
            print(response.answer)

            if response.sql:
                print("\nGenerated SQL:")
                print(response.sql)

            if (
                response.result_df is not None
                and not response.result_df.empty
            ):
                print("\nQuery result:")
                print(
                    response.result_df
                    .head(20)
                    .to_string(index=False)
                )

            if response.sources:
                print("\nSources:")

                for index, source in enumerate(
                    response.sources,
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