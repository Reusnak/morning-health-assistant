from unittest.mock import patch
from morning_coach import MorningCoach


class TestMorningCoach:
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    def test_init_loads_profile_and_history(self, mock_profile, mock_history):
        coach = MorningCoach()
        assert coach.profile["style"] == "warm"
        assert coach.history == []

    @patch("morning_coach.display_encouragement")
    @patch("morning_coach.generate_encouragement", return_value="慢慢来～")
    @patch("morning_coach.ask_question", return_value="今天想轻松一点")
    @patch("morning_coach.display_greeting")
    @patch("morning_coach.generate_greeting", return_value="早上好呀～")
    @patch("morning_coach.evaluate_status", return_value="fair")
    @patch("morning_coach.calculate_composite_score", return_value=57.2)
    @patch("morning_coach.get_trend_warning", return_value=None)
    @patch("morning_coach.load_history", return_value=[])
    @patch("morning_coach.load_profile", return_value={"name": "用户", "style": "warm"})
    @patch("morning_coach.get_yesterday_health_data")
    @patch("morning_coach.save_record")
    def test_run_full_flow(self, mock_save, mock_health, mock_profile, mock_history,
                           mock_trend, mock_score, mock_status, mock_greeting_gen,
                           mock_display, mock_ask, mock_enc_gen, mock_enc_display):
        mock_health.return_value = {"date": "2026-06-08", "sleep_score": 62, "stress_level": 5}

        coach = MorningCoach()
        coach.run()

        mock_health.assert_called_once()
        mock_score.assert_called_once_with(62, 5)
        mock_status.assert_called_once_with(57.2)
        mock_greeting_gen.assert_called_once_with("fair", "warm", None,
                                                   {"date": "2026-06-08", "sleep_score": 62, "stress_level": 5})
        mock_display.assert_called_once_with("早上好呀～")
        mock_ask.assert_called_once()
        mock_enc_gen.assert_called_once_with("今天想轻松一点", "fair", "warm")
        mock_enc_display.assert_called_once_with("慢慢来～")
        mock_save.assert_called_once()
