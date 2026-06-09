import json
from memory.profile_store import load_goals, save_goals, expire_old_goals, get_active_goals


class TestLoadGoals:
    def test_returns_empty_when_missing(self, tmp_path):
        path = tmp_path / "goals.json"
        assert load_goals(str(path)) == []

    def test_loads_existing(self, tmp_path):
        path = tmp_path / "goals.json"
        goals = [{"goal": "早点下班", "date": "2026-06-09", "status": "active"}]
        path.write_text(json.dumps(goals))
        assert len(load_goals(str(path))) == 1


class TestSaveGoals:
    def test_creates_file(self, tmp_path):
        path = tmp_path / "goals.json"
        goals = [{"goal": "运动30分钟", "date": "2026-06-09", "status": "active"}]
        save_goals(goals, str(path))
        loaded = json.loads(path.read_text())
        assert len(loaded) == 1

    def test_overwrites_existing(self, tmp_path):
        path = tmp_path / "goals.json"
        path.write_text(json.dumps([{"goal": "旧目标", "date": "2026-06-08", "status": "active"}]))
        save_goals([{"goal": "新目标", "date": "2026-06-09", "status": "active"}], str(path))
        loaded = json.loads(path.read_text())
        assert len(loaded) == 1
        assert loaded[0]["goal"] == "新目标"


class TestExpireOldGoals:
    def test_marks_old_active_as_expired(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-05", "status": "active"},
            {"goal": "目标B", "date": "2026-06-09", "status": "active"},
        ]
        result = expire_old_goals(goals, max_days=3, today="2026-06-09")
        assert result[0]["status"] == "expired"
        assert result[1]["status"] == "active"

    def test_does_not_expire_recent(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-08", "status": "active"},
        ]
        result = expire_old_goals(goals, max_days=3, today="2026-06-09")
        assert result[0]["status"] == "active"

    def test_already_expired_stays_expired(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-05", "status": "expired"},
        ]
        result = expire_old_goals(goals, max_days=3, today="2026-06-09")
        assert result[0]["status"] == "expired"

    def test_empty_list(self):
        assert expire_old_goals([], max_days=3, today="2026-06-09") == []


class TestGetActiveGoals:
    def test_filters_active(self):
        goals = [
            {"goal": "目标A", "date": "2026-06-08", "status": "active"},
            {"goal": "目标B", "date": "2026-06-07", "status": "done"},
            {"goal": "目标C", "date": "2026-06-09", "status": "active"},
        ]
        active = get_active_goals(goals)
        assert len(active) == 2

    def test_empty_list(self):
        assert get_active_goals([]) == []
