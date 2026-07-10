from app.services.ai_query_service import (
    analyze_database_question,
)
from app.tools.sql_validator import (
    SQLValidationError,
)


def main() -> None:
    print("Manufacturing AI Analysis Engine")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() in {
            "exit",
            "quit",
        }:
            break

        if not question:
            print("Please enter a question.\n")
            continue

        try:
            sql, result_df, analysis = (
                analyze_database_question(
                    question
                )
            )

            print("\nGenerated SQL:")
            print(sql)

            print("\nQuery result:")

            if result_df.empty:
                print("No data found.")
            else:
                print(
                    result_df.head(20).to_string(
                        index=False
                    )
                )

            print("\nAI analysis:")
            print(analysis)

        except SQLValidationError as exc:
            print(
                f"\nSQL safety validation failed: {exc}"
            )

        except Exception as exc:
            print(
                f"\nUnable to analyze the question: {exc}"
            )

        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()