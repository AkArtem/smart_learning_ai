import pandas as pd
from src.db.database import DatabaseManager


def df_from_db(db_path=None):
    db = DatabaseManager(db_path=db_path)
    conn = db._connect()
    try:
        query = """
        SELECT ls.id AS session_id, s.id AS subject_id, s.name AS subject_name,
               ls.start_timestamp, ls.duration_minutes, ls.focus_level, ls.test_score, ls.notes
        FROM learning_sessions ls
        JOIN subjects s ON ls.subject_id = s.id
        """
        df = pd.read_sql_query(query, conn, parse_dates=["start_timestamp"]) 
        if df.empty:
            return df
        df["date"] = df["start_timestamp"].dt.date
        df["week_start"] = (
            df["start_timestamp"] - pd.to_timedelta(df["start_timestamp"].dt.weekday, unit="d")
        ).dt.normalize()
        return df
    finally:
        conn.close()


def compute_overall_summary(df):
    total_sessions = len(df)
    total_minutes = int(df["duration_minutes"].sum()) if total_sessions > 0 else 0
    avg_focus = float(df["focus_level"].mean()) if total_sessions > 0 else None
    avg_score = float(df["test_score"].dropna().mean()) if "test_score" in df and df["test_score"].notna().any() else None
    sessions_per_subject = df.groupby("subject_name").size().sort_values(ascending=False)
    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "avg_focus": avg_focus,
        "avg_score": avg_score,
        "sessions_per_subject": sessions_per_subject,
    }


def subject_stats(df):
    return df.groupby("subject_name").agg(
        sessions=("session_id", "count"),
        total_minutes=("duration_minutes", "sum"),
        avg_focus=("focus_level", "mean"),
        avg_score=("test_score", "mean"),
    )


def weekly_minutes(df):
    if df.empty:
        return pd.Series(dtype="int")
    s = df.set_index("start_timestamp").resample("W")["duration_minutes"].sum().sort_index()
    return s


def top_subjects(df, n=5):
    return df.groupby("subject_name")["duration_minutes"].sum().sort_values(ascending=False).head(n)

def missing_report(df):
    return df.isna().sum()


def productivity_index(df):
    return (df["focus_level"] * df["duration_minutes"]).mean()

def best_hour(df):
    try:
        return int(df["start_timestamp"].dt.hour.mode()[0])
    except Exception:
        return None


def best_weekday(df):
    try:
        return str(df["start_timestamp"].dt.day_name().mode()[0])
    except Exception:
        return None


def weakest_subject(df):
    if df.empty or "test_score" not in df or df["test_score"].dropna().empty:
        return None
    return df.groupby("subject_name")["test_score"].mean().idxmin()


def focus_trend(df):
    if df.empty:
        return pd.Series(dtype="float")
    return df.set_index("start_timestamp").resample("M")["focus_level"].mean()


def most_productive_subject(df):
    s = (df["focus_level"] * df["duration_minutes"]).groupby(df["subject_name"]).sum()
    if s.empty:
        return None
    return s.idxmax()