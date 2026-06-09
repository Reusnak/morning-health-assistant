"""定时调度：每天早上自动运行晨间健康助手。"""

import os
import time
import schedule
from dotenv import load_dotenv

load_dotenv()


def run_coach():
    """执行一次晨间对话。"""
    from morning_coach import MorningCoach
    print("\n" + "=" * 50)
    print("🌅  晨间健康助手 - 定时启动")
    print("=" * 50 + "\n")
    coach = MorningCoach()
    coach.run()


def start_scheduler():
    """启动定时调度器。"""
    schedule_time = os.environ.get("SCHEDULE_TIME", "08:00")
    schedule.every().day.at(schedule_time).do(run_coach)

    print(f"⏰  晨间健康助手已启动，每天 {schedule_time} 自动运行")
    print("   按 Ctrl+C 停止\n")

    run_coach()  # 启动时立即运行一次

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()
