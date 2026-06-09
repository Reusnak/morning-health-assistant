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
