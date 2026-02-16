import pytest
from src.recommender.recommender import RecommendationEngine, Recommendation
from src.db.database import DatabaseManager
from src.models.subject import Subject
from src.models.session import SessionRecord
from datetime import datetime, timedelta


@pytest.fixture
def test_db_path(tmp_path):
    return str(tmp_path / "test_recommend.db")


@pytest.fixture
def engine_with_data(test_db_path):
    db = DatabaseManager(db_path=test_db_path)
    db.migrate()

    db.add_subject("Math")
    db.add_subject("History")
    db.add_subject("English")

    conn = db._connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects")
    subjects = {name: id for id, name in cursor.fetchall()}
    conn.close()

    today = datetime.now()
    for i in range(10):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")

        session = SessionRecord(
            subject_id=subjects["Math"],
            date=date,
            duration_minutes=30,
            focus_level=1,
            test_score=45,
        )
        db.add_session(session)

        session = SessionRecord(
            subject_id=subjects["History"],
            date=date,
            duration_minutes=45,
            focus_level=2,
            test_score=85,
        )
        db.add_session(session)

    engine = RecommendationEngine(db_path=test_db_path)
    return engine


def test_low_focus_detection(engine_with_data):
    recs = engine_with_data.analyze()
    focus_recs = [r for r in recs if r.category == "focus"]
    assert len(focus_recs) > 0
    assert "Low Focus" in focus_recs[0].title


def test_weak_subject_detection(engine_with_data):
    recs = engine_with_data.analyze()
    subject_recs = [r for r in recs if r.category == "subject"]
    assert len(subject_recs) > 0
    assert "Math" in subject_recs[0].advice or "Boost" in subject_recs[0].title


def test_recommendations_have_priority(engine_with_data):
    recs = engine_with_data.analyze()
    for rec in recs:
        assert rec.priority in [1, 2, 3]


def test_text_advice_output(engine_with_data):
    text = engine_with_data.get_text_advice()
    assert isinstance(text, str)
    assert len(text) > 0
    assert "Recommendations" in text or "All good" in text

def test_daily_plan_generation(engine_with_data):
    plan = engine_with_data.generate_daily_plan()
    assert isinstance(plan, dict)
    assert "date" in plan
    assert "sessions" in plan
    assert "total_time" in plan
    assert isinstance(plan["sessions"], list)


def test_weekly_plan_generation(engine_with_data):
    """Test weekly plan generation"""
    plan = engine_with_data.generate_weekly_plan()
    assert isinstance(plan, dict)
    assert "week" in plan
    assert "subjects" in plan
    assert "daily_target" in plan


def test_dashboard_output(engine_with_data):
    dashboard = engine_with_data.get_dashboard()
    assert isinstance(dashboard, dict)
    assert "metrics" in dashboard
    assert "top_subjects" in dashboard
    assert "recommendations_by_priority" in dashboard
    assert "status" in dashboard


def test_empty_no_crash(tmp_path):
    db_path = str(tmp_path / "empty.db")
    db = DatabaseManager(db_path=db_path)
    db.migrate()

    engine = RecommendationEngine(db_path=db_path)
    text = engine.get_text_advice()
    assert isinstance(text, str)
    assert len(text) > 0
