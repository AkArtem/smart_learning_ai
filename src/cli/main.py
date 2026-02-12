import argparse
import sqlite3
from src.db.database import DatabaseManager
from src.models.session import SessionRecord

def cmd_init(args=None):
    db = DatabaseManager()
    db.migrate()
    print(f"Database initialized at {db.db_path}")

def cmd_add_subject(args):
    db = DatabaseManager()
    try:
        sid = db.add_subject(args.name)
        print(f"Subject '{args.name}' added with id={sid}")
    except sqlite3.IntegrityError:
        print(f"Subject '{args.name}' already exists")
    except ValueError as e:
        print(e)

def cmd_delete_subject(args):
    db = DatabaseManager()
    rc = db.delete_subject(args.subject_id)
    if rc > 0:
        print(f"Deleted subject id={args.subject_id} and associated sessions")
    else:
        print(f"No subject found with id={args.subject_id}")

def cmd_show_subject(args):
    db = DatabaseManager()
    subj = db.get_subject(args.subject_id)
    if subj:
        print(f"Subject id={subj.id}: {subj.name}")
    else:
        print(f"No subject found with id={args.subject_id}")

def cmd_list_subjects(args):
    db = DatabaseManager()
    subjects = db.get_subjects()
    for s in subjects:
        print(f"{s.id}: {s.name}")

def cmd_add_session(args):
    db = DatabaseManager()
    session = SessionRecord(
        subject_id=args.subject_id,
        date=args.date,
        start_time=args.start_time,
        duration_minutes=args.duration,
        focus_level=args.focus,
        test_score=args.score,
        notes=args.notes
    )
    row_id = db.add_session(session)
    print(f"Added session id={row_id}")
    
def cmd_show_session(args):
    db = DatabaseManager()
    session = db.get_session(args.session_id)
    if session:
        print(f"Session id={session.id}: Subject ID={session.subject_id}, "
              f"{session.start_time} {session.date}, {session.duration_minutes}min, "
              f"focus={session.focus_level}, score={session.test_score}, notes={session.notes}")
    else:
        print(f"No session found with id={args.session_id}")
    
def cmd_delete_session(args):
    db = DatabaseManager()
    rc = db.delete_session(args.session_id)
    if rc > 0:
        print(f"Deleted session id={args.session_id}")
    else:
        print(f"No session found with id={args.session_id}")

def cmd_list_sessions(args):
    db = DatabaseManager()
    sessions = db.list_sessions(limit=args.limit)
    for s in sessions:
        print(f"{s.id}: subject_id={s.subject_id}, {s.start_time} {s.date}, "
              f"{s.duration_minutes}min, focus={s.focus_level}, score={s.test_score}")

def main():
    parser = argparse.ArgumentParser(prog="slearn")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init")
    p_init.set_defaults(func=cmd_init)

    p_add_subj = sub.add_parser("add-subject")
    p_add_subj.add_argument("name")
    p_add_subj.set_defaults(func=cmd_add_subject)
    
    p_del_subj = sub.add_parser("delete-subject")
    p_del_subj.add_argument("subject_id", type=int)
    p_del_subj.set_defaults(func=cmd_delete_subject)
    
    p_show_subj = sub.add_parser("show-subject")
    p_show_subj.add_argument("subject_id", type=int)
    p_show_subj.set_defaults(func=cmd_show_subject)

    p_del = sub.add_parser("delete-session")
    p_del.add_argument("session_id", type=int)
    p_del.set_defaults(func=cmd_delete_session)

    p_list_subj = sub.add_parser("list-subjects")
    p_list_subj.set_defaults(func=cmd_list_subjects)

    p_add_sess = sub.add_parser("add-session")
    p_add_sess.add_argument("subject_id", type=int)
    p_add_sess.add_argument("date")  # YYYY-MM-DD
    p_add_sess.add_argument("--start-time")   # HH:MM
    p_add_sess.add_argument("--duration", type=int, required=True)
    p_add_sess.add_argument("--focus", type=int, choices=range(1,6), required=True)
    p_add_sess.add_argument("--score", type=int)
    p_add_sess.add_argument("--notes")
    p_add_sess.set_defaults(func=cmd_add_session)

    p_list_sess = sub.add_parser("list-sessions")
    p_list_sess.add_argument("--limit", type=int, default=10)
    p_list_sess.set_defaults(func=cmd_list_sessions)
    
    p_show_sess = sub.add_parser("show-session")
    p_show_sess.add_argument("session_id", type=int)
    p_show_sess.set_defaults(func=cmd_show_session)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()