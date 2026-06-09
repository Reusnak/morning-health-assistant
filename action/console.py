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
