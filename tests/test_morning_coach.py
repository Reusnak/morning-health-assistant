from unittest.mock import patch
from morning_coach import MorningCoach


class TestMorningCoach:
    @patch("morning_coach.load_goals", return_value=[])
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    def test_init_loads_profile_and_history(self, mock_profile, mock_history, mock_goals):
        coach = MorningCoach()
        assert coach.profile["style"] == "warm"
        assert coach.history == []

    @patch("morning_coach.save_goals")
    @patch("morning_coach.extract_goals", return_value=["早点下班"])
    @patch("morning_coach.display_encouragement")
    @patch("morning_coach.chat_turn", return_value="加油！你今天打算怎么做？")
    @patch("morning_coach.ask_question", side_effect=["想早点下班", "再见"])
    @patch("morning_coach.display_greeting")
    @patch("morning_coach.generate_greeting", return_value="早上好！")
    @patch("morning_coach.evaluate_status", return_value="fair")
    @patch("morning_coach.calculate_composite_score", return_value=57.2)
    @patch("morning_coach.get_active_goals", return_value=[])
    @patch("morning_coach.expire_old_goals", return_value=[])
    @patch("morning_coach.get_trend_warning", return_value=None)
    @patch("morning_coach.load_goals", return_value=[])
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    @patch("morning_coach.get_yesterday_health_data")
    @patch("morning_coach.save_record")
    def test_run_multi_turn_flow(self, mock_save, mock_health, mock_profile, mock_history,
                                  mock_trend, mock_goals_load, mock_expire, mock_active,
                                  mock_score, mock_status, mock_greeting_gen,
                                  mock_display, mock_ask, mock_chat, mock_enc_display,
                                  mock_extract, mock_save_goals):
        mock_health.return_value = {"date": "2026-06-10", "sleep_score": 62, "stress_level": 5}

        coach = MorningCoach()
        coach.run()

        mock_greeting_gen.assert_called_once()
        mock_display.assert_called_once_with("早上好！")
        mock_chat.assert_called_once()
        mock_extract.assert_called_once()
        mock_save.assert_called_once()
        mock_save_goals.assert_called_once()

    @patch("morning_coach.save_goals")
    @patch("morning_coach.extract_goals", return_value=[])
    @patch("morning_coach.display_encouragement")
    @patch("morning_coach.chat_turn", return_value="好的，祝你今天一切顺利！")
    @patch("morning_coach.ask_question", side_effect=["没什么特别的"])
    @patch("morning_coach.display_greeting")
    @patch("morning_coach.generate_greeting", return_value="早上好！")
    @patch("morning_coach.evaluate_status", return_value="good")
    @patch("morning_coach.calculate_composite_score", return_value=85.0)
    @patch("morning_coach.get_active_goals", return_value=[])
    @patch("morning_coach.expire_old_goals", return_value=[])
    @patch("morning_coach.get_trend_warning", return_value=None)
    @patch("morning_coach.load_goals", return_value=[])
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    @patch("morning_coach.get_yesterday_health_data")
    @patch("morning_coach.save_record")
    def test_run_natural_ending(self, mock_save, mock_health, mock_profile, mock_history,
                                mock_trend, mock_goals_load, mock_expire, mock_active,
                                mock_score, mock_status, mock_greeting_gen,
                                mock_display, mock_ask, mock_chat, mock_enc_display,
                                mock_extract, mock_save_goals):
        """chat_turn 返回不含问号时自然结束。"""
        mock_health.return_value = {"date": "2026-06-10", "sleep_score": 90, "stress_level": 1}

        coach = MorningCoach()
        coach.run()

        mock_chat.assert_called_once()
        assert mock_ask.call_count == 1
