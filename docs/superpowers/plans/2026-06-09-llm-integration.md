# LLM 集成实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 reasoning 层的硬编码问候语/鼓励语模板替换为 DeepSeek LLM 调用，使 Agent 能动态生成个性化自然语言回复。

**Architecture:** 在 reasoning 层新增 `llm_generator.py` 封装 LLM 调用，删除 `status_evaluator.py` 中的硬编码字典。评分和状态判断保留规则引擎。LLM 调用失败时降级到默认模板。

**Tech Stack:** openai SDK (DeepSeek 兼容), python-dotenv

---

## File Structure

```
变更文件：
├── reasoning/
│   ├── __init__.py                   # 修改：从 llm_generator 导入 greeting/encouragement
│   ├── status_evaluator.py           # 修改：删除硬编码字典和两个函数
│   └── llm_generator.py              # 新增：LLM 调用封装
├── tests/
│   ├── test_status_evaluator.py      # 修改：删除 TestGenerateGreeting/TestGenerateEncouragement
│   ├── test_llm_generator.py         # 新增：LLM mock 测试
│   └── test_morning_coach.py         # 修改：generate_greeting 调用多传 health_data
├── morning_coach.py                  # 修改：generate_greeting 多传 health_data
├── requirements.txt                  # 修改：新增 openai, python-dotenv
├── .gitignore                        # 修改：新增 .env
└── .env.example                      # 新增：配置模板
```

---

### Task 1: 配置与依赖

**Files:**
- Modify: `requirements.txt`
- Modify: `.gitignore`
- Create: `.env.example`

- [ ] **Step 1: 更新 requirements.txt**

替换为：
```
colorama>=0.4.6
pytest>=7.0.0
openai>=1.0.0
python-dotenv>=1.0.0
```

- [ ] **Step 2: 更新 .gitignore**

追加 `.env`：
```
__pycache__/
*.pyc
.pytest_cache/
.env
```

- [ ] **Step 3: 创建 .env.example**

```
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

- [ ] **Step 4: 安装新依赖**

Run: `pip install openai python-dotenv`
Expected: Successfully installed

- [ ] **Step 5: 提交**

Run: `git add -A && git commit -m "chore: add LLM dependencies and config template"`

---

### Task 2: reasoning/llm_generator.py

**Files:**
- Create: `reasoning/llm_generator.py`
- Create: `tests/test_llm_generator.py`

- [ ] **Step 1: 写失败测试**

`tests/test_llm_generator.py`：
```python
from unittest.mock import patch, MagicMock
from reasoning.llm_generator import get_llm_client, generate_greeting, generate_encouragement


class TestGetLlmClient:
    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "test-key",
        "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
        "DEEPSEEK_MODEL": "deepseek-chat",
    })
    def test_creates_client_with_env_vars(self):
        client = get_llm_client()
        assert client is not None


class TestGenerateGreeting:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_calls_llm_and_returns_string(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "早上好！昨天休息得不错，今天精力充沛地开始吧。"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate_greeting("good", "warm", None,
                                   {"date": "2026-06-08", "sleep_score": 85, "stress_level": 2})
        assert "早上好" in result
        mock_client.chat.completions.create.assert_called_once()

    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_health_data(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "你好"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        generate_greeting("fair", "warm", None,
                          {"date": "2026-06-08", "sleep_score": 62, "stress_level": 5})

        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args.kwargs["messages"][1]["content"]
        assert "62" in prompt_content
        assert "5" in prompt_content

    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_trend_warning(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "你好"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        generate_greeting("poor", "warm", "连续三天状态偏低",
                          {"date": "2026-06-08", "sleep_score": 40, "stress_level": 8})

        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args.kwargs["messages"][1]["content"]
        assert "连续三天状态偏低" in prompt_content

    @patch("reasoning.llm_generator.get_llm_client")
    def test_fallback_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        result = generate_greeting("good", "warm", None,
                                   {"date": "2026-06-08", "sleep_score": 85, "stress_level": 2})
        assert len(result) > 0  # 应该返回降级模板


class TestGenerateEncouragement:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_calls_llm_and_returns_string(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "慢慢来，你已经很棒了！"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate_encouragement("今天有点累", "fair", "warm")
        assert "慢慢来" in result

    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_user_input(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "加油"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        generate_encouragement("想休息一下", "poor", "direct")

        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args.kwargs["messages"][1]["content"]
        assert "想休息一下" in prompt_content

    @patch("reasoning.llm_generator.get_llm_client")
    def test_fallback_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        result = generate_encouragement("今天想轻松一点", "fair", "warm")
        assert len(result) > 0  # 应该返回降级模板
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_llm_generator.py -v`
Expected: FAIL — ImportError

- [ ] **Step 3: 写实现**

`reasoning/llm_generator.py`：
```python
"""思考层：LLM 驱动的问候语与鼓励语生成。"""

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


def get_llm_client() -> OpenAI:
    """从环境变量读取配置，创建 DeepSeek API 客户端。"""
    return OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )


def _call_llm(system_prompt: str, user_prompt: str, temperature: float) -> str:
    """调用 LLM API 并返回生成的文本。"""
    client = get_llm_client()
    response = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=200,
    )
    return response.choices[0].message.content


def generate_greeting(status: str, style: str, trend_warning: str | None,
                      health_data: dict) -> str:
    """调用 LLM 生成个性化问候语。失败时降级到默认模板。"""
    style_desc = _STYLE_DESCS.get(style, _STYLE_DESCS["warm"])
    status_desc = _STATUS_DESCS.get(status, _STATUS_DESCS["fair"])
    trend_section = f"- 趋势提醒：{trend_warning}" if trend_warning else ""

    system_prompt = "你是一个温暖的晨间健康助手。根据用户的健康状态数据，生成一段个性化的晨间问候语。只输出问候语本身，不要加引号或额外说明。"
    user_prompt = (
        f"请生成一段晨间问候语。\n"
        f"要求：\n"
        f"- 语气风格：{style_desc}\n"
        f"- 用户状态：{status_desc}\n"
        f"- 昨日数据：睡眠评分 {health_data['sleep_score']}/100，压力指数 {health_data['stress_level']}/10\n"
        f"{trend_section}\n"
        f"只输出问候语本身。"
    )

    try:
        return _call_llm(system_prompt, user_prompt, temperature=0.7)
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
        return _call_llm(system_prompt, user_prompt, temperature=0.8)
    except Exception:
        return _FALLBACK_ENCOURAGEMENTS.get((status, style), _FALLBACK_ENCOURAGEMENTS[(status, "warm")])
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_llm_generator.py -v`
Expected: 8 passed

- [ ] **Step 5: 提交**

Run: `git add -A && git commit -m "feat: add LLM-powered greeting and encouragement generation"`

---

### Task 3: 清理 status_evaluator.py + 更新测试

**Files:**
- Modify: `reasoning/status_evaluator.py`（删除硬编码字典和两个旧函数）
- Modify: `tests/test_status_evaluator.py`（删除 TestGenerateGreeting 和 TestGenerateEncouragement）
- Modify: `reasoning/__init__.py`（从 llm_generator 导入）

- [ ] **Step 1: 清理 status_evaluator.py**

替换整个文件为（只保留评分和状态判断）：
```python
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
```

- [ ] **Step 2: 清理 tests/test_status_evaluator.py**

替换整个文件为（只保留评分和状态判断测试）：
```python
import pytest
from reasoning.status_evaluator import calculate_composite_score, evaluate_status


class TestCalculateCompositeScore:
    def test_perfect_score(self):
        assert calculate_composite_score(100, 0) == 100.0

    def test_worst_score(self):
        assert calculate_composite_score(0, 10) == 0.0

    def test_moderate_values(self):
        assert calculate_composite_score(62, 5) == pytest.approx(57.2)

    def test_high_sleep_high_stress(self):
        assert calculate_composite_score(90, 8) == pytest.approx(62.0)


class TestEvaluateStatus:
    def test_good_threshold(self):
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

- [ ] **Step 3: 更新 reasoning/__init__.py**

替换为：
```python
from .status_evaluator import calculate_composite_score, evaluate_status
from .llm_generator import generate_greeting, generate_encouragement
```

- [ ] **Step 4: 运行 reasoning 层测试确认通过**

Run: `python -m pytest tests/test_status_evaluator.py tests/test_llm_generator.py -v`
Expected: 18 passed (10 + 8)

- [ ] **Step 5: 提交**

Run: `git add -A && git commit -m "refactor: remove hardcoded templates, route greeting/encouragement through LLM"`

---

### Task 4: 更新 morning_coach.py + 集成测试

**Files:**
- Modify: `morning_coach.py`（generate_greeting 多传 health_data）
- Modify: `tests/test_morning_coach.py`（更新 mock 签名）

- [ ] **Step 1: 更新 morning_coach.py**

将第 34 行：
```python
        greeting = generate_greeting(status, self.profile["style"], trend_warning)
```
替换为：
```python
        greeting = generate_greeting(status, self.profile["style"], trend_warning, health_data)
```

其余代码不变。

- [ ] **Step 2: 更新 tests/test_morning_coach.py**

将第 36 行的 mock 断言：
```python
        mock_greeting_gen.assert_called_once_with("fair", "warm", None)
```
替换为：
```python
        mock_greeting_gen.assert_called_once_with("fair", "warm", None,
                                                   {"date": "2026-06-08", "sleep_score": 62, "stress_level": 5})
```

其余代码不变。

- [ ] **Step 3: 运行全部测试确认无回归**

Run: `python -m pytest tests/ -v`
Expected: 全部 passed（约 30 个测试：10 status_evaluator + 8 llm_generator + 4 console + 3 health_data + 2 morning_coach + 12 profile_store - 删除的 12 个旧测试 + 新增 8 个）

具体：3 + 4 + 10 + 12 + 8 + 2 = 39 passed

- [ ] **Step 4: 提交**

Run: `git add -A && git commit -m "feat: pass health_data to LLM greeting for personalized generation"`

---

### Task 5: 更新 README + 最终验证

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README**

在"快速开始"部分，`pip install` 之后、`python morning_coach.py` 之前，添加配置说明。将快速开始部分替换为：

```markdown
## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 DeepSeek API
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY

# 运行
python morning_coach.py
```
```

其余部分不变。

- [ ] **Step 2: 运行全部测试最终确认**

Run: `python -m pytest tests/ -v`
Expected: 39 passed

- [ ] **Step 3: 提交**

Run: `git add -A && git commit -m "docs: update README with LLM configuration instructions"`
