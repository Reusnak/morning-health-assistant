"""晨间健康助手 Agent — 入口模块。"""

from perception import get_yesterday_health_data
from reasoning import (
    calculate_composite_score,
    evaluate_status,
    generate_greeting,
    chat_turn,
    extract_goals,
)
from action import display_greeting, ask_question, display_encouragement
from memory import (
    load_profile, load_history, save_record, get_trend_warning,
    load_goals, save_goals, expire_old_goals, get_active_goals,
)
from tools import get_weather, get_today_schedule

_EXIT_KEYWORDS = {"结束", "再见", "拜拜", "quit", "exit"}


def _format_conversation(messages: list[dict]) -> str:
    """将 messages 列表格式化为对话文本（用于目标提取）。"""
    role_map = {"user": "用户", "assistant": "助手"}
    lines = []
    for m in messages:
        if m["role"] in role_map:
            lines.append(f"{role_map[m['role']]}：{m['content']}")
    return "\n".join(lines)


class MorningCoach:
    """晨间健康助手 Agent，协调感知→记忆→思考→行动循环。"""

    def __init__(self):
        self.profile = load_profile()
        self.history = load_history()

    def run(self) -> None:
        """执行完整的感知→记忆→思考→行动→记忆循环（多轮对话）。"""
        # 感知：获取健康数据
        health_data = get_yesterday_health_data()

        # 感知：获取工具数据（天气 + 日程）
        weather = get_weather(city=self.profile.get("city"))
        schedule = get_today_schedule()

        # 记忆：检查历史趋势
        trend_warning = get_trend_warning(self.history, self.profile["style"])

        # 记忆：加载并清理目标
        goals = load_goals()
        goals = expire_old_goals(goals)
        active_goals = get_active_goals(goals)
        active_goal_texts = [g["goal"] for g in active_goals]

        # 思考：评估状态 + 生成问候（含目标跟进）
        score = calculate_composite_score(
            health_data["sleep_score"], health_data["stress_level"]
        )
        status = evaluate_status(score)
        greeting = generate_greeting(
            status, self.profile["style"], trend_warning, health_data,
            active_goal_texts, weather=weather, schedule=schedule,
        )

        # 行动：展示问候，初始化对话历史
        messages = [{"role": "assistant", "content": greeting}]
        display_greeting(greeting)

        # 行动：多轮对话循环
        last_user_input = ""
        for turn in range(5):
            user_input = ask_question("你：")
            last_user_input = user_input
            if user_input.strip() in _EXIT_KEYWORDS:
                break
            messages.append({"role": "user", "content": user_input})

            reply = chat_turn(messages, status, self.profile["style"])
            messages.append({"role": "assistant", "content": reply})
            display_encouragement(reply)

            # 自然收尾判断：回复不含问号
            if "？" not in reply and "?" not in reply:
                break

        # 记忆：提取目标
        conversation_text = _format_conversation(messages)
        new_goal_texts = extract_goals(conversation_text)
        for g in new_goal_texts:
            goals.append({
                "goal": g,
                "date": health_data["date"],
                "status": "active",
            })
        save_goals(goals)

        # 记忆：保存历史
        save_record({
            "date": health_data["date"],
            "sleep_score": health_data["sleep_score"],
            "stress_level": health_data["stress_level"],
            "status": status,
            "user_response": last_user_input,
        })


def main():
    coach = MorningCoach()
    coach.run()


if __name__ == "__main__":
    main()
