# 晨间健康助手 Agent

一个基于 Hermes 架构（感知→思考→行动→记忆）的晨间健康助手，通过 DeepSeek LLM 根据用户的健康数据动态生成个性化问候和引导。

## 架构

```
感知 (Perception)  → 获取健康数据（sleep_score, stress_level）
记忆 (Memory)      → 读取用户偏好 + 历史状态趋势
思考 (Reasoning)   → 规则引擎评分 → LLM 生成问候语/鼓励语
行动 (Action)      → 彩色终端输出 + 用户交互
记忆 (Memory)      → 保存本次交互记录
```

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
