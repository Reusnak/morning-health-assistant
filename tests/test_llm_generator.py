from unittest.mock import patch, MagicMock
from reasoning.llm_generator import get_llm_client, generate_greeting, chat_turn, extract_goals


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



class TestChatTurn:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_reply_with_context(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "听起来不错！那今天有什么具体计划吗？"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        messages = [
            {"role": "system", "content": "你是晨间助手"},
            {"role": "assistant", "content": "早上好！"},
            {"role": "user", "content": "今天想轻松一点"},
        ]
        result = chat_turn(messages, "fair", "warm")
        assert "听起来" in result
        mock_client.chat.completions.create.assert_called_once()

    @patch("reasoning.llm_generator.get_llm_client")
    def test_fallback_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        messages = [
            {"role": "system", "content": "你是晨间助手"},
            {"role": "assistant", "content": "早上好！"},
            {"role": "user", "content": "今天想轻松一点"},
        ]
        result = chat_turn(messages, "fair", "warm")
        assert len(result) > 0


class TestExtractGoals:
    @patch("reasoning.llm_generator.get_llm_client")
    def test_extracts_goals_from_conversation(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["早点下班", "做顿好吃的"]'
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        conversation = "助手：早上好！\n用户：想早点下班，回家做顿好吃的。"
        result = extract_goals(conversation)
        assert result == ["早点下班", "做顿好吃的"]

    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_empty_when_no_goals(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "[]"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = extract_goals("助手：早上好！\n用户：没什么特别的。")
        assert result == []

    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_empty_on_parse_failure(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这不是JSON"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = extract_goals("助手：早上好！\n用户：随便聊聊。")
        assert result == []

    @patch("reasoning.llm_generator.get_llm_client")
    def test_returns_empty_on_api_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client

        result = extract_goals("对话内容")
        assert result == []
