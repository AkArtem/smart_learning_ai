from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
from src.analytics.analytics import (
    df_from_db,
    compute_overall_summary,
    subject_stats,
)


@dataclass
class Recommendation:
    category: str
    title: str
    advice: str
    priority: int


class RecommendationEngine:
    def __init__(self, db_path=None):
        self.df = df_from_db(db_path=db_path)
        self.recommendations = []

    def analyze(self):
        if self.df.empty:
            return []

        self.recommendations = []
        self._check_low_focus()
        self._check_weak_subjects()
        self._check_burnout()
        self._check_schedule()
        self.recommendations.sort(key=lambda x: x.priority)
        return self.recommendations

    def _check_low_focus(self):
        avg_focus = self.df["focus_level"].mean()
        if avg_focus < 2.5:
            self.recommendations.append(
                Recommendation(
                    category="focus",
                    title="Low Focus Detected",
                    advice="Your focus is low. Try shorter sessions (25-30 min) with breaks.",
                    priority=1,
                )
            )
        elif avg_focus < 3:
            self.recommendations.append(
                Recommendation(
                    category="focus",
                    title="Focus Could Be Better",
                    advice="Moderate focus. Consider 40-min sessions with 10-min breaks.",
                    priority=2,
                )
            )

    def _check_weak_subjects(self):
        stats = subject_stats(self.df)
        for subject, row in stats.iterrows():
            avg_score = row["avg_score"]
            sessions = row["sessions"]
            if sessions >= 2 and pd.notna(avg_score) and avg_score < 60:
                self.recommendations.append(
                    Recommendation(
                        category="subject",
                        title=f"Boost {subject}",
                        advice=f"Your score in {subject} is low ({avg_score:.0f}%). Try 2-3 focused sessions this week.",
                        priority=1,
                    )
                )

    def _check_burnout(self):
        weekly = self.df.groupby("date").size()
        if len(weekly) >= 2:
            recent_days = weekly.iloc[-7:].sum()
            prev_days = weekly.iloc[-14:-7].sum()
            if recent_days == 0:
                self.recommendations.append(
                    Recommendation(
                        category="burnout",
                        title="Time to Rest",
                        advice="You haven't studied recently. Take a break, then restart fresh!",
                        priority=1,
                    )
                )
            elif prev_days > 0 and recent_days < (prev_days * 0.5):
                self.recommendations.append(
                    Recommendation(
                        category="burnout",
                        title="Burnout Alert",
                        advice="Your study activity is dropping. Time for a rest day!",
                        priority=1,
                    )
                )
        if len(self.df) >= 3:
            recent_avg = self.df.iloc[-3:]["duration_minutes"].mean()
            prev_avg = self.df.iloc[-10:-3]["duration_minutes"].mean() if len(self.df) >= 10 else recent_avg
            if recent_avg < (prev_avg * 0.5) and prev_avg > 0:
                self.recommendations.append(
                    Recommendation(
                        category="burnout",
                        title="Energy Low",
                        advice="Sessions are getting shorter. Get rest and hydrate!",
                        priority=2,
                    )
                )

    def _check_schedule(self):
        summary = compute_overall_summary(self.df)
        if summary["total_sessions"] > 0:
            sessions_per_day = summary["total_sessions"] / max(len(set(self.df["date"])), 1)
            if sessions_per_day < 1:
                self.recommendations.append(
                    Recommendation(
                        category="schedule",
                        title="Build Daily Habit",
                        advice="Aim for at least 1 study session per day.",
                        priority=2,
                    )
                )

    def generate_daily_plan(self, date_str=None):
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        summary = compute_overall_summary(self.df)
        weak_subjects = subject_stats(self.df).sort_values("avg_score").index.tolist()[:3]
        plan = {"date": date_str, "sessions": [], "total_time": 0}
        session_time = 25 if summary["avg_focus"] and summary["avg_focus"] < 2.5 else 40
        times = ["09:00", "14:00", "18:00"]
        for i, subject in enumerate(weak_subjects[:3]):
            plan["sessions"].append({
                "time": times[i],
                "subject": subject,
                "duration": session_time,
                "break_after": 10,
            })
            plan["total_time"] += session_time
        return plan

    def generate_weekly_plan(self):
        stats = subject_stats(self.df)
        plan = {"week": datetime.now().strftime("%Y-W%W"), "daily_target": 90, "subjects": []}
        if not stats.empty:
            for subject in stats.index[:5]:
                plan["subjects"].append({
                    "subject": subject,
                    "sessions": 3,
                    "total_minutes": 120,
                })
        return plan

    def get_text_advice(self):
        self.analyze()
        if not self.recommendations:
            return "All good! Keep up the learning!"
        text = "Recommendations:\n" + "=" * 40 + "\n\n"
        for rec in self.recommendations:
            text += f"[{rec.priority}] {rec.title}\n  {rec.advice}\n\n"
        return text

    def get_dashboard(self):
        summary = compute_overall_summary(self.df)
        self.analyze()
        dashboard = {
            "metrics": {
                "focus_level": summary["avg_focus"],
                "avg_score": summary["avg_score"],
                "study_consistency": len(set(self.df["date"])),
                "recommendation_count": len(self.recommendations),
            },
            "top_subjects": summary["sessions_per_subject"].head(5).to_dict(),
            "recommendations_by_priority": {
                "high": [r for r in self.recommendations if r.priority == 1],
                "medium": [r for r in self.recommendations if r.priority == 2],
                "low": [r for r in self.recommendations if r.priority == 3],
            },
            "status": self._get_status(),
        }
        return dashboard

    def _get_status(self):
        self.analyze()
        high_priority = [r for r in self.recommendations if r.priority == 1]
        if not high_priority:
            return "On Track"
        elif len(high_priority) <= 2:
            return "Needs Attention"
        else:
            return "Action Required"


def print_recommendation_summary(engine):
    print(engine.get_text_advice())
    print("\nDaily Plan for Today:")
    daily = engine.generate_daily_plan()
    for session in daily["sessions"]:
        print(f"  {session['time']} - {session['subject']} ({session['duration']} min)")