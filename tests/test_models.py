from src.models.subject import Subject
from src.models.session import SessionRecord


def test_subject_creation():
    s = Subject(name="Math", id=1)

    assert s.name == "Math"
    assert s.id == 1


def test_subject_repr():
    s = Subject(name="Physics", id=2)

    r = repr(s)

    assert "Physics" in r
    assert "2" in r


def test_subject_validation():
    try:
        Subject(name="   ", id=3)
        assert False, "Expected ValueError for empty subject name"
    except ValueError:
        pass


def test_session_creation():
    session = SessionRecord(
        subject_id=1,
        date="2026-02-11",
        duration_minutes=60,
        focus_level=4,
        start_time="18:30",
        test_score=80,
        notes="Good session",
        id=5,
    )

    assert session.subject_id == 1
    assert session.date == "2026-02-11"
    assert session.duration_minutes == 60
    assert session.focus_level == 4
    assert session.start_time == "18:30"
    assert session.test_score == 80
    assert session.notes == "Good session"
    assert session.id == 5


def test_session_repr():
    session = SessionRecord(
        subject_id=2,
        date="2026-02-12",
        duration_minutes=30,
        focus_level=3,
    )

    r = repr(session)

    assert "2026-02-12" in r
    assert "30" in r
    assert "3" in r
