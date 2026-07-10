from app.services.hybrid_analysis_service import (
    analyze_hybrid_question,
)


def main() -> None:
    question = (
        "哪个设备的异常率最高，"
        "根据SOP应该检查什么？"
    )

    result = analyze_hybrid_question(
        question
    )

    print("\nAnswer:")
    print(result.answer)

    print("\nSQL:")
    print(result.sql)

    print("\nData:")
    print(
        result.result_df
        .head(20)
        .to_string(index=False)
    )

    print("\nSources:")

    for index, source in enumerate(
        result.sources,
        start=1,
    ):
        print(
            f"{index}. {source.source} "
            f"(score={source.score:.4f})"
        )


if __name__ == "__main__":
    main()