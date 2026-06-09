# 晨间健康助手 Agent 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个可运行的晨间健康助手 Agent，根据健康数据生成个性化问候，通过彩色终端与用户交互。

**Architecture:** 类封装 Agent（MorningCoach），四层模块化设计：perception（感知）→ reasoning（思考）→ action（行动）→ memory（记忆）。各层通过 dict 传递数据，接口清晰，便于扩展。

**Tech Stack:** Python 3.10+, colorama, pytest

---

## File Structure

```
morning-health-assistant/
├── morning_coach.py                  # 入口 + MorningCoach 类
├── perception/
│   ├── __init__.py                   # from .health_data import get_yesterday_health_data
│   └── health_data.py                # 硬编码健康数据
├── reasoning/
│   ├── __init__.py                   # from .status_evaluator import *
│   └── status_evaluator.py           # 评分 + 状态判断 + 问候语生成
├── action/
│   ├── __init__.py                   # from .console import *
│   └── console.py                    # 彩色终端交互
├── memory/
│   ├── __init__.py                   # from .profile_store import *
│   └── profile_store.py              # 偏好 + 历史记录读写
├── data/
│   └── sample_data.csv               # 示例数据
├── tests/
│   ├── __init__.py
│   ├── test_health_data.py
│   ├── test_status_evaluator.py
│   ├── test_profile_store.py
│   ├── test_console.py
│   └── test_morning_coach.py
├── user_profile.json                 # 运行时自动生成
├── history.json                      # 运行时自动生成
├── requirements.txt
└── README.md
```

---

### Task 1: 项目脚手架

**Files:**
- Create: `requirements.txt`
- Create: `perception/__init__.py`, `reasoning/__init__.py`, `action/__init__.py`, `memory/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: 初始化项目结构**

创建 requirements.txt：

```
colorama>=0.4.6
pytest>=7.0.0
```

创建五个空 `__init__.py`（导入语句在各自模块创建时同步添加）：

- `perception/__init__.py`
- `reasoning/__init__.py`
- `action/__init__.py`
- `memory/__init__.py`
- `tests/__init__.py`

均为空文件。

- [ ] **Step 2: 安装依赖**

Run: `pip install -r requirements.txt`
Expected: Successfully installed colorama, pytest

- [ ] **Step 3: 初始化 git 并提交**

Run: `git init && git add -A && git commit -m "chore: project scaffold with package structure"`

---

### Task 2: perception/health_data.py

**Files:**
- Create: `perception/health_data.py`
- Create: `tests/test_health_data.py`

- [ ] **Step 1: 写失败测试**

`tests/test_health_data.py`：
```python
from perception.health_data import get_yesterday_health_data


def test_returns_dict_with_required_keys():
    data = get_yesterday_health_data()
    assert isinstance(data, dict)
    assert "date" in data
    assert "sleep_score" in data
    assert "stress_level" in data


def test_sleep_score_in_valid_range():
    data = get_yesterday_health_data()
    assert 0 <= data["sleep_score"] <= 100


def test_stress_level_in_valid_range():
    data = get_yesterday_health_data()
    assert 0 <= data["stress_level"] <= 10
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_health_data.py -v`
Expected: FAIL — ModuleNotFoundError: No module named 'perception.health_data'

- [ ] **Step 3: 写实现**

`perception/health_data.py`：
```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_health_data.py -v`
Expected: 3 passed

- [ ] **Step 5: 更新 perception/__init__.py**

追加导入：
```python
from .health_data import get_yesterday_health_data
```

- [ ] **Step 6: 提交**

Run: `git add -A && git commit -m "feat: add perception layer with health data module"`

---

### Task 3: reasoning/status_evaluator.py — 评分与状态判断

**Files:**
- Create: `reasoning/status_evaluator.py`
- Create: `tests/test_status_evaluator.py`

- [ ] **Step 1: 写失败测试**

`tests/test_status_evaluator.py`：
```python
import pytest
from reasoning.status_evaluator import calculate_composite_score, evaluate_status


class TestCalculateCompositeScore:
    def test_perfect_score(self):
        assert calculate_composite_score(100, 0) == 100.0

    def test_worst_score(self):
        assert calculate_composite_score(0, 10) == 0.0

    def test_moderate_values(self):
        # 62 * 0.6 + (10 - 5) * 4 = 37.2 + 20 = 57.2
        assert calculate_composite_score(62, 5) == pytest.approx(57.2)

    def test_high_sleep_high_stress(self):
        # 90 * 0.6 + (10 - 8) * 4 = 54 + 8 = 62
        assert calculate_composite_score(90, 8) == pytest.approx(62.0)


class TestEvaluateStatus:
    def test_good_threshold(self):
        # 75 * 0.6 + (10 - 0) * 4 = 45 + 40 = 85
        assert evaluate_status(85.0) == "good"

    def test_good_boundary(self):
        assert evaluate_status(75.0) == "good"

    def test_fair(self):
        assert evaluate_status(57.2) == "fair"

    def test_fair_boundary_low(self):
        assert evaluate_status(50.0) == "fair"

    def test_poor(self):
        assert evaluate_status(30.0) == "poor"

    def test_poor_boundary(self):
        assert evaluate_status(49.9) == "poor"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_status_evaluator.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: 写实现**

`reasoning/status_evaluator.py`（先只写评分和状态函数）：
```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_status_evaluator.py -v`
Expected: 6 passed

- [ ] **Step 5: 更新 reasoning/__init__.py**

追加导入（先只导出评分相关函数，Task 4 会追加问候语函数）：
```python
from .status_evaluator import calculate_composite_score, evaluate_status
```

- [ ] **Step 6: 提交**

Run: `git add -A && git commit -m "feat: add scoring and status evaluation in reasoning layer"`

---

### Task 4: reasoning/status_evaluator.py — 问候语生成

**Files:**
- Modify: `reasoning/status_evaluator.py`（追加 generate_greeting 和 generate_encouragement）
- Modify: `tests/test_status_evaluator.py`（追加测试）

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_status_evaluator.py`：
```python
from reasoning.status_evaluator import generate_greeting, generate_encouragement


class TestGenerateGreeting:
    def test_warm_good(self):
        result = generate_greeting("good", "warm", None)
        assert "早上好" in result
        assert "顺其自然" in result

    def test_warm_fair(self):
        result = generate_greeting("fair", "warm", None)
        assert "早上好" in result
        assert "小事" in result

    def test_warm_poor(self):
        result = generate_greeting("poor", "warm", None)
        assert "早上好" in result
        assert "照顾好自己" in result

    def test_direct_good(self):
        result = generate_greeting("good", "direct", None)
        assert "轻松推进" in result

    def test_direct_fair(self):
        result = generate_greeting("fair", "direct", None)
        assert "小事" in result

    def test_direct_poor(self):
        result = generate_greeting("poor", "direct", None)
        assert "优先休息" in result

    def test_with_trend_warning(self):
        result = generate_greeting("poor", "warm", "注意到你最近几天都没怎么休息好，要对自己温柔一点哦。")
        assert result.startswith("注意到你最近")
        assert "照顾好自己" in result

    def test_no_trend_warning(self):
        result = generate_greeting("good", "warm", None)
        assert not result.startswith("注意到")


class TestGenerateEncouragement:
    def test_warm_good(self):
        result = generate_encouragement("今天想轻松一点", "good", "warm")
        assert len(result) > 0

    def test_warm_poor(self):
        result = generate_encouragement("只想休息", "poor", "warm")
        assert len(result) > 0

    def test_direct_good(self):
        result = generate_encouragement("继续推进项目", "good", "direct")
        assert len(result) > 0

    def test_direct_poor(self):
        result = generate_encouragement("什么都不想做", "poor", "direct")
        assert len(result) > 0
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_status_evaluator.py::TestGenerateGreeting -v`
Expected: FAIL — ImportError

- [ ] **Step 3: 追加实现到 reasoning/status_evaluator.py**

在文件末尾追加：
```python
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
```

- [ ] **Step 4: 运行全部 reasoning 测试确认通过**

Run: `python -m pytest tests/test_status_evaluator.py -v`
Expected: 16 passed

- [ ] **Step 5: 更新 reasoning/__init__.py**

替换为完整导入：
```python
from .status_evaluator import (
    calculate_composite_score,
    evaluate_status,
    generate_greeting,
    generate_encouragement,
)
```

- [ ] **Step 6: 提交**

Run: `git add -A && git commit -m "feat: add greeting and encouragement generation"`

---

### Task 5: memory/profile_store.py

**Files:**
- Create: `memory/profile_store.py`
- Create: `tests/test_profile_store.py`

- [ ] **Step 1: 写失败测试**

`tests/test_profile_store.py`：
```python
import json
import pytest
from memory.profile_store import load_profile, load_history, save_record, get_trend_warning


class TestLoadProfile:
    def test_creates_default_when_missing(self, tmp_path):
        path = tmp_path / "user_profile.json"
        profile = load_profile(str(path))
        assert profile["name"] == "用户"
        assert profile["style"] == "warm"
        assert path.exists()

    def test_loads_existing(self, tmp_path):
        path = tmp_path / "user_profile.json"
        path.write_text(json.dumps({"name": "小明", "style": "direct"}))
        profile = load_profile(str(path))
        assert profile["name"] == "小明"
        assert profile["style"] == "direct"


class TestLoadHistory:
    def test_returns_empty_when_missing(self, tmp_path):
        path = tmp_path / "history.json"
        history = load_history(str(path))
        assert history == []

    def test_loads_existing(self, tmp_path):
        path = tmp_path / "history.json"
        records = [
            {"date": "2026-06-06", "status": "fair"},
            {"date": "2026-06-07", "status": "good"},
            {"date": "2026-06-08", "status": "poor"},
        ]
        path.write_text(json.dumps(records))
        history = load_history(str(path))
        assert len(history) == 3

    def test_limits_to_n_days(self, tmp_path):
        path = tmp_path / "history.json"
        records = [{"date": f"2026-06-0{i}", "status": "fair"} for i in range(1, 6)]
        path.write_text(json.dumps(records))
        history = load_history(str(path), days=3)
        assert len(history) == 3


class TestSaveRecord:
    def test_appends_to_existing(self, tmp_path):
        path = tmp_path / "history.json"
        path.write_text(json.dumps([{"date": "2026-06-07", "status": "good"}]))
        save_record({"date": "2026-06-08", "status": "poor"}, str(path))
        records = json.loads(path.read_text())
        assert len(records) == 2
        assert records[-1]["status"] == "poor"

    def test_creates_file_when_missing(self, tmp_path):
        path = tmp_path / "history.json"
        save_record({"date": "2026-06-08", "status": "fair"}, str(path))
        records = json.loads(path.read_text())
        assert len(records) == 1


class TestGetTrendWarning:
    def test_no_warning_when_fewer_than_3(self):
        history = [
            {"status": "poor"},
            {"status": "poor"},
        ]
        assert get_trend_warning(history, "warm") is None

    def test_warning_when_3_consecutive_poor(self):
        history = [
            {"status": "poor"},
            {"status": "poor"},
            {"status": "poor"},
        ]
        result = get_trend_warning(history, "warm")
        assert "温柔" in result

    def test_warning_direct_style(self):
        history = [
            {"status": "poor"},
            {"status": "poor"},
            {"status": "poor"},
        ]
        result = get_trend_warning(history, "direct")
        assert "调整节奏" in result

    def test_no_warning_when_not_all_poor(self):
        history = [
            {"status": "fair"},
            {"status": "poor"},
            {"status": "poor"},
        ]
        assert get_trend_warning(history, "warm") is None

    def test_no_warning_when_empty(self):
        assert get_trend_warning([], "warm") is None
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_profile_store.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: 写实现**

`memory/profile_store.py`：
```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_profile_store.py -v`
Expected: 11 passed

- [ ] **Step 5: 更新 memory/__init__.py**

追加导入：
```python
from .profile_store import load_profile, load_history, save_record, get_trend_warning
```

- [ ] **Step 6: 提交**

Run: `git add -A && git commit -m "feat: add memory layer with profile and history management"`

---

### Task 6: action/console.py

**Files:**
- Create: `action/console.py`
- Create: `tests/test_console.py`

- [ ] **Step 1: 写失败测试**

`tests/test_console.py`：
```python
from action.console import print_colored, display_greeting, ask_question, display_encouragement


class TestPrintColored:
    def test_outputs_text(self, capsys):
        print_colored("hello", "green")
        captured = capsys.readouterr()
        assert "hello" in captured.out


class TestDisplayGreeting:
    def test_outputs_greeting(self, capsys):
        display_greeting("早上好呀～")
        captured = capsys.readouterr()
        assert "早上好呀～" in captured.out


class TestAskQuestion:
    def test_returns_user_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "今天想轻松一点")
        result = ask_question("你的回答：")
        assert result == "今天想轻松一点"


class TestDisplayEncouragement:
    def test_outputs_encouragement(self, capsys):
        display_encouragement("慢慢来～")
        captured = capsys.readouterr()
        assert "慢慢来" in captured.out
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_console.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: 写实现**

`action/console.py`：
```python
"""行动层：彩色终端交互。"""

from colorama import Fore, Style, init

init(autoreset=True)


def print_colored(text: str, color: str) -> None:
    """用 colorama 输出彩色文本。"""
    color_map = {
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "red": Fore.RED,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
    }
    print(f"{color_map.get(color, Fore.WHITE)}{text}{Style.RESET_ALL}")


def display_greeting(greeting: str) -> None:
    """格式化打印问候语（绿色标题 + 白色正文）。"""
    print()
    print_colored("=" * 40, "green")
    print_colored("☀️  晨间健康助手", "green")
    print_colored("=" * 40, "green")
    print()
    print_colored(greeting, "white")
    print()


def ask_question(prompt: str = "> ") -> str:
    """打印提示，等待用户输入，返回回答。"""
    return input(prompt)


def display_encouragement(text: str) -> None:
    """打印鼓励语（黄色）。"""
    print()
    print_colored(text, "yellow")
    print()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_console.py -v`
Expected: 4 passed

- [ ] **Step 5: 更新 action/__init__.py**

追加导入：
```python
from .console import print_colored, display_greeting, ask_question, display_encouragement
```

- [ ] **Step 6: 提交**

Run: `git add -A && git commit -m "feat: add action layer with colored console output"`

---

### Task 7: morning_coach.py — 集成

**Files:**
- Create: `morning_coach.py`
- Create: `tests/test_morning_coach.py`

- [ ] **Step 1: 写失败测试**

`tests/test_morning_coach.py`：
```python
from unittest.mock import patch
from morning_coach import MorningCoach


class TestMorningCoach:
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    def test_init_loads_profile_and_history(self, mock_profile, mock_history):
        coach = MorningCoach()
        assert coach.profile["style"] == "warm"
        assert coach.history == []

    @patch("morning_coach.display_encouragement")
    @patch("morning_coach.generate_encouragement", return_value="慢慢来～")
    @patch("morning_coach.ask_question", return_value="今天想轻松一点")
    @patch("morning_coach.display_greeting")
    @patch("morning_coach.generate_greeting", return_value="早上好呀～")
    @patch("morning_coach.evaluate_status", return_value="fair")
    @patch("morning_coach.calculate_composite_score", return_value=57.2)
    @patch("morning_coach.get_trend_warning", return_value=None)
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    @patch("morning_coach.get_yesterday_health_data")
    @patch("morning_coach.save_record")
    def test_run_full_flow(self, mock_save, mock_health, mock_profile, mock_history,
                           mock_trend, mock_score, mock_status, mock_greeting_gen,
                           mock_display, mock_ask, mock_enc_gen, mock_enc_display):
        mock_health.return_value = {"date": "2026-06-08", "sleep_score": 62, "stress_level": 5}

        coach = MorningCoach()
        coach.run()

        mock_health.assert_called_once()
        mock_score.assert_called_once_with(62, 5)
        mock_status.assert_called_once_with(57.2)
        mock_greeting_gen.assert_called_once_with("fair", "warm", None)
        mock_display.assert_called_once_with("早上好呀～")
        mock_ask.assert_called_once()
        mock_enc_gen.assert_called_once_with("今天想轻松一点", "fair", "warm")
        mock_enc_display.assert_called_once_with("慢慢来～")
        mock_save.assert_called_once()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_morning_coach.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: 写实现**

`morning_coach.py`：
```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_morning_coach.py -v`
Expected: 2 passed

- [ ] **Step 5: 运行全部测试确认无回归**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed（约 28 个测试）

- [ ] **Step 6: 提交**

Run: `git add -A && git commit -m "feat: integrate all layers into MorningCoach agent"`

---

### Task 8: 数据文件 + 文档

**Files:**
- Create: `data/sample_data.csv`
- Create: `README.md`

- [ ] **Step 1: 创建示例数据**

`data/sample_data.csv`：
```csv
date,sleep_score,stress_level
2026-06-03,55,7
2026-06-04,80,2
2026-06-05,65,4
2026-06-06,72,5
2026-06-07,85,3
2026-06-08,45,8
```

- [ ] **Step 2: 创建 README**

`README.md`：
```markdown
# 晨间健康助手 Agent

一个基于 Hermes 架构（感知→思考→行动→记忆）的晨间健康助手，根据用户的健康数据生成个性化问候和引导。

## 架构

```
感知 (Perception)  → 获取健康数据（sleep_score, stress_level）
记忆 (Memory)      → 读取用户偏好 + 历史状态趋势
思考 (Reasoning)   → 综合评分 → 状态判断 → 生成问候语
行动 (Action)      → 彩色终端输出 + 用户交互
记忆 (Memory)      → 保存本次交互记录
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python morning_coach.py
```

## 项目结构

- `morning_coach.py` — 入口 + MorningCoach 类
- `perception/` — 感知层，获取健康数据
- `reasoning/` — 思考层，评估状态 + 生成问候
- `action/` — 行动层，彩色终端交互
- `memory/` — 记忆层，偏好 + 历史管理
- `data/sample_data.csv` — 示例健康数据

## 运行测试

```bash
python -m pytest tests/ -v
```

## 扩展

- 接入真实 API：修改 `perception/health_data.py`
- 增加健康指标：修改 `reasoning/status_evaluator.py` 的评分公式
- 切换沟通渠道：新增 `action/` 下的模块
```

- [ ] **Step 3: 最终集成测试**

手动运行确认完整流程：
```bash
python morning_coach.py
```

Expected: 彩色输出问候语，等待输入后显示鼓励语，退出后在项目根目录生成 `user_profile.json` 和 `history.json`。

- [ ] **Step 4: 提交**

Run: `git add -A && git commit -m "docs: add sample data and README"`
