from app.services.query_decomposition_service import (
    decompose_hybrid_question,
)


TEST_QUESTIONS = [
    (
        "哪个设备的异常率最高，"
        "根据SOP应该检查什么？"
    ),
    (
        "找出UNDER数量最多的产品，"
        "并告诉我连续UNDER时如何处理。"
    ),
    (
        "目前哪台设备最需要校准，"
        "校准流程是什么？"
    ),
    (
        "最近30天异常率最高的设备是哪台，"
        "应该采取哪些质量管理措施？"
    ),
]


def main() -> None:
    for question in TEST_QUESTIONS:
        print("=" * 80)
        print("Original question:")
        print(question)

        result = decompose_hybrid_question(
            question
        )

        print("\nDatabase question:")
        print(result.database_question)

        print("\nKnowledge question:")
        print(result.knowledge_question)

        print("\nReason:")
        print(result.reason)

        print()


if __name__ == "__main__":
    main()