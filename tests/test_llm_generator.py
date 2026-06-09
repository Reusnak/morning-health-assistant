from unittest.mock import patch, MagicMock
from reasoning.llm_generator import get_llm_client, generate_greeting, generate_encouragement


class TestGetLlmClient:
    @patch.dict("os.environ", {
        "DEEPSEEK_API_KEY": "test-key",
        "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
        "DEEPSEEK_MODEL": "deepseek-chat",
    })
    def test_creates_client_with_env_vars(self):
        client = get_llm_client()
        assert client is not None


class TestGenerateGreeting:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_calls_llm_and_returns_string(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "早上好！昨天休息得不错，今天精力充沛地开始吧。"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate_greeting("good", "warm", None,
                                   {"date": "2026-06-08", "sleep_score": 85, "stress_level": 2})
        assert "早上好" in result
        mock_client.chat.completions.create.assert_called_once()

    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_health_data(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "你好"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        generate_greeting("fair", "warm", None,
                          {"date": "2026-06-08", "sleep_score": 62, "stress_level": 5})

        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args.kwargs["messages"][1]["content"]
        assert "62" in prompt_content
        assert "5" in prompt_content

    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_trend_warning(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "你好"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        generate_greeting("poor", "warm", "连续三天状态偏低",
                          {"date": "2026-06-08", "sleep_score": 40, "stress_level": 8})

        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args.kwargs["messages"][1]["content"]
        assert "连续三天状态偏低" in prompt_content

    @patch("reasoning.llm_generator.get_llm_client")
    def test_fallback_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        result = generate_greeting("good", "warm", None,
                                   {"date": "2026-06-08", "sleep_score": 85, "stress_level": 2})
        assert len(result) > 0


class TestGenerateEncouragement:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_calls_llm_and_returns_string(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "慢慢来，你已经很棒了！"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = generate_encouragement("今天有点累", "fair", "warm")
        assert "慢慢来" in result

    @patch("reasoning.llm_generator.get_llm_client")
    def test_prompt_includes_user_input(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "加油"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        generate_encouragement("想休息一下", "poor", "direct")

        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args.kwargs["messages"][1]["content"]
        assert "想休息一下" in prompt_content

    @patch("reasoning.llm_generator.get_llm_client")
    def test_fallback_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        result = generate_encouragement("今天想轻松一点", "fair", "warm")
        assert len(result) > 0
