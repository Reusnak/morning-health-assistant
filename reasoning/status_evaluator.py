"""思考层：健康状态评估与问候语生成。"""


def calculate_composite_score(sleep_score: int, stress_level: int) -> float:
    """计算综合健康评分。

    composite_score = sleep_score × 0.6 + (10 - stress_level) × 4
    满分 100。
    """
    return sleep_score * 0.6 + (10 - stress_level) * 4


def evaluate_status(score: float) -> str:
    """根据综合评分判断基础状态。

    Returns:
        "good" | "fair" | "poor"
    """
    if score >= 75:
        return "good"
    elif score >= 50:
        return "fair"
    else:
        return "poor"


_GREETINGS = {
    ("good", "warm"): "早上好呀～昨天休息得不错！今天有什么事是你觉得顺其自然就好的？",
    ("good", "direct"): "状态不错。今天哪些事可以轻松推进？",
    ("fair", "warm"): "早上好呀～昨天好像有点累，没关系的。今天有哪些小事你能做好？从小处开始就好。",
    ("fair", "direct"): "状态一般。今天专注做好一两件小事。",
    ("poor", "warm"): "早上好呀～昨天辛苦了...今天最重要的事就是照顾好自己，哪怕只是好好吃一顿饭。",
    ("poor", "direct"): "状态较差。今天降低预期，优先休息。",
}

_ENCOURAGEMENTS = {
    ("good", "warm"): "听起来不错呢，祝你今天一切顺利！",
    ("good", "direct"): "保持节奏，继续推进。",
    ("fair", "warm"): "慢慢来，每一步都算数的～",
    ("fair", "direct"): "今天做好一件事就足够了。",
    ("poor", "warm"): "已经是很勇敢的一天了，照顾好自己。",
    ("poor", "direct"): "降低预期，优先恢复。",
}


def generate_greeting(status: str, style: str, trend_warning: str | None) -> str:
    """根据状态、风格和趋势警告生成完整问候语。"""
    greeting = _GREETINGS.get((status, style), _GREETINGS[(status, "warm")])
    if trend_warning:
        return f"{trend_warning}\n{greeting}"
    return greeting


def generate_encouragement(user_input: str, status: str, style: str) -> str:
    """根据用户回答和当前状态生成鼓励语。"""
    return _ENCOURAGEMENTS.get((status, style), _ENCOURAGEMENTS[(status, "warm")])
