"""晨间健康助手 Agent — 入口模块。"""

from perception import get_yesterday_health_data
from reasoning import (
    calculate_composite_score,
    evaluate_status,
    generate_greeting,
    generate_encouragement,
)
from action import display_greeting, ask_question, display_encouragement
from memory import load_profile, load_history, save_record, get_trend_warning


class MorningCoach:
    """晨间健康助手 Agent，协调感知→记忆→思考→行动循环。"""

    def __init__(self):
        self.profile = load_profile()
        self.history = load_history()

    def run(self) -> None:
        """执行完整的感知→记忆→思考→行动→记忆循环。"""
        # 感知：获取健康数据
        health_data = get_yesterday_health_data()

        # 记忆：检查历史趋势
        trend_warning = get_trend_warning(self.history, self.profile["style"])

        # 思考：评估状态 + 生成问候
        score = calculate_composite_score(
            health_data["sleep_score"], health_data["stress_level"]
        )
        status = evaluate_status(score)
        greeting = generate_greeting(status, self.profile["style"], trend_warning)

        # 行动：展示问候 + 等待回答 + 展示鼓励
        display_greeting(greeting)
        user_response = ask_question("你的回答：")
        encouragement = generate_encouragement(
            user_response, status, self.profile["style"]
        )
        display_encouragement(encouragement)

        # 记忆：保存本次记录
        save_record({
            "date": health_data["date"],
            "sleep_score": health_data["sleep_score"],
            "stress_level": health_data["stress_level"],
            "status": status,
            "user_response": user_response,
        })


def main():
    coach = MorningCoach()
    coach.run()


if __name__ == "__main__":
    main()
