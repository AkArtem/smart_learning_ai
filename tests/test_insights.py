from src.db.database import DatabaseManager
from src.models.session import SessionRecord
from src.analytics import analytics


def _make_sample_db(path):
    db = DatabaseManager(db_path=path)
    db.migrate()
    a = db.add_subject("Math")
    b = db.add_subject("History")

    s1 = SessionRecord(subject_id=a, date="2026-02-01", start_time="09:00", duration_minutes=60, focus_level=5, test_score=90)
    s2 = SessionRecord(subject_id=a, date="2026-02-02", start_time="09:00", duration_minutes=30, focus_level=4, test_score=85)
    s3 = SessionRecord(subject_id=b, date="2026-02-03", start_time="19:00", duration_minutes=45, focus_level=2, test_score=60)

    db.add_session(s1)
    db.add_session(s2)
    db.add_session(s3)
    return db


def test_best_hour_and_weakest_and_productivity(tmp_path):
    db_file = tmp_path / "insights_db.sqlite"
    _make_sample_db(str(db_file))
    df = analytics.df_from_db(db_path=str(db_file))

    assert analytics.best_hour(df) == 9
    assert analytics.weakest_subject(df) == "History"
    pidx = analytics.productivity_index(df)
    assert round(pidx, 2) == round(((5*60) + (4*30) + (2*45))/3, 2)


def test_focus_trend_empty_and_single(tmp_path):
    # empty df
    db_file = tmp_path / "empty_db.sqlite"
    db = DatabaseManager(db_path=str(db_file))
    db.migrate()
    df = analytics.df_from_db(db_path=str(db_file))
    trend = analytics.focus_trend(df)
    assert trend.empty

    # one session
    db2_file = tmp_path / "one_db.sqlite"
    db2 = DatabaseManager(db_path=str(db2_file))
    db2.migrate()
    sid = db2.add_subject("Solo")
    s = SessionRecord(subject_id=sid, date="2026-02-05", start_time="10:00", duration_minutes=30, focus_level=4)
    db2.add_session(s)
    df2 = analytics.df_from_db(db_path=str(db2_file))
    trend2 = analytics.focus_trend(df2)
    assert not trend2.empty