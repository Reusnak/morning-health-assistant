from unittest.mock import patch, MagicMock
from scheduler import run_coach


class TestRunCoach:
    @patch("morning_coach.MorningCoach")
    def test_creates_and_runs_coach(self, MockCoach):
        mock_instance = MagicMock()
        MockCoach.return_value = mock_instance

        run_coach()

        MockCoach.assert_called_once()
        mock_instance.run.assert_called_once()
