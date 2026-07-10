from app.services.intent_router_service import (
    route_question,
)


TEST_QUESTIONS = [
    "哪个设备的异常率最高？",
    "最近30天每天的平均重量偏差是多少？",
    "E102报警是什么意思？",
    "连续三次UNDER应该怎么处理？",
    "哪个设备的异常率最高，应该检查什么？",
    "哪个设备最需要校准？",
    "找出UNDER最多的设备并告诉我处理流程。",
    "你好",
]


def main() -> None:
    for question in TEST_QUESTIONS:
        print("=" * 70)
        print("Question:", question)

        decision = route_question(
            question
        )

        print("Intent:", decision.intent)
        print(
            "Confidence:",
            f"{decision.confidence:.2f}",
        )
        print("Reason:", decision.reason)


if __name__ == "__main__":
    main()