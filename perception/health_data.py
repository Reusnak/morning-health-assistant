"""感知层：获取用户昨日健康数据。"""


def get_yesterday_health_data() -> dict:
    """返回模拟的昨日健康数据。

    Returns:
        dict: 包含 date, sleep_score, stress_level 的字典。
    """
    return {
        "date": "2026-06-08",
        "sleep_score": 62,
        "stress_level": 5,
    }
