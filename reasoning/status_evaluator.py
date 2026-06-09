"""思考层：健康状态评估。"""


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
