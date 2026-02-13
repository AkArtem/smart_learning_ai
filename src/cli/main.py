import argparse
import sqlite3
import os
from src.db.database import DatabaseManager
from src.models.session import SessionRecord
from src.analytics import analytics
from src import visualization

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

    p_analytics = sub.add_parser("analytics-summary")
    p_analytics.set_defaults(func=cmd_analytics_summary)

    p_plot = sub.add_parser("analytics-plot")
    p_plot.add_argument("--chart", choices=["sessions_over_time", "focus_dist", "subject_breakdown", "all"], default="all")
    p_plot.add_argument("--out-dir", default="data/plots")
    p_plot.set_defaults(func=cmd_analytics_plot)

    p_quality = sub.add_parser("analytics-quality")
    p_quality.set_defaults(func=cmd_analytics_quality)

    p_dashboard = sub.add_parser("analytics-dashboard")
    p_dashboard.add_argument("--out-dir", default="data/plots")
    p_dashboard.set_defaults(func=cmd_analytics_dashboard)

    p_insights = sub.add_parser("analytics-insights")
    p_insights.set_defaults(func=cmd_analytics_insights)

    p_report = sub.add_parser("analytics-report")
    p_report.add_argument("--out-dir", default="data/exports")
    p_report.set_defaults(func=cmd_analytics_report)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


def cmd_analytics_summary(args):
    df = analytics.df_from_db()
    summary = analytics.compute_overall_summary(df)
    print(f"Total sessions: {summary['total_sessions']}")
    print(f"Total minutes: {summary['total_minutes']}")
    print(f"Average focus: {summary['avg_focus']}")
    print(f"Average score: {summary['avg_score']}")
    print("Sessions per subject:")
    for subj, cnt in summary['sessions_per_subject'].items():
        print(f"  {subj}: {cnt}")


def cmd_analytics_plot(args):
    df = analytics.df_from_db()
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    charts = []
    if args.chart in ("sessions_over_time", "all"):
        fig = visualization.plot_sessions_over_time(df)
        path = os.path.join(out_dir, "sessions_over_time.png")
        fig.savefig(path)
        charts.append(path)
    if args.chart in ("focus_dist", "all"):
        fig = visualization.plot_focus_distribution(df)
        path = os.path.join(out_dir, "focus_distribution.png")
        fig.savefig(path)
        charts.append(path)
    if args.chart in ("subject_breakdown", "all"):
        fig = visualization.plot_subject_breakdown(df)
        path = os.path.join(out_dir, "subject_breakdown.png")
        fig.savefig(path)
        charts.append(path)
    if charts:
        print("Saved charts:")
        for p in charts:
            print(f"  {p}")
    else:
        print("No charts generated")


def cmd_analytics_quality(args):
    df = analytics.df_from_db()
    miss = analytics.missing_report(df)
    for col, cnt in miss.items():
        if int(cnt) > 0:
            print(f"{col}: {int(cnt)} missing")


def cmd_analytics_dashboard(args):
    df = analytics.df_from_db()
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    fig = visualization.plot_dashboard(df)
    path = os.path.join(out_dir, "dashboard.png")
    fig.savefig(path)
    print(f"Saved dashboard: {path}")


def cmd_analytics_insights(args):
    df = analytics.df_from_db()
    best = analytics.best_hour(df)
    prod = analytics.most_productive_subject(df)
    weak = analytics.weakest_subject(df)
    pidx = analytics.productivity_index(df)

    print("Learning Insights")
    print("-----------------")
    print(f"Best study hour: {best}")
    print(f"Most productive subject: {prod}")
    print(f"Weakest subject: {weak}")
    print(f"Productivity index: {round(pidx,2) if pidx is not None else 'n/a'}")


def cmd_analytics_report(args):
    df = analytics.df_from_db()
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    total_minutes = analytics.compute_overall_summary(df)["total_minutes"]
    best = analytics.best_hour(df)
    weak = analytics.weakest_subject(df)
    prod = analytics.most_productive_subject(df)

    path = os.path.join(out_dir, "report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("Learning Summary\n")
        f.write("----------------\n")
        f.write(f"Total time: {total_minutes//60}h {total_minutes%60}min\n")
        f.write(f"Best hour: {best}\n")
        f.write(f"Most productive subject: {prod}\n")
        f.write(f"Weakest subject: {weak}\n")
    print(f"Exported report: {path}")

if __name__ == "__main__":
    main()