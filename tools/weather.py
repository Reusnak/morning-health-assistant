"""工具层：天气查询。"""

import json
import urllib.request


def get_weather(city: str = "Beijing") -> dict:
    """从 wttr.in 获取天气数据。

    Returns:
        {"city": str, "temperature": str, "description": str, "humidity": str}
        获取失败时返回 {"city": city, "error": "..."}
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        current = data["current_condition"][0]
        return {
            "city": city,
            "temperature": current.get("temp_C", "?"),
            "description": current.get("weatherDesc", [{}])[0].get("value", "未知"),
            "humidity": current.get("humidity", "?"),
        }
    except Exception as e:
        return {"city": city, "error": str(e)}
