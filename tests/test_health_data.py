from perception.health_data import get_yesterday_health_data


def test_returns_dict_with_required_keys():
    data = get_yesterday_health_data()
    assert isinstance(data, dict)
    assert "date" in data
    assert "sleep_score" in data
    assert "stress_level" in data


def test_sleep_score_in_valid_range():
    data = get_yesterday_health_data()
    assert 0 <= data["sleep_score"] <= 100


def test_stress_level_in_valid_range():
    data = get_yesterday_health_data()
    assert 0 <= data["stress_level"] <= 10
