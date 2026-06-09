"""记忆层：用户偏好与历史记录管理。"""

import json
from pathlib import Path

_DEFAULT_PROFILE = {"name": "用户", "style": "warm"}

_TREND_WARNINGS = {
    "warm": "注意到你最近几天都没怎么休息好，要对自己温柔一点哦。",
    "direct": "连续三天状态偏低，建议调整节奏。",
}


def load_profile(path: str = "user_profile.json") -> dict:
    """加载用户偏好；文件不存在则创建默认配置并返回。"""
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    p.write_text(json.dumps(_DEFAULT_PROFILE, ensure_ascii=False, indent=2), encoding="utf-8")
    return dict(_DEFAULT_PROFILE)


def load_history(path: str = "history.json", days: int = 3) -> list[dict]:
    """读取最近 N 天历史记录。"""
    p = Path(path)
    if not p.exists():
        return []
    records = json.loads(p.read_text(encoding="utf-8"))
    return records[-days:]


def save_record(record: dict, path: str = "history.json") -> None:
    """追加一条记录到历史文件。"""
    p = Path(path)
    if p.exists():
        records = json.loads(p.read_text(encoding="utf-8"))
    else:
        records = []
    records.append(record)
    p.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def get_trend_warning(history: list[dict], style: str) -> str | None:
    """连续 3 天欠佳则返回警告文本，否则 None。"""
    if len(history) < 3:
        return None
    if all(r["status"] == "poor" for r in history[-3:]):
        return _TREND_WARNINGS.get(style, _TREND_WARNINGS["warm"])
    return None


def load_goals(path: str = "goals.json") -> list[dict]:
    """读取目标列表；文件不存在返回空列表。"""
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def save_goals(goals: list[dict], path: str = "goals.json") -> None:
    """写入目标列表到文件。"""
    p = Path(path)
    p.write_text(json.dumps(goals, ensure_ascii=False, indent=2), encoding="utf-8")


def expire_old_goals(goals: list[dict], max_days: int = 3, today: str | None = None) -> list[dict]:
    """将超过 max_days 天的 active 目标标记为 expired。"""
    from datetime import date
    today_date = date.fromisoformat(today) if today else date.today()
    for g in goals:
        if g["status"] == "active":
            goal_date = date.fromisoformat(g["date"])
            if (today_date - goal_date).days > max_days:
                g["status"] = "expired"
    return goals


def get_active_goals(goals: list[dict]) -> list[dict]:
    """返回 status=active 的目标列表。"""
    return [g for g in goals if g["status"] == "active"]
