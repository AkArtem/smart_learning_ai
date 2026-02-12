import argparse
import sqlite3
from src.db.database import DatabaseManager
from src.models.session import SessionRecord

def cmd_init():
    db = DatabaseManager()
    db.migrate()
    print(f"Database initialized at {db.db_path}")

def cmd_add_subject(args):
    db = DatabaseManager()
    conn = db._connect()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (args.name,))
        conn.commit()
        print(f"Subject '{args.name}' added with id={cur.lastrowid}")
    except sqlite3.IntegrityError:
        print(f"Subject '{args.name}' already exists")
    finally:
        conn.close()

def cmd_delete_subject(args):
    db = DatabaseManager()
    conn = db._connect()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM subjects WHERE id = ?", (args.subject_id,))
        if cur.rowcount > 0:
            print(f"Deleted subject id={args.subject_id} and associated sessions")
        else:
            print(f"No subject found with id={args.subject_id}")
        conn.commit()
    finally:
        conn.close()

def cmd_show_subject(args):
    db = DatabaseManager()
    conn = db._connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM subjects WHERE id = ?", (args.subject_id,))
        row = cur.fetchone()
        if row:
            print(f"Subject id={row['id']}: {row['name']}")
        else:
            print(f"No subject found with id={args.subject_id}")
    finally:
        conn.close()

def cmd_list_subjects(args):
    db = DatabaseManager()
    conn = db._connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM subjects ORDER BY name")
        rows = cur.fetchall()
        for row in rows:
            print(f"{row['id']}: {row['name']}")
    finally:
        conn.close()

def cmd_list_subjects(args):
    db = DatabaseManager()
    conn = db._connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM subjects ORDER BY name")
        rows = cur.fetchall()
        for row in rows:
            print(f"{row['id']}: {row['name']}")
    finally:
        conn.close()

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
        print(f"Session id={session.id}: subject_id={session.subject_id}, "
              f"{session.start_time} {session.date}, {session.duration_minutes}min, "
              f"focus={session.focus_level}, score={session.test_score}, notes={session.notes}")
    else:
        print(f"No session found with id={args.session_id}")
    
def cmd_delete_session(args):
    db = DatabaseManager()
    conn = db._connect()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM learning_sessions WHERE id = ?", (args.session_id,))
        if cur.rowcount > 0:
            print(f"Deleted session id={args.session_id}")
        else:
            print(f"No session found with id={args.session_id}")
        conn.commit()
    finally:
        conn.close()

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