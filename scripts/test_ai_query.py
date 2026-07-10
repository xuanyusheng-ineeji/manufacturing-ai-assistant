from app.services.ai_query_service import ask_database
from app.tools.sql_validator import SQLValidationError


def main() -> None:
    print("Manufacturing AI Database Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() in {
            "exit",
            "quit",
        }:
            break

        try:
            sql, result_df = ask_database(question)

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

        except SQLValidationError as exc:
            print(f"\nSQL rejected: {exc}")

        except Exception as exc:
            print(f"\nError: {exc}")

        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()