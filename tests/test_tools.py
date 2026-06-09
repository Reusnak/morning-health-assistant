from unittest.mock import patch, MagicMock
from tools.weather import get_weather
from tools.calendar import get_today_schedule


class TestGetWeather:
    @patch("tools.weather.urllib.request.urlopen")
    def test_returns_weather_data(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"current_condition":[{"temp_C":"22","weatherDesc":[{"value":"Sunny"}],"humidity":"45"}]}'
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = get_weather("Beijing")
        assert result["temperature"] == "22"
        assert result["description"] == "Sunny"
        assert result["humidity"] == "45"

    @patch("tools.weather.urllib.request.urlopen", side_effect=Exception("Network error"))
    def test_returns_error_on_failure(self, mock_urlopen):
        result = get_weather("Beijing")
        assert "error" in result


class TestGetTodaySchedule:
    def test_returns_list_of_events(self):
        schedule = get_today_schedule()
        assert isinstance(schedule, list)
        assert len(schedule) > 0
        assert "time" in schedule[0]
        assert "title" in schedule[0]
        assert "duration_min" in schedule[0]
