import pytest
from reasoning.status_evaluator import calculate_composite_score, evaluate_status


class TestCalculateCompositeScore:
    def test_perfect_score(self):
        assert calculate_composite_score(100, 0) == 100.0

    def test_worst_score(self):
        assert calculate_composite_score(0, 10) == 0.0

    def test_moderate_values(self):
        # 62 * 0.6 + (10 - 5) * 4 = 37.2 + 20 = 57.2
        assert calculate_composite_score(62, 5) == pytest.approx(57.2)

    def test_high_sleep_high_stress(self):
        # 90 * 0.6 + (10 - 8) * 4 = 54 + 8 = 62
        assert calculate_composite_score(90, 8) == pytest.approx(62.0)


class TestEvaluateStatus:
    def test_good_threshold(self):
        # 75 * 0.6 + (10 - 0) * 4 = 45 + 40 = 85
        assert evaluate_status(85.0) == "good"

    def test_good_boundary(self):
        assert evaluate_status(75.0) == "good"

    def test_fair(self):
        assert evaluate_status(57.2) == "fair"

    def test_fair_boundary_low(self):
        assert evaluate_status(50.0) == "fair"

    def test_poor(self):
        assert evaluate_status(30.0) == "poor"

    def test_poor_boundary(self):
        assert evaluate_status(49.9) == "poor"


from reasoning.status_evaluator import generate_greeting, generate_encouragement


class TestGenerateGreeting:
    def test_warm_good(self):
        result = generate_greeting("good", "warm", None)
        assert "早上好" in result
        assert "顺其自然" in result

    def test_warm_fair(self):
        result = generate_greeting("fair", "warm", None)
        assert "早上好" in result
        assert "小事" in result

    def test_warm_poor(self):
        result = generate_greeting("poor", "warm", None)
        assert "早上好" in result
        assert "照顾好自己" in result

    def test_direct_good(self):
        result = generate_greeting("good", "direct", None)
        assert "轻松推进" in result

    def test_direct_fair(self):
        result = generate_greeting("fair", "direct", None)
        assert "小事" in result

    def test_direct_poor(self):
        result = generate_greeting("poor", "direct", None)
        assert "优先休息" in result

    def test_with_trend_warning(self):
        result = generate_greeting("poor", "warm", "注意到你最近几天都没怎么休息好，要对自己温柔一点哦。")
        assert result.startswith("注意到你最近")
        assert "照顾好自己" in result

    def test_no_trend_warning(self):
        result = generate_greeting("good", "warm", None)
        assert not result.startswith("注意到")


class TestGenerateEncouragement:
    def test_warm_good(self):
        result = generate_encouragement("今天想轻松一点", "good", "warm")
        assert len(result) > 0

    def test_warm_poor(self):
        result = generate_encouragement("只想休息", "poor", "warm")
        assert len(result) > 0

    def test_direct_good(self):
        result = generate_encouragement("继续推进项目", "good", "direct")
        assert len(result) > 0

    def test_direct_poor(self):
        result = generate_encouragement("什么都不想做", "poor", "direct")
        assert len(result) > 0
