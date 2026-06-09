# 多轮对话 + 目标追踪设计

## 概述

将单轮问答改为 LLM 驱动的多轮对话（最多 5 轮），LLM 自行判断是否继续追问。对话结束后自动提取用户目标，存入 goals.json，下次运行时主动跟进。未完成目标保留 3 天后自动过期。

## 对话流程

```
1. 加载未完成目标 → 融入问候语
2. LLM 生成问候（含目标跟进）
3. 展示问候 → 用户回答
4. 循环（最多 5 轮）：
   a. 将用户回答追加到 messages
   b. LLM 生成回复（追问或总结）
   c. 展示回复
   d. 如果 LLM 自然收尾或用户说"结束/再见"→ 跳出循环
   e. 否则 → 等待用户输入
5. 对话结束后，LLM 提取目标 → 存入 goals.json
6. 保存本次记录到 history.json
```

## 对话上下文维护

当前 `_call_llm()` 只传单轮消息（system + user）。改为传完整 `messages` 列表。

新增 `reasoning/llm_generator.py` 中的 `chat_turn(messages, status, style)` 函数，接收完整对话历史，返回 LLM 回复。`messages` 列表在 `morning_coach.py` 的 `run()` 中维护。

## 结束判断

三种情况结束对话：
1. 达到 5 轮上限 → 强制结束
2. 用户输入 "结束" / "再见" / "拜拜" → 用户主动退出
3. LLM 回复中不含问号（？/?）且语气像总结 → 自然收尾

## 目标追踪

### goals.json 数据结构

```json
[
  {
    "goal": "想早点下班休息",
    "date": "2026-06-08",
    "status": "active"
  },
  {
    "goal": "每天运动30分钟",
    "date": "2026-06-06",
    "status": "active"
  }
]
```

- `status`：`active`（进行中）、`done`（LLM 判断用户已完成）、`expired`（超过 3 天自动标记）
- 超过 3 天的 `active` 目标自动标记为 `expired`，不再跟进

### 记忆层新增函数（memory/profile_store.py）

| 函数 | 签名 | 说明 |
|------|------|------|
| `load_goals` | `(path: str = "goals.json") -> list[dict]` | 读取 goals.json，不存在返回空列表 |
| `save_goals` | `(goals: list[dict], path: str = "goals.json") -> None` | 写入 goals.json |
| `expire_old_goals` | `(goals: list[dict], max_days: int = 3) -> list[dict]` | 将超过 max_days 天的 active 目标标记为 expired，返回更新后的列表 |
| `get_active_goals` | `(goals: list[dict]) -> list[dict]` | 返回 status=active 的目标列表 |

### 目标提取（reasoning/llm_generator.py 新增）

对话结束后，调一次 LLM 提取目标：

```
system prompt:
你是一个助手。从以下晨间对话中提取用户今天提到的目标或计划。
输出 JSON 数组，每个元素是一个目标字符串。
如果没有明确目标，输出空数组 []。
只输出 JSON，不要其他内容。

user prompt:
{完整对话文本}
```

LLM 返回如 `["早点下班", "回家做顿好吃的"]`，用 `json.loads()` 解析，存入 goals.json。

提取失败时（LLM 返回非 JSON），静默跳过，不影响主流程。

### 目标跟进融入问候语

`generate_greeting()` 的 prompt 中新增目标上下文：

```
- 用户之前设定的未完成目标：{active_goals}
如果有关注目标，请在问候中自然地提及并询问进展。
```

无活跃目标时不追加此段。

## 文件变更

### 新增

| 文件 | 说明 |
|------|------|
| `goals.json` | 运行时自动生成 |
| `tests/test_goal_store.py` | 目标存储测试 |

### 修改

| 文件 | 改动 |
|------|------|
| `memory/profile_store.py` | 新增 `load_goals`, `save_goals`, `expire_old_goals`, `get_active_goals` |
| `memory/__init__.py` | 导出新增函数 |
| `reasoning/llm_generator.py` | 新增 `chat_turn()`, `extract_goals()`；修改 `generate_greeting()` 加入 active_goals 参数 |
| `reasoning/__init__.py` | 导出新增函数 |
| `morning_coach.py` | `run()` 改为多轮对话循环 |
| `tests/test_llm_generator.py` | 新增 `chat_turn` 和 `extract_goals` 的测试 |
| `tests/test_morning_coach.py` | 更新集成测试为多轮流程 |

## 新增接口

### reasoning/llm_generator.py

```python
def chat_turn(messages: list[dict], status: str, style: str) -> str:
    """多轮对话：传入完整 messages 列表，返回 LLM 回复。
    失败时返回降级回复。
    """

def extract_goals(conversation_text: str) -> list[str]:
    """从对话全文中提取用户目标。返回目标字符串列表。
    解析失败返回空列表。
    """
```

### reasoning/llm_generator.py 修改

```python
# generate_greeting 签名新增 active_goals 参数
def generate_greeting(status: str, style: str, trend_warning: str | None,
                      health_data: dict, active_goals: list[str] | None = None) -> str:
```

### _call_llm 修改

```python
# 当前签名（单轮）
def _call_llm(system_prompt: str, user_prompt: str, temperature: float) -> str:

# 改为（支持多轮）
def _call_llm(messages: list[dict], temperature: float) -> str:
    # messages 已包含 system prompt 作为第一条
```

## morning_coach.py run() 核心逻辑

```python
def run(self):
    # 感知
    health_data = get_yesterday_health_data()

    # 记忆：历史趋势
    trend_warning = get_trend_warning(self.history, self.profile["style"])

    # 记忆：加载并清理目标
    goals = load_goals()
    goals = expire_old_goals(goals)
    active_goals = get_active_goals(goals)
    active_goal_texts = [g["goal"] for g in active_goals]

    # 思考：生成问候（含目标跟进）
    score = calculate_composite_score(health_data["sleep_score"], health_data["stress_level"])
    status = evaluate_status(score)
    greeting = generate_greeting(status, self.profile["style"], trend_warning, health_data, active_goal_texts)

    # 行动：展示问候，初始化对话
    messages = [{"role": "system", "content": system_prompt}, {"role": "assistant", "content": greeting}]
    display_greeting(greeting)

    # 行动：多轮对话循环
    for turn in range(5):
        user_input = ask_question("你：")
        if user_input.strip() in ("结束", "再见", "拜拜"):
            break
        messages.append({"role": "user", "content": user_input})

        reply = chat_turn(messages, status, self.profile["style"])
        messages.append({"role": "assistant", "content": reply})
        display_encouragement(reply)

        # 自然收尾判断
        if "？" not in reply and "?" not in reply:
            break

    # 记忆：提取目标
    conversation_text = format_messages(messages)
    new_goal_texts = extract_goals(conversation_text)
    for g in new_goal_texts:
        goals.append({"goal": g, "date": health_data["date"], "status": "active"})
    save_goals(goals)

    # 记忆：保存历史
    save_record({
        "date": health_data["date"],
        "sleep_score": health_data["sleep_score"],
        "stress_level": health_data["stress_level"],
        "status": status,
        "user_response": user_input,
    })
```

## 错误处理

- `extract_goals()` 解析 LLM 返回值失败（非 JSON）：返回空列表，不中断主流程
- `chat_turn()` API 调用失败：返回降级文本 "今天的对话很有意义，祝你一天顺利！"
- `load_goals()` / `save_goals()` 文件异常：同 profile_store 的处理模式

## 测试策略

### tests/test_goal_store.py（新增）

- `test_load_goals_returns_empty_when_missing`
- `test_save_goals_creates_file`
- `test_expire_old_goals_marks_expired`
- `test_get_active_goals_filters_active`

### tests/test_llm_generator.py（追加）

- `TestChatTurn::test_returns_reply_with_context`
- `TestChatTurn::test_fallback_on_api_error`
- `TestExtractGoals::test_extracts_goals_from_conversation`
- `TestExtractGoals::test_returns_empty_on_parse_failure`

### tests/test_morning_coach.py（重写）

- 更新 mock 以覆盖多轮循环
- 验证 `chat_turn`, `extract_goals`, `load_goals`, `save_goals` 被正确调用
