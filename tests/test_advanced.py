from src.db.database import DatabaseManager
from src.models.session import SessionRecord
from src.analytics import analytics


def _make_db(path):
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


def test_longest_streak_and_growth(tmp_path):
    db_file = tmp_path / "adv.sqlite"
    _make_db(str(db_file))
    df = analytics.df_from_db(db_path=str(db_file))
    assert analytics.longest_streak(df) >= 1
    gr = analytics.growth_rate(df)
    assert (gr is None) or isinstance(gr, float)


def test_focus_corr_and_recs(tmp_path):
    db_file = tmp_path / "adv2.sqlite"
    _make_db(str(db_file))
    df = analytics.df_from_db(db_path=str(db_file))
    corr = analytics.focus_score_corr(df)
    assert corr is not None
    recs = analytics.recommendations(df)
    assert isinstance(recs, list)
