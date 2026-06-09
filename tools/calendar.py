"""工具层：日程查询。"""


def get_today_schedule() -> list[dict]:
    """获取今日日程。

    Returns:
        [{"time": str, "title": str, "duration_min": int}]
        当前返回模拟数据，未来可接入真实日历 API。
    """
    return [
        {"time": "09:00", "title": "团队站会", "duration_min": 30},
        {"time": "14:00", "title": "项目评审", "duration_min": 60},
        {"time": "17:00", "title": "1on1 与主管", "duration_min": 30},
    ]
