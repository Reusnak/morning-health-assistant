from action.console import print_colored, display_greeting, ask_question, display_encouragement


class TestPrintColored:
    def test_outputs_text(self, capsys):
        print_colored("hello", "green")
        captured = capsys.readouterr()
        assert "hello" in captured.out


class TestDisplayGreeting:
    def test_outputs_greeting(self, capsys):
        display_greeting("早上好呀～")
        captured = capsys.readouterr()
        assert "早上好呀～" in captured.out


class TestAskQuestion:
    def test_returns_user_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "今天想轻松一点")
        result = ask_question("你的回答：")
        assert result == "今天想轻松一点"


class TestDisplayEncouragement:
    def test_outputs_encouragement(self, capsys):
        display_encouragement("慢慢来～")
        captured = capsys.readouterr()
        assert "慢慢来" in captured.out
