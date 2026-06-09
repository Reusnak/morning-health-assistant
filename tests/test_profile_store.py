import json
import pytest
from memory.profile_store import load_profile, load_history, save_record, get_trend_warning


class TestLoadProfile:
    def test_creates_default_when_missing(self, tmp_path):
        path = tmp_path / "user_profile.json"
        profile = load_profile(str(path))
        assert profile["name"] == "用户"
        assert profile["style"] == "warm"
        assert profile["city"] == "Shenzhen"
        assert path.exists()

    def test_loads_existing(self, tmp_path):
        path = tmp_path / "user_profile.json"
        path.write_text(json.dumps({"name": "小明", "style": "direct"}))
        profile = load_profile(str(path))
        assert profile["name"] == "小明"
        assert profile["style"] == "direct"


class TestLoadHistory:
    def test_returns_empty_when_missing(self, tmp_path):
        path = tmp_path / "history.json"
        history = load_history(str(path))
        assert history == []

    def test_loads_existing(self, tmp_path):
        path = tmp_path / "history.json"
        records = [
            {"date": "2026-06-06", "status": "fair"},
            {"date": "2026-06-07", "status": "good"},
            {"date": "2026-06-08", "status": "poor"},
        ]
        path.write_text(json.dumps(records))
        history = load_history(str(path))
        assert len(history) == 3

    def test_limits_to_n_days(self, tmp_path):
        path = tmp_path / "history.json"
        records = [{"date": f"2026-06-0{i}", "status": "fair"} for i in range(1, 6)]
        path.write_text(json.dumps(records))
        history = load_history(str(path), days=3)
        assert len(history) == 3


class TestSaveRecord:
    def test_appends_to_existing(self, tmp_path):
        path = tmp_path / "history.json"
        path.write_text(json.dumps([{"date": "2026-06-07", "status": "good"}]))
        save_record({"date": "2026-06-08", "status": "poor"}, str(path))
        records = json.loads(path.read_text())
        assert len(records) == 2
        assert records[-1]["status"] == "poor"

    def test_creates_file_when_missing(self, tmp_path):
        path = tmp_path / "history.json"
        save_record({"date": "2026-06-08", "status": "fair"}, str(path))
        records = json.loads(path.read_text())
        assert len(records) == 1


class TestGetTrendWarning:
    def test_no_warning_when_fewer_than_3(self):
        history = [
            {"status": "poor"},
            {"status": "poor"},
        ]
        assert get_trend_warning(history, "warm") is None

    def test_warning_when_3_consecutive_poor(self):
        history = [
            {"status": "poor"},
            {"status": "poor"},
            {"status": "poor"},
        ]
        result = get_trend_warning(history, "warm")
        assert "温柔" in result

    def test_warning_direct_style(self):
        history = [
            {"status": "poor"},
            {"status": "poor"},
            {"status": "poor"},
        ]
        result = get_trend_warning(history, "direct")
        assert "调整节奏" in result

    def test_no_warning_when_not_all_poor(self):
        history = [
            {"status": "fair"},
            {"status": "poor"},
            {"status": "poor"},
        ]
        assert get_trend_warning(history, "warm") is None

    def test_no_warning_when_empty(self):
        assert get_trend_warning([], "warm") is None
