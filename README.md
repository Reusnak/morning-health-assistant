# 晨间健康助手 Agent

一个晨间健康助手，通过 DeepSeek LLM 根据用户的健康数据、天气和日程动态生成个性化问候，支持多轮对话、目标追踪和定时调度。

## 架构

```
感知 (Perception)  → 获取健康数据 + 天气 + 日程
记忆 (Memory)      → 读取用户偏好 + 历史趋势 + 未完成目标
思考 (Reasoning)   → 规则引擎评分 → LLM 生成个性化问候/多轮对话/目标提取
行动 (Action)      → 彩色终端多轮对话
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY
# 可选：修改 SCHEDULE_TIME（默认 08:00）

# 单次运行
python morning_coach.py

# 定时运行（每天早上自动启动）
python scheduler.py
```

## Agent 能力

- **LLM 多轮对话**：DeepSeek 驱动，最多 5 轮，自动判断追问或收尾
- **目标追踪**：对话中自动提取用户目标，下次运行时主动跟进，3 天自动过期
- **工具调用**：获取实时天气（wttr.in）+ 日程信息，融入建议
- **个性化**：根据用户偏好（warm/direct）调整语气
- **定时调度**：通过 scheduler.py 每天定时运行

## 项目结构

- `morning_coach.py` — Agent 入口 + MorningCoach 类
- `scheduler.py` — 定时调度器
- `perception/` — 感知层，获取健康数据
- `reasoning/` — 思考层，评分 + LLM 生成（问候/对话/目标提取）
- `action/` — 行动层，彩色终端交互
- `memory/` — 记忆层，偏好 + 历史 + 目标管理
- `tools/` — 工具层，天气 + 日程
- `data/sample_data.csv` — 示例健康数据

## 运行测试

```bash
python -m pytest tests/ -v
```

## 扩展

- 接入真实健康 API：修改 `perception/health_data.py`
- 增加健康指标：修改 `reasoning/status_evaluator.py` 的评分公式
- 切换沟通渠道（飞书等）：新增 `action/` 下的模块
- 接入真实日历：修改 `tools/calendar.py`
- 接入真实天气：`tools/weather.py` 已用 wttr.in，可替换为其他 API
