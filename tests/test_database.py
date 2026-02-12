import os
import tempfile

from src.db.database import DatabaseManager
from src.models.session import SessionRecord

def create_test_db():
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    db = DatabaseManager(db_path=temp.name)
    db.migrate()
    return db, temp.name

def test_database_init():
    db, path = create_test_db()
    assert os.path.exists(path)
    os.remove(path)

def test_add_subject():
    db, path = create_test_db()
    subject_id = db.add_subject("Math")
    assert subject_id == 1

    subjects = db.get_subjects()
    assert len(subjects) == 1
    assert subjects[0].name == "Math"
    os.remove(path)

def test_add_session():
    db, path = create_test_db()
    db.add_subject("Physics")

    session = SessionRecord(
        subject_id=1,
        date="2026-02-11",
        duration_minutes=60,
        focus_level=4,
        start_time="18:30",
        test_score=90,
        notes="Nice",
    )

    session_id = db.add_session(session)
    assert session_id == 1

    sessions = db.get_sessions()
    assert len(sessions) == 1

    s = sessions[0]

    assert s.subject_id == 1
    assert s.date == "2026-02-11"
    assert s.duration_minutes == 60
    assert s.focus_level == 4
    os.remove(path)

def test_get_single_session():
    db, path = create_test_db()
    db.add_subject("AI")
    session = SessionRecord(
        subject_id=1,
        date="2026-02-12",
        duration_minutes=45,
        focus_level=5,
    )

    sid = db.add_session(session)
    loaded = db.get_session(sid)
    
    assert loaded is not None
    assert loaded.id == sid
    assert loaded.focus_level == 5
    os.remove(path)

def test_delete_subject():
    db, path = create_test_db()

    sid = db.add_subject("Biology")
    assert sid == 1

    rc = db.delete_subject(sid)
    assert rc == 1

    subs = db.get_subjects()
    assert len(subs) == 0

    os.remove(path)

def test_delete_session():
    db, path = create_test_db()

    db.add_subject("Chemistry")

    session = SessionRecord(
        subject_id=1,
        date="2026-02-13",
        duration_minutes=30,
        focus_level=3,
    )

    sid = db.add_session(session)
    assert sid == 1

    rc = db.delete_session(sid)
    assert rc == 1

    loaded = db.get_session(sid)
    assert loaded is None

    os.remove(path)