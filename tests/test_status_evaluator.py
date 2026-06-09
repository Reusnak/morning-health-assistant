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
