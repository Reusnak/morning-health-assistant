# 多轮对话 + 目标追踪实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将单轮问答改为 LLM 驱动的多轮对话（最多 5 轮），对话结束后自动提取用户目标，下次运行时主动跟进。

**Architecture:** 在现有 reasoning/memory 层上扩展。重构 `_call_llm()` 支持 messages 列表，新增 `chat_turn()` 和 `extract_goals()` 函数，memory 层新增目标存储函数，morning_coach.py 的 `run()` 改为多轮循环。

**Tech Stack:** openai SDK (DeepSeek), python-dotenv, pytest

---

## File Structure

```
变更文件：
├── memory/
│   ├── __init__.py                   # 修改：导出目标函数
│   └── profile_store.py              # 修改：新增 load_goals, save_goals, expire_old_goals, get_active_goals
├── reasoning/
│   ├── __init__.py                   # 修改：导出 chat_turn, extract_goals
│   └── llm_generator.py              # 修改：重构 _call_llm, 新增 chat_turn/extract_goals, 改 generate_greeting
├── morning_coach.py                  # 重写：run() 改为多轮对话循环
├── tests/
│   ├── test_goal_store.py            # 新增：目标存储测试
│   ├── test_llm_generator.py         # 修改：追加 chat_turn/extract_goals 测试
│   └── test_morning_coach.py         # 重写：多轮流程测试
```

---

### Task 1: 目标存储（memory 层）

**Files:**
- Modify: `memory/profile_store.py`
- Modify: `memory/__init__.py`
- Create: `tests/test_goal_store.py`

- [ ] **Step 1: 写失败测试**

`tests/test_goal_store.py`：
```python
import json
from memory.profile_store import load_goals, save_goals, expire_old_goals, get_active_goals


class TestLoadGoals:
    def test_returns_empty_when_missing(self, tmp_path):
        path = tmp_path / "goals.json"
        assert load_goals(str(path)) == []

    def test_loads_existing(self, tmp_path):
        path = tmp_path / "goals.json"
        goals = [{"goal": "早点下班", "date": "2026-06-09", "status": "active"}]
        path.write_text(json.dumps(goals))
        assert len(load_goals(str(path))) == 1


class TestSaveGoals:
    def test_creates_file(self, tmp_path):
        path = tmp_path / "goals.json"
        goals = [{"goal": "运动30分钟", "date": "2026-06-09", "status": "active"}]
        save_goals(goals, str(path))
        loaded = json.loads(path.read_text())
        assert len(loaded) == 1

    def test_overwrites_existing(self, tmp_path):
        path = tmp_path / "goals.json"
        path.write_text(json.dumps([{"goal": "旧目标", "date": "2026-06-08", "status": "active"}]))
        save_goals([{"goal": "新目标", "date": "2026-06-09", "status": "active"}], str(path))
        loaded = json.loads(path.read_text())
        assert len(loaded) == 1
        assert loaded[0]["goal"] == "新目标"


class TestExpireOldGoals:
    def test_marks_old_active_as_expired(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-05", "status": "active"},
            {"goal": "目标B", "date": "2026-06-09", "status": "active"},
        ]
        result = expire_old_goals(goals, max_days=3, today="2026-06-09")
        assert result[0]["status"] == "expired"
        assert result[1]["status"] == "active"

    def test_does_not_expire_recent(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-08", "status": "active"},
        ]
        result = expire_old_goals(goals, max_days=3, today="2026-06-09")
        assert result[0]["status"] == "active"

    def test_already_expired_stays_expired(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-05", "status": "expired"},
        ]
        result = expire_old_goals(goals, max_days=3, today="2026-06-09")
        assert result[0]["status"] == "expired"

    def test_empty_list(self):
        assert expire_old_goals([], max_days=3, today="2026-06-09") == []


class TestGetActiveGoals:
    def test_filters_active(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-08", "status": "active"},
            {"goal": "目标B", "date": "2026-06-07", "status": "done"},
            {"goal": "目标C", "date": "2026-06-09", "status": "active"},
        ]
        active = get_active_goals(goals)
        assert len(active) == 2

    def test_empty_list(self):
        assert get_active_goals([]) == []
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_goal_store.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: 写实现**

追加到 `memory/profile_store.py` 文件末尾（保留现有函数不变）：
```python
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
    from datetime import date, timedelta
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
```

- [ ] **Step 4: 更新 memory/__init__.py**

替换为：
```python
from .profile_store import (
    load_profile, load_history, save_record, get_trend_warning,
    load_goals, save_goals, expire_old_goals, get_active_goals,
)
```

- [ ] **Step 5: 运行测试确认通过**

Run: `python -m pytest tests/test_goal_store.py -v`
Expected: 9 passed

- [ ] **Step 6: 运行全部测试确认无回归**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed

- [ ] **Step 7: 提交**

Run: `git add -A && git commit -m "feat: add goal storage in memory layer"`

---

### Task 2: 重构 _call_llm + 新增 chat_turn 和 extract_goals

**Files:**
- Modify: `reasoning/llm_generator.py`
- Modify: `tests/test_llm_generator.py`
- Modify: `reasoning/__init__.py`

此任务会重构 `_call_llm` 签名从 `(system_prompt, user_prompt, temperature)` 改为 `(messages, temperature)`，同步更新所有调用方。

- [ ] **Step 1: 追加失败测试到 tests/test_llm_generator.py**

在文件末尾追加（保留现有测试不变）：
```python
from reasoning.llm_generator import chat_turn, extract_goals


class TestChatTurn:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_reply_with_context(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "听起来不错！那今天有什么具体计划吗？"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        messages = [
            {"role": "system", "content": "你是晨间助手"},
            {"role": "assistant", "content": "早上好！"},
            {"role": "user", "content": "今天想轻松一点"},
        ]
        result = chat_turn(messages, "fair", "warm")
        assert "听起来" in result
        mock_client.chat.completions.create.assert_called_once()

    @patch("reasoning.llm_generator.get_llm_client")
    def test_fallback_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        messages = [
            {"role": "system", "content": "你是晨间助手"},
            {"role": "assistant", "content": "早上好！"},
            {"role": "user", "content": "今天想轻松一点"},
        ]
        result = chat_turn(messages, "fair", "warm")
        assert len(result) > 0


class TestExtractGoals:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_extracts_goals_from_conversation(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["早点下班", "做顿好吃的"]'
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        conversation = "助手：早上好！\n用户：想早点下班，回家做顿好吃的。"
        result = extract_goals(conversation)
        assert result == ["早点下班", "做顿好吃的"]

    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_empty_when_no_goals(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "[]"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = extract_goals("助手：早上好！\n用户：没什么特别的。")
        assert result == []

    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_empty_on_parse_failure(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这不是JSON"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = extract_goals("助手：早上好！\n用户：随便聊聊。")
        assert result == []

    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_empty_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        result = extract_goals("对话内容")
        assert result == []
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_llm_generator.py::TestChatTurn -v`
Expected: FAIL — ImportError

- [ ] **Step 3: 重写 reasoning/llm_generator.py**

替换整个文件为：
```python
"""思考层：LLM 驱动的问候语、对话与目标提取。"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_STYLE_DESCS = {
    "warm": "温和共情，像一个关心你的朋友",
    "direct": "简洁务实，给出具体建议",
}

_STATUS_DESCS = {
    "good": "状态良好",
    "fair": "状态一般",
    "poor": "状态欠佳",
}

_FALLBACK_GREETINGS = {
    ("good", "warm"): "早上好呀～昨天休息得不错！今天有什么事是你觉得顺其自然就好的？",
    ("good", "direct"): "状态不错。今天哪些事可以轻松推进？",
    ("fair", "warm"): "早上好呀～昨天好像有点累，没关系的。今天有哪些小事你能做好？从小处开始就好。",
    ("fair", "direct"): "状态一般。今天专注做好一两件小事。",
    ("poor", "warm"): "早上好呀～昨天辛苦了...今天最重要的事就是照顾好自己，哪怕只是好好吃一顿饭。",
    ("poor", "direct"): "状态较差。今天降低预期，优先休息。",
}

_FALLBACK_ENCOURAGEMENTS = {
    ("good", "warm"): "听起来不错呢，祝你今天一切顺利！",
    ("good", "direct"): "保持节奏，继续推进。",
    ("fair", "warm"): "慢慢来，每一步都算数的～",
    ("fair", "direct"): "今天做好一件事就足够了。",
    ("poor", "warm"): "已经是很勇敢的一天了，照顾好自己。",
    ("poor", "direct"): "降低预期，优先恢复。",
}

_CHAT_SYSTEM_PROMPT = (
    "你是一个温暖的晨间健康助手。你正在和用户进行晨间对话。"
    "根据对话上下文，自然地追问或回应。"
    "如果你想结束对话，给出一段温暖的总结鼓励，不要用问号结尾。"
    "如果你还想继续了解用户，用问号结尾的问题追问。"
    "只输出你的回复，不要加引号或额外说明。"
)


def get_llm_client() -> OpenAI:
    """从环境变量读取配置，创建 DeepSeek API 客户端。"""
    return OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )


def _call_llm(messages: list[dict], temperature: float) -> str:
    """调用 LLM API 并返回生成的文本。messages 包含 system prompt。"""
    client = get_llm_client()
    response = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=messages,
        temperature=temperature,
        max_tokens=200,
    )
    return response.choices[0].message.content


def generate_greeting(status: str, style: str, trend_warning: str | None,
                      health_data: dict, active_goals: list[str] | None = None) -> str:
    """调用 LLM 生成个性化问候语。失败时降级到默认模板。"""
    style_desc = _STYLE_DESCS.get(style, _STYLE_DESCS["warm"])
    status_desc = _STATUS_DESCS.get(status, _STATUS_DESCS["fair"])
    trend_section = f"- 趋势提醒：{trend_warning}" if trend_warning else ""
    goals_section = ""
    if active_goals:
        goals_list = "、".join(active_goals)
        goals_section = f"- 用户之前设定的未完成目标：{goals_list}\n如果有关注目标，请在问候中自然地提及并询问进展。\n"

    system_prompt = "你是一个温暖的晨间健康助手。根据用户的健康状态数据，生成一段个性化的晨间问候语。只输出问候语本身，不要加引号或额外说明。"
    user_prompt = (
        f"请生成一段晨间问候语。\n"
        f"要求：\n"
        f"- 语气风格：{style_desc}\n"
        f"- 用户状态：{status_desc}\n"
        f"- 昨日数据：睡眠评分 {health_data['sleep_score']}/100，压力指数 {health_data['stress_level']}/10\n"
        f"{goals_section}"
        f"{trend_section}\n"
        f"只输出问候语本身。"
    )

    try:
        return _call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ], temperature=0.7)
    except Exception:
        return _FALLBACK_GREETINGS.get((status, style), _FALLBACK_GREETINGS[(status, "warm")])


def generate_encouragement(user_input: str, status: str, style: str) -> str:
    """调用 LLM 根据用户回答生成鼓励语。失败时降级到默认模板。"""
    style_desc = _STYLE_DESCS.get(style, _STYLE_DESCS["warm"])
    status_desc = _STATUS_DESCS.get(status, _STATUS_DESCS["fair"])

    system_prompt = "你是一个温暖的晨间健康助手。用户刚刚回答了你的晨间问题。只输出鼓励语本身，不要加引号或额外说明。"
    user_prompt = (
        f"请生成一句简短的鼓励。\n"
        f"要求：\n"
        f"- 语气风格：{style_desc}\n"
        f"- 用户当前状态：{status_desc}\n"
        f"- 用户的回答：\"{user_input}\"\n"
        f"- 生成一句简短的鼓励（1-2句话）\n"
        f"只输出鼓励语本身。"
    )

    try:
        return _call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ], temperature=0.8)
    except Exception:
        return _FALLBACK_ENCOURAGEMENTS.get((status, style), _FALLBACK_ENCOURAGEMENTS[(status, "warm")])


def chat_turn(messages: list[dict], status: str, style: str) -> str:
    """多轮对话：传入完整 messages 列表，返回 LLM 回复。失败时返回降级文本。"""
    style_desc = _STYLE_DESCS.get(style, _STYLE_DESCS["warm"])
    status_desc = _STATUS_DESCS.get(status, _STATUS_DESCS["fair"])

    system_content = f"{_CHAT_SYSTEM_PROMPT}\n语气风格：{style_desc}\n用户当前状态：{status_desc}"

    full_messages = [{"role": "system", "content": system_content}] + messages

    try:
        return _call_llm(full_messages, temperature=0.8)
    except Exception:
        return "今天的对话很有意义，祝你一天顺利！"


def extract_goals(conversation_text: str) -> list[str]:
    """从对话全文中提取用户目标。返回目标字符串列表。解析失败返回空列表。"""
    system_prompt = (
        "你是一个助手。从以下晨间对话中提取用户今天提到的目标或计划。"
        "输出 JSON 数组，每个元素是一个简短的目标字符串。"
        "如果没有明确目标，输出空数组 []。"
        "只输出 JSON 数组，不要其他内容。"
    )

    try:
        raw = _call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": conversation_text},
        ], temperature=0.3)
        return json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return []
```

- [ ] **Step 4: 更新 reasoning/__init__.py**

替换为：
```python
from .status_evaluator import calculate_composite_score, evaluate_status
from .llm_generator import generate_greeting, generate_encouragement, chat_turn, extract_goals
```

- [ ] **Step 5: 更新现有测试中的 mock 断言**

`tests/test_llm_generator.py` 中的 `TestGenerateGreeting` 和 `TestGenerateEncouragement` 测试了 `_call_llm` 的旧签名。由于 `_call_llm` 现在接收 `messages` 列表而非 `system_prompt` + `user_prompt`，需要确认现有测试的 mock 断言方式。

现有测试通过 `call_args.kwargs["messages"][1]["content"]` 访问 prompt 内容，这仍然有效，因为 `_call_llm` 现在直接把 messages 传给 API。无需修改现有测试。

Run: `python -m pytest tests/test_llm_generator.py -v`
Expected: 18 passed (8 existing + 6 TestChatTurn + 4 TestExtractGoals)

- [ ] **Step 6: 运行全部测试确认无回归**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed

- [ ] **Step 7: 提交**

Run: `git add -A && git commit -m "feat: add multi-turn chat and goal extraction with LLM"`

---

### Task 3: 重写 morning_coach.py 为多轮对话

**Files:**
- Modify: `morning_coach.py`
- Modify: `tests/test_morning_coach.py`

- [ ] **Step 1: 重写 morning_coach.py**

替换整个文件为：
```python
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
            status, self.profile["style"], trend_warning, health_data, active_goal_texts
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
```

- [ ] **Step 2: 重写 tests/test_morning_coach.py**

替换整个文件为：
```python
from unittest.mock import patch, MagicMock
from morning_coach import MorningCoach


def _mock_make_chain(ask_responses):
    """创建 ask_question 的 side_effect 序列，最后一次触发退出。"""
    return ask_responses + ["再见"]


class TestMorningCoach:
    @patch("morning_coach.load_goals", return_value=[])
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    def test_init_loads_profile_and_history(self, mock_profile, mock_history, mock_goals):
        coach = MorningCoach()
        assert coach.profile["style"] == "warm"
        assert coach.history == []

    @patch("morning_coach.save_goals")
    @patch("morning_coach.extract_goals", return_value=["早点下班"])
    @patch("morning_coach.display_encouragement")
    @patch("morning_coach.chat_turn", return_value="加油！")
    @patch("morning_coach.ask_question", side_effect=["想早点下班", "再见"])
    @patch("morning_coach.display_greeting")
    @patch("morning_coach.generate_greeting", return_value="早上好！")
    @patch("morning_coach.evaluate_status", return_value="fair")
    @patch("morning_coach.calculate_composite_score", return_value=57.2)
    @patch("morning_coach.get_active_goals", return_value=[])
    @patch("morning_coach.expire_old_goals", return_value=[])
    @patch("morning_coach.get_trend_warning", return_value=None)
    @patch("morning_coach.load_goals", return_value=[])
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    @patch("morning_coach.get_yesterday_health_data")
    @patch("morning_coach.save_record")
    def test_run_multi_turn_flow(self, mock_save, mock_health, mock_profile, mock_history,
                                  mock_trend, mock_goals_load, mock_expire, mock_active,
                                  mock_score, mock_status, mock_greeting_gen,
                                  mock_display, mock_ask, mock_chat, mock_enc_display,
                                  mock_extract, mock_save_goals):
        mock_health.return_value = {"date": "2026-06-10", "sleep_score": 62, "stress_level": 5}

        coach = MorningCoach()
        coach.run()

        mock_greeting_gen.assert_called_once()
        mock_display.assert_called_once_with("早上好！")
        mock_chat.assert_called_once()
        mock_extract.assert_called_once()
        mock_save.assert_called_once()
        mock_save_goals.assert_called_once()

    @patch("morning_coach.save_goals")
    @patch("morning_coach.extract_goals", return_value=[])
    @patch("morning_coach.display_encouragement")
    @patch("morning_coach.chat_turn", return_value="好的，祝你今天一切顺利！")
    @patch("morning_coach.ask_question", side_effect=["没什么特别的"])
    @patch("morning_coach.display_greeting")
    @patch("morning_coach.generate_greeting", return_value="早上好！")
    @patch("morning_coach.evaluate_status", return_value="good")
    @patch("morning_coach.calculate_composite_score", return_value=85.0)
    @patch("morning_coach.get_active_goals", return_value=[])
    @patch("morning_coach.expire_old_goals", return_value=[])
    @patch("morning_coach.get_trend_warning", return_value=None)
    @patch("morning_coach.load_goals", return_value=[])
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    @patch("morning_coach.get_yesterday_health_data")
    @patch("morning_coach.save_record")
    def test_run_natural_ending(self, mock_save, mock_health, mock_profile, mock_history,
                                mock_trend, mock_goals_load, mock_expire, mock_active,
                                mock_score, mock_status, mock_greeting_gen,
                                mock_display, mock_ask, mock_chat, mock_enc_display,
                                mock_extract, mock_save_goals):
        """chat_turn 返回不含问号时自然结束。"""
        mock_health.return_value = {"date": "2026-06-10", "sleep_score": 90, "stress_level": 1}

        coach = MorningCoach()
        coach.run()

        mock_chat.assert_called_once()
        # 自然收尾，不再 ask_question
        assert mock_ask.call_count == 1
```

- [ ] **Step 3: 运行全部测试**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed

- [ ] **Step 4: 提交**

Run: `git add -A && git commit -m "feat: rewrite morning_coach with multi-turn conversation loop"`

---

### Task 4: 最终验证

- [ ] **Step 1: 运行全部测试**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed（约 55 个测试）

- [ ] **Step 2: 手动集成测试（需要 .env 配置）**

如果 `.env` 已配置 DeepSeek API Key：
```bash
python morning_coach.py
```

Expected：Agent 输出问候，用户回答后追问，输入"再见"结束。运行后检查 `goals.json` 是否包含提取的目标。

- [ ] **Step 3: 提交最终状态**

Run: `git add -A && git commit -m "test: verify multi-turn conversation integration"`
