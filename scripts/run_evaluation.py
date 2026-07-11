import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.database.connection import execute_query
from app.services.intent_router_service import (
    route_question,
)
from app.services.query_decomposition_service import (
    decompose_hybrid_question,
)
from app.services.retrieval_service import (
    retrieve_documents,
)
from app.services.text_to_sql_service import (
    generate_sql,
)
from app.tools.sql_validator import (
    SQLValidationError,
    validate_sql,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "evaluation" / "datasets"
RESULT_DIR = BASE_DIR / "evaluation" / "results"


@dataclass
class EvaluationResult:
    category: str
    question: str
    passed: bool
    expected: str
    actual: str
    error: str | None = None


def load_json(filename: str) -> list[dict]:
    path = DATASET_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def evaluate_intent_router() -> list[EvaluationResult]:
    cases = load_json("intent_cases.json")
    results: list[EvaluationResult] = []

    for case in cases:
        question = case["question"]
        expected = case["expected_intent"]

        try:
            decision = route_question(question)
            actual = decision.intent

            results.append(
                EvaluationResult(
                    category="intent",
                    question=question,
                    passed=actual == expected,
                    expected=expected,
                    actual=actual,
                )
            )

        except Exception as exc:
            results.append(
                EvaluationResult(
                    category="intent",
                    question=question,
                    passed=False,
                    expected=expected,
                    actual="error",
                    error=str(exc),
                )
            )

    return results


def evaluate_sql_generation() -> list[EvaluationResult]:
    cases = load_json("sql_cases.json")
    results: list[EvaluationResult] = []

    for case in cases:
        question = case["question"]

        try:
            generated_sql = generate_sql(question)
            validated_sql = validate_sql(generated_sql)

            upper_sql = validated_sql.upper()

            required_terms_passed = all(
                term.upper() in upper_sql
                for term in case["required_terms"]
            )

            required_tables_passed = all(
                table.lower() in validated_sql.lower()
                for table in case["required_tables"]
            )

            forbidden_terms_passed = all(
                term.upper() not in upper_sql
                for term in case["forbidden_terms"]
            )

            result_df = execute_query(validated_sql)

            passed = (
                required_terms_passed
                and required_tables_passed
                and forbidden_terms_passed
                and result_df is not None
            )

            results.append(
                EvaluationResult(
                    category="sql",
                    question=question,
                    passed=passed,
                    expected=(
                        "Required tables and SQL terms, "
                        "safe and executable"
                    ),
                    actual=validated_sql,
                )
            )

        except Exception as exc:
            results.append(
                EvaluationResult(
                    category="sql",
                    question=question,
                    passed=False,
                    expected="Safe executable SELECT",
                    actual="error",
                    error=str(exc),
                )
            )

    return results


def evaluate_retrieval() -> list[EvaluationResult]:
    cases = load_json("rag_cases.json")
    results: list[EvaluationResult] = []

    for case in cases:
        question = case["question"]

        try:
            retrieved = retrieve_documents(
                question=question,
                top_k=4,
            )

            retrieved_sources = {
                item.source
                for item in retrieved
            }

            combined_text = " ".join(
                item.text.lower()
                for item in retrieved
            )

            source_passed = any(
                source in retrieved_sources
                for source in case["expected_sources"]
            )

            keyword_passed = any(
                keyword.lower() in combined_text
                for keyword in case["expected_keywords"]
            )

            passed = (
                source_passed
                and keyword_passed
            )

            results.append(
                EvaluationResult(
                    category="rag",
                    question=question,
                    passed=passed,
                    expected=(
                        f"Sources={case['expected_sources']}, "
                        f"keywords={case['expected_keywords']}"
                    ),
                    actual=", ".join(
                        sorted(retrieved_sources)
                    ),
                )
            )

        except Exception as exc:
            results.append(
                EvaluationResult(
                    category="rag",
                    question=question,
                    passed=False,
                    expected="Relevant document retrieval",
                    actual="error",
                    error=str(exc),
                )
            )

    return results


def evaluate_decomposition() -> list[EvaluationResult]:
    cases = load_json(
        "decomposition_cases.json"
    )

    results: list[EvaluationResult] = []

    for case in cases:
        question = case["question"]

        try:
            decomposition = (
                decompose_hybrid_question(
                    question
                )
            )

            database_question = (
                decomposition.database_question
            )

            knowledge_question = (
                decomposition.knowledge_question
            )

            database_passed = all(
                keyword.lower()
                in database_question.lower()
                for keyword
                in case["database_keywords"]
            )

            knowledge_passed = all(
                keyword.lower()
                in knowledge_question.lower()
                for keyword
                in case["knowledge_keywords"]
            )

            passed = (
                database_passed
                and knowledge_passed
                and database_question
                != knowledge_question
            )

            results.append(
                EvaluationResult(
                    category="decomposition",
                    question=question,
                    passed=passed,
                    expected=(
                        "Independent database and "
                        "knowledge questions"
                    ),
                    actual=(
                        f"DB: {database_question}\n"
                        f"Knowledge: {knowledge_question}"
                    ),
                )
            )

        except Exception as exc:
            results.append(
                EvaluationResult(
                    category="decomposition",
                    question=question,
                    passed=False,
                    expected="Valid decomposition",
                    actual="error",
                    error=str(exc),
                )
            )

    return results


def print_category_summary(
    category: str,
    results: list[EvaluationResult],
) -> None:
    passed_count = sum(
        result.passed
        for result in results
    )

    total_count = len(results)

    pass_rate = (
        passed_count / total_count * 100
        if total_count
        else 0
    )

    print(
        f"{category}: "
        f"{passed_count}/{total_count} "
        f"({pass_rate:.1f}%)"
    )


def save_results(
    results: list[EvaluationResult],
) -> None:
    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        RESULT_DIR / "latest_results.json"
    )

    output_path.write_text(
        json.dumps(
            [
                asdict(result)
                for result in results
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"\nDetailed results saved to: "
        f"{output_path}"
    )


def main() -> None:
    print(
        "Manufacturing AI Assistant Evaluation"
    )

    print("=" * 70)

    category_results = {
        "Intent Router": (
            evaluate_intent_router()
        ),
        "Text-to-SQL": (
            evaluate_sql_generation()
        ),
        "RAG Retrieval": (
            evaluate_retrieval()
        ),
        "Query Decomposition": (
            evaluate_decomposition()
        ),
    }

    all_results: list[EvaluationResult] = []

    print("\nEvaluation summary:")

    for category, results in (
        category_results.items()
    ):
        print_category_summary(
            category,
            results,
        )

        all_results.extend(results)

    total_passed = sum(
        result.passed
        for result in all_results
    )

    total_count = len(all_results)

    overall_rate = (
        total_passed / total_count * 100
        if total_count
        else 0
    )

    print(
        f"\nOverall: "
        f"{total_passed}/{total_count} "
        f"({overall_rate:.1f}%)"
    )

    failed_results = [
        result
        for result in all_results
        if not result.passed
    ]

    if failed_results:
        print("\nFailed cases:")

        for result in failed_results:
            print("-" * 70)
            print(
                f"[{result.category}] "
                f"{result.question}"
            )
            print(
                f"Expected: {result.expected}"
            )
            print(
                f"Actual: {result.actual}"
            )

            if result.error:
                print(
                    f"Error: {result.error}"
                )

    save_results(all_results)


if __name__ == "__main__":
    main()