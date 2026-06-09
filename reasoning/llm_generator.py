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
