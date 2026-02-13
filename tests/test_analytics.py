from src.db.database import DatabaseManager
from src.models.session import SessionRecord
from src.analytics import analytics


def _make_sample_db(path):
    db = DatabaseManager(db_path=path)
    db.migrate()
    math_id = db.add_subject("Math")
    hist_id = db.add_subject("History")

    s1 = SessionRecord(subject_id=math_id, date="2026-02-01", start_time="09:00", duration_minutes=60, focus_level=4, test_score=85)
    s2 = SessionRecord(subject_id=math_id, date="2026-02-03", start_time="10:00", duration_minutes=45, focus_level=3, test_score=78)
    s3 = SessionRecord(subject_id=hist_id, date="2026-02-02", start_time="08:30", duration_minutes=30, focus_level=5, test_score=92)

    db.add_session(s1)
    db.add_session(s2)
    db.add_session(s3)
    return db


def test_compute_overall_summary(tmp_path):
    db_file = tmp_path / "test_db.sqlite"
    _make_sample_db(str(db_file))
    df = analytics.df_from_db(db_path=str(db_file))
    summary = analytics.compute_overall_summary(df)

    assert summary["total_sessions"] == 3
    assert summary["total_minutes"] == 135
    assert round(summary["avg_focus"], 2) == round((4 + 3 + 5) / 3, 2)
    assert "Math" in summary["sessions_per_subject"].index


def test_subject_stats(tmp_path):
    db_file = tmp_path / "test_db2.sqlite"
    _make_sample_db(str(db_file))
    df = analytics.df_from_db(db_path=str(db_file))
    stats = analytics.subject_stats(df)
    assert stats.loc["Math", "sessions"] == 2
    assert stats.loc["History", "sessions"] == 1