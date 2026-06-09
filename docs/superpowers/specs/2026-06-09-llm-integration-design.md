# LLM 集成设计：让晨间健康助手成为真正的 Agent

## 概述

将 reasoning 层的硬编码问候语/鼓励语模板替换为 DeepSeek LLM 调用，使 Agent 能根据健康数据和用户回答动态生成个性化、有同理心的自然语言回复。评分和状态判断保留规则引擎（确定性）。

## 架构方案

**方案 A：在 reasoning 层内新增 llm_generator.py**

- 新增 `reasoning/llm_generator.py` 封装 LLM 调用
- 删除 `status_evaluator.py` 中的硬编码字典
- 其他层不受影响

## 依赖变更

### requirements.txt 新增

```
openai>=1.0.0
python-dotenv>=1.0.0
```

DeepSeek 兼容 OpenAI SDK，通过 `openai.OpenAI(base_url=...)` 调用。

### .env 文件（新增，加入 .gitignore）

```
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### .env.example（新增，提交到 git）

```
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 文件变更

### 新增

| 文件 | 说明 |
|------|------|
| `reasoning/llm_generator.py` | LLM 调用封装：get_llm_client(), generate_greeting(), generate_encouragement() |
| `.env.example` | 配置模板 |
| `tests/test_llm_generator.py` | LLM 生成函数的 mock 测试 |

### 修改

| 文件 | 改动 |
|------|------|
| `reasoning/status_evaluator.py` | 删除 `_GREETINGS`、`_ENCOURAGEMENTS` 字典和旧的 `generate_greeting()`、`generate_encouragement()` 函数 |
| `reasoning/__init__.py` | `generate_greeting` 和 `generate_encouragement` 从 `llm_generator` 导入 |
| `morning_coach.py` | `generate_greeting()` 调用多传 `health_data` 参数 |
| `requirements.txt` | 新增 `openai` 和 `python-dotenv` |
| `.gitignore` | 新增 `.env` |

### 删除

| 文件中的内容 | 说明 |
|---|---|
| `tests/test_status_evaluator.py` 中的 `TestGenerateGreeting` 和 `TestGenerateEncouragement` | 这些测的是硬编码字典，已移除 |

## reasoning/llm_generator.py 接口

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm_client() -> OpenAI:
    """从 .env 读取配置，创建 DeepSeek API 客户端。"""

def generate_greeting(status: str, style: str, trend_warning: str | None,
                      health_data: dict) -> str:
    """调用 LLM 生成个性化问候语。
    
    Args:
        status: "good" | "fair" | "poor"
        style: "warm" | "direct"
        trend_warning: 连续欠佳时的趋势警告文本，或 None
        health_data: {"date": str, "sleep_score": int, "stress_level": int}
    
    Returns:
        LLM 生成的问候语字符串
    """

def generate_encouragement(user_input: str, status: str, style: str) -> str:
    """调用 LLM 根据用户回答生成鼓励语。
    
    Args:
        user_input: 用户的回答文本
        status: "good" | "fair" | "poor"
        style: "warm" | "direct"
    
    Returns:
        LLM 生成的鼓励语字符串
    """
```

## Prompt 设计

### generate_greeting system prompt

```
你是一个温暖的晨间健康助手。根据用户的健康状态数据，生成一段个性化的晨间问候语。

要求：
- 语气风格：{style_desc}
- 用户状态：{status_desc}
- 昨日数据：睡眠评分 {sleep_score}/100，压力指数 {stress_level}/10
{trend_section}
只输出问候语本身，不要加引号或额外说明。
```

其中：
- style "warm" → style_desc = "温和共情，像一个关心你的朋友"
- style "direct" → style_desc = "简洁务实，给出具体建议"
- status "good" → status_desc = "状态良好"
- status "fair" → status_desc = "状态一般"
- status "poor" → status_desc = "状态欠佳"
- trend_section = f"- 趋势提醒：{trend_warning}" 或 ""

### generate_encouragement system prompt

```
你是一个温暖的晨间健康助手。用户刚刚回答了你的晨间问题。

要求：
- 语气风格：{style_desc}
- 用户当前状态：{status_desc}
- 用户的回答："{user_input}"
- 生成一句简短的鼓励（1-2句话）

只输出鼓励语本身，不要加引号或额外说明。
```

### API 调用参数

- model: 从 .env 读取 DEEPSEEK_MODEL
- temperature: 0.7（问候语）/ 0.8（鼓励语）
- max_tokens: 200
- 单轮调用，不维护多轮对话

## morning_coach.py 改动

```python
# 改动前
greeting = generate_greeting(status, self.profile["style"], trend_warning)

# 改动后
greeting = generate_greeting(status, self.profile["style"], trend_warning, health_data)
```

`generate_encouragement` 签名不变，无需改动调用方式。

## 主流程（更新后）

```
1. 感知：health_data = get_yesterday_health_data()
2. 记忆：trend_warning = get_trend_warning(history, style)
3. 规则引擎：score = calculate_composite_score(sleep_score, stress_level)
              status = evaluate_status(score)
4. LLM 生成：greeting = generate_greeting(status, style, trend_warning, health_data)
5. 行动：display_greeting(greeting)
6. 行动：user_response = ask_question("你的回答：")
7. LLM 生成：encouragement = generate_encouragement(user_response, status, style)
8. 行动：display_encouragement(encouragement)
9. 记忆：save_record({...})
```

## 测试策略

### tests/test_llm_generator.py（新增）

所有测试 mock `openai.OpenAI` 的 `chat.completions.create` 方法，不发起真实 API 调用。

```python
from unittest.mock import patch, MagicMock

class TestGetLlmClient:
    def test_creates_client_with_env_vars(self):
        # 验证从 .env 读取 base_url 和 api_key

class TestGenerateGreeting:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_calls_llm_and_returns_string(self, mock_get_client):
        # mock LLM 返回，验证调用参数和返回值
    
    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_health_data(self, mock_get_client):
        # 验证 prompt 中包含 sleep_score, stress_level
    
    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_trend_warning(self, mock_get_client):
        # 验证有趋势警告时 prompt 中包含它

class TestGenerateEncouragement:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_calls_llm_and_returns_string(self, mock_get_client):
        # mock LLM 返回，验证调用参数和返回值
    
    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_user_input(self, mock_get_client):
        # 验证 prompt 中包含用户的回答
```

### tests/test_status_evaluator.py（修改）

- 删除 `TestGenerateGreeting` 和 `TestGenerateEncouragement` 类
- 保留 `TestCalculateCompositeScore` 和 `TestEvaluateStatus`（规则引擎不变）

### tests/test_morning_coach.py（修改）

- `generate_greeting` mock 需要多接受 `health_data` 参数
- 验证调用时传入了 `health_data`

## 错误处理

- `.env` 文件不存在或缺少 API key：启动时报错退出，提示用户配置
- LLM API 调用失败（网络/限流）：打印友好错误信息，降级到规则引擎的默认问候语
