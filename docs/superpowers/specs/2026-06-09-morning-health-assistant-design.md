# 晨间健康助手 Agent 设计文档

## 概述

构建一个可运行的 Python Agent，每天早晨根据用户健康数据（睡眠评分 + 压力指数）主动对话，引导晨间反思与目标设定。采用 Hermes 架构：感知 → 思考 → 行动 → 记忆。

## 架构方案

**类封装 Agent，分层模块设计（方案 B）**

- 一个 `MorningCoach` 类协调各层
- 每层一个子包：perception / reasoning / action / memory
- 主入口 `morning_coach.py` 实例化并运行

## 项目结构

```
morning-health-assistant/
├── morning_coach.py            # 入口 + MorningCoach 类
├── perception/
│   ├── __init__.py
│   └── health_data.py          # get_yesterday_health_data()
├── reasoning/
│   ├── __init__.py
│   └── status_evaluator.py     # 综合评分 + 状态判断 + 问候语生成
├── action/
│   ├── __init__.py
│   └── console.py              # 彩色终端输出 + 用户输入
├── memory/
│   ├── __init__.py
│   └── profile_store.py        # 读写偏好 + 历史记录
├── data/
│   └── sample_data.csv         # 示例健康数据
├── user_profile.json           # 用户偏好（首次运行自动生成）
├── history.json                # 历史记录（自动追加）
├── requirements.txt
└── README.md
```

## 数据模型

### sample_data.csv

| 字段 | 类型 | 范围 | 说明 |
|---|---|---|---|
| date | str | YYYY-MM-DD | 日期 |
| sleep_score | int | 0-100 | 睡眠评分 |
| stress_level | int | 0-10 | 压力指数 |

示例：
```csv
date,sleep_score,stress_level
2026-06-06,72,5
2026-06-07,85,3
2026-06-08,45,8
```

### user_profile.json

```json
{
  "name": "用户",
  "style": "warm"
}
```

`style` 可选值：`warm`（温和共情）、`direct`（简洁务实）。首次运行时不存在，自动创建默认配置。

### history.json

```json
[
  {
    "date": "2026-06-08",
    "sleep_score": 45,
    "stress_level": 8,
    "status": "poor",
    "user_response": "今天想早点下班休息"
  }
]
```

每次运行追加一条记录。不存在时自动创建空数组。

## 核心算法

### 综合评分公式

```
composite_score = sleep_score × 0.6 + (10 - stress_level) × 4
```

- sleep_score 贡献 0~60 分
- 压力反向贡献 0~40 分
- 满分 100

### 状态阈值

| composite_score | 状态 | 标签 |
|---|---|---|
| ≥ 75 | 良好 | `good` |
| 50 ~ 74 | 一般 | `fair` |
| < 50 | 欠佳 | `poor` |

### 沟通风格适配

| 状态 | warm | direct |
|---|---|---|
| good | "早上好呀～昨天休息得不错！今天有什么事是你觉得顺其自然就好的？" | "状态不错。今天哪些事可以轻松推进？" |
| fair | "昨天好像有点累，没关系的～今天有哪些小事你能做好？" | "状态一般。今天专注做好一两件小事。" |
| poor | "昨天辛苦了...今天最重要的事就是照顾好自己，哪怕只是好好吃一顿饭。" | "状态较差。今天降低预期，优先休息。" |

### 历史趋势检测

读取 history.json 最近 3 天记录。如果连续 3 天状态均为 `poor`，在问候语前追加趋势警告：

- warm: "注意到你最近几天都没怎么休息好，要对自己温柔一点哦。"
- direct: "连续三天状态偏低，建议调整节奏。"

不满足条件时不追加任何额外文本。

## 主流程

```
MorningCoach.run():
1. perception:  get_yesterday_health_data() → 健康数据 dict
2. memory:      load_profile() → 用户偏好
                load_history() → 最近记录
                get_trend_warning() → 趋势警告文本或 None
3. reasoning:   calculate_composite_score() → 综合分
                evaluate_status() → 状态标签
                generate_greeting() → 完整问候语
4. action:      display_greeting() → 彩色打印问候
                ask_question() → 等待用户输入
                generate_encouragement() → 根据回答生成鼓励
                display_encouragement() → 彩色打印鼓励
5. memory:      save_record() → 追加本次记录到 history.json
```

## 模块接口

### perception/health_data.py

```python
def get_yesterday_health_data() -> dict:
    """返回 { "date": str, "sleep_score": int, "stress_level": int }"""
```

纯硬编码字典。未来接入真实 API 仅需修改此函数。

### reasoning/status_evaluator.py

```python
def calculate_composite_score(sleep_score: int, stress_level: int) -> float:
    """返回 0-100 综合评分"""

def evaluate_status(score: float) -> str:
    """返回 "good" | "fair" | "poor" """

def generate_greeting(status: str, style: str, trend_warning: str | None) -> str:
    """拼接完整问候语（趋势警告 + 状态问候 + 晨间问题）"""

def generate_encouragement(user_input: str, status: str, style: str) -> str:
    """根据用户回答生成一句鼓励语"""
```

### action/console.py

```python
def print_colored(text: str, color: str) -> None:
    """用 colorama 输出彩色文本"""

def display_greeting(greeting: str) -> None:
    """格式化打印问候语（绿色标题 + 白色正文）"""

def ask_question(question: str) -> str:
    """打印问题，等待输入，返回回答"""

def display_encouragement(text: str) -> None:
    """打印鼓励语（黄色）"""
```

### memory/profile_store.py

```python
def load_profile(path: str = "user_profile.json") -> dict:
    """加载用户偏好；文件不存在则创建默认配置并返回"""

def load_history(path: str = "history.json", days: int = 3) -> list[dict]:
    """读取最近 N 天历史记录"""

def save_record(record: dict, path: str = "history.json") -> None:
    """追加一条记录到历史文件"""

def get_trend_warning(history: list[dict], style: str) -> str | None:
    """连续欠佳则返回警告文本，否则 None"""
```

### morning_coach.py

```python
class MorningCoach:
    def __init__(self):
        self.profile = load_profile()
        self.history = load_history()

    def run(self) -> None:
        """感知→记忆→思考→行动→记忆 完整循环"""

def main():
    coach = MorningCoach()
    coach.run()

if __name__ == "__main__":
    main()
```

## 依赖

- `colorama` — 跨平台彩色终端输出

requirements.txt：
```
colorama>=0.4.6
```

## 运行方式

```bash
pip install -r requirements.txt
python morning_coach.py
```

## 可扩展性设计

| 扩展方向 | 改动点 | 其他模块 |
|---|---|---|
| 接入真实健康 API | 仅改 `perception/health_data.py` | 不变 |
| 增加更多健康指标 | 改评分公式 + 问候语模板 | 接口不变 |
| 切换沟通渠道（微信/邮件） | 新增 action 层模块 | 其他层不变 |
| 更复杂的规则引擎 | 替换 `reasoning/` 内部实现 | 接口不变 |
