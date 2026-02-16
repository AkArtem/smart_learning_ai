import argparse
import sqlite3
import os
from src.db.database import DatabaseManager
from src.models.session import SessionRecord
from src.analytics import analytics
from src import visualization
import pandas as pd
from sklearn.model_selection import train_test_split
from src.ml import preprocessing, features, train, model, predict
from src.recommender.recommender import RecommendationEngine, print_recommendation_summary


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

    p_streak = sub.add_parser("analytics-streak")
    p_streak.set_defaults(func=cmd_analytics_streak)

    p_focus_plot = sub.add_parser("analytics-plot-focus-trend")
    p_focus_plot.add_argument("--out-dir", default="data/plots")
    p_focus_plot.set_defaults(func=cmd_analytics_plot_focus)

    p_best_hours = sub.add_parser("analytics-best-hours")
    p_best_hours.add_argument("--out-dir", default="data/plots")
    p_best_hours.set_defaults(func=cmd_analytics_best_hours)

    p_rolling = sub.add_parser("analytics-rolling")
    p_rolling.set_defaults(func=cmd_analytics_rolling)

    p_growth = sub.add_parser("analytics-growth-rate")
    p_growth.set_defaults(func=cmd_analytics_growth)

    p_corr = sub.add_parser("analytics-focus-corr")
    p_corr.set_defaults(func=cmd_analytics_corr)

    p_recs = sub.add_parser("analytics-recommendations")
    p_recs.set_defaults(func=cmd_analytics_recommendations)

    p_daily_plan = sub.add_parser("recommend-daily-plan")
    p_daily_plan.add_argument("--date", default=None, help="YYYY-MM-DD, default today")
    p_daily_plan.set_defaults(func=cmd_recommend_daily_plan)

    p_weekly_plan = sub.add_parser("recommend-weekly-plan")
    p_weekly_plan.set_defaults(func=cmd_recommend_weekly_plan)

    p_rec_dashboard = sub.add_parser("recommend-dashboard")
    p_rec_dashboard.set_defaults(func=cmd_recommend_dashboard)

    p_all = sub.add_parser("analytics-all-plots")
    p_all.add_argument("--out-dir", default="data/plots")
    p_all.set_defaults(func=cmd_analytics_all_plots)

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

    #ML Commands
    p_ml_train = sub.add_parser("ml-train")
    p_ml_train.set_defaults(func=cmd_ml_train)
    
    p_ml_predict = sub.add_parser("ml-predict")
    p_ml_predict.add_argument("--model", dest='model_name', default='RandomForest')
    p_ml_predict.set_defaults(func=cmd_ml_predict)
    
    p_ml_eval = sub.add_parser("ml-evaluate")
    p_ml_eval.set_defaults(func=cmd_ml_evaluate)
    
    p_ml_list = sub.add_parser("ml-list-models")
    p_ml_list.set_defaults(func=cmd_ml_list_models)
    
    p_ml_delete = sub.add_parser("ml-delete-model")
    p_ml_delete.add_argument("model_name")
    p_ml_delete.set_defaults(func=cmd_ml_delete_model)
    
    p_ml_ensemble = sub.add_parser("ml-ensemble-predict")
    p_ml_ensemble.add_argument("--models", default='LinearRegression,RandomForest,GradientBoosting')
    p_ml_ensemble.add_argument("--method", choices=['average', 'median'], default='average')
    p_ml_ensemble.set_defaults(func=cmd_ml_ensemble_predict)
    
    p_ml_info = sub.add_parser("ml-info")
    p_ml_info.add_argument("model_name")
    p_ml_info.set_defaults(func=cmd_ml_info)

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


def cmd_analytics_streak(args):
    df = analytics.df_from_db()
    s = analytics.longest_streak(df)
    print(f"Longest streak: {s} days")


def cmd_analytics_plot_focus(args):
    df = analytics.df_from_db()
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    fig = visualization.plot_focus_trend(df)
    path = os.path.join(out_dir, "focus_trend.png")
    fig.savefig(path)
    print(f"Saved focus trend: {path}")


def cmd_analytics_best_hours(args):
    df = analytics.df_from_db()
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    fig = visualization.plot_best_hours(df)
    path = os.path.join(out_dir, "best_hours.png")
    fig.savefig(path)
    print(f"Saved best hours: {path}")


def cmd_analytics_rolling(args):
    df = analytics.df_from_db()
    r = analytics.rolling_minutes(df)
    print(r.tail(10))


def cmd_analytics_growth(args):
    df = analytics.df_from_db()
    gr = analytics.growth_rate(df)
    print(f"Growth rate (last week vs prev): {gr}")


def cmd_analytics_corr(args):
    df = analytics.df_from_db()
    c = analytics.focus_score_corr(df)
    print(f"Focus/test_score correlation: {c}")


def cmd_analytics_recommendations(args):
    engine = RecommendationEngine()
    print(engine.get_text_advice())


def cmd_recommend_daily_plan(args):
    engine = RecommendationEngine()
    plan = engine.generate_daily_plan(args.date)
    
    print(f"Daily Plan - {plan['date']}")
    print("=" * 40)
    for session in plan["sessions"]:
        print(f"\n{session['time']}")
        print(f"  Subject: {session['subject']}")
        print(f"  Duration: {session['duration']} minutes")
        print(f"  Break after: {session['break_after']} minutes")
    print(f"\nTotal: {plan['total_time']} minutes")


def cmd_recommend_weekly_plan(args):
    engine = RecommendationEngine()
    plan = engine.generate_weekly_plan()
    
    print(f"Weekly Plan - {plan['week']}")
    print("=" * 40)
    print(f"Daily target: {plan['daily_target']} minutes\n")
    
    for i, subj in enumerate(plan["subjects"], 1):
        print(f"{i}. {subj['subject']}")
        print(f"   Sessions this week: {subj['sessions']}")
        print(f"   Total time: {subj['total_minutes']} minutes\n")

def cmd_recommend_dashboard(args):
    engine = RecommendationEngine()
    dashboard = engine.get_dashboard()
    
    print("Learning Dashboard")
    print("=" * 40)
    print(f"\nStatus: {dashboard['status']}")
    print(f"\nMetrics:")
    print(f"  Focus Level: {dashboard['metrics']['focus_level']}")
    print(f"  Avg Score: {dashboard['metrics']['avg_score']}")
    print(f"  Study Consistency: {dashboard['metrics']['study_consistency']} days")
    print(f"  Recommendations: {dashboard['metrics']['recommendation_count']}")
    
    print(f"\nTop Subjects:")
    for subj, sessions in dashboard["top_subjects"].items():
        print(f"  {subj}: {sessions} sessions")
    
    print(f"\nRecommendations by Priority:")
    print(f"  High: {len(dashboard['recommendations_by_priority']['high'])}")
    print(f"  Medium: {len(dashboard['recommendations_by_priority']['medium'])}")
    print(f"  Low: {len(dashboard['recommendations_by_priority']['low'])}")



def cmd_analytics_all_plots(args):
    df = analytics.df_from_db()
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    fig = visualization.plot_all_charts(df)
    path = os.path.join(out_dir, "all_charts.png")
    fig.savefig(path)
    print(f"Saved combined charts: {path}")


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


#ML Commands

def cmd_ml_train(args):
    try:
        df = analytics.df_from_db()
        if df.empty:
            print("No session data available. Add some sessions first.")
            return
        
        print(f"Loading {len(df)} sessions...")
        feature_cols = ['focus_level', 'duration_minutes']
        X = df[feature_cols].copy()
        y = df['test_score'].copy()
        
        print(f"Using {len(feature_cols)} features: {feature_cols}")
        print(f"Feature shape: {X.shape}")
        
        X = preprocessing.clean_data(X.assign(test_score=y)).drop('test_score', axis=1)
        y = y[X.index]
        
        X_train, X_test, y_train, y_test = preprocessing.train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        X_train_scaled, X_test_scaled, scaler = preprocessing.scale_features(X_train, X_test)
        
        print(f"Train set: {X_train_scaled.shape[0]} samples")
        print(f"Test set: {X_test_scaled.shape[0]} samples")
        
        print("Training models...")
        models_dict = train.train_all_models(X_train_scaled, y_train)
        
        print("\nModel Performance on Test Set:")
        print("-" * 60)
        for model_name, mod in models_dict.items():
            y_pred = mod.predict(X_test_scaled)
            metrics = model.evaluate_model(y_test, y_pred)
            print(f"\n{model_name}:")
            for metric_name, value in metrics.items():
                print(f"  {metric_name:10s}: {value:.4f}")
        
        print("\nSaving models...")
        predict.save_all_models(models_dict, 'models')
        print("Models saved to 'models/' directory")
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()


def cmd_ml_predict(args):
    try:
        model_name = args.model_name if hasattr(args, 'model_name') else 'RandomForest'
        
        print(f"Loading model: {model_name}...")
        mod = predict.load_model(model_name, 'models')
        
        df = analytics.df_from_db()
        if df.empty:
            print("No session data available.")
            return
        
        feature_cols = ['focus_level', 'duration_minutes']
        X = df[feature_cols].copy()
        
        X_clean = preprocessing.clean_data(X.assign(test_score=df['test_score'])).drop('test_score', axis=1)
        
        predictions = predict.predict(mod, X_clean)
        
        print(f"\nPredictions from {model_name}:")
        print(f"Total predictions: {len(predictions)}")
        print(f"Average prediction: {predictions.mean():.2f}")
        print(f"Min prediction: {predictions.min():.2f}")
        print(f"Max prediction: {predictions.max():.2f}")
        print(f"\nSample predictions (first 5):")
        for i, pred in enumerate(predictions[:5]):
            print(f"  Sample {i+1}: {pred:.2f}")
        
        if len(predictions) > 5:
            print(f"  ... and {len(predictions) - 5} more predictions")
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()


def cmd_ml_evaluate(args):
    try:
        df = analytics.df_from_db()
        if df.empty:
            print("No session data available.")
            return
        
        print(f"Loading {len(df)} sessions...")
        
        feature_cols = ['focus_level', 'duration_minutes']
        X = df[feature_cols].copy()
        y = df['test_score'].copy()
        X_clean = preprocessing.clean_data(X.assign(test_score=y)).drop('test_score', axis=1)
        y = y[X_clean.index]
        cv_folds = 5
        
        print(f"Running {cv_folds}-fold cross-validation with {len(feature_cols)} features...")
        print("\nModel Performance (Cross-Validation):")
        print("-" * 60)
        
        lin_mod = train.LinearModel()
        lin_mod.train(X_clean, y)
        cv_lin = train.cross_validate_model(lin_mod, X_clean, y, cv_folds)
        print(f"\nLinearModel:")
        for metric, value in cv_lin.items():
            print(f"  {metric:20s}: {value:.4f}")

        rf_mod = train.RandomForestModel()
        rf_mod.train(X_clean, y)
        cv_rf = train.cross_validate_model(rf_mod, X_clean, y, cv_folds)
        print(f"\nRandomForestModel:")
        for metric, value in cv_rf.items():
            print(f"  {metric:20s}: {value:.4f}")

        gb_mod = train.GradientBoostingModel()
        gb_mod.train(X_clean, y)
        cv_gb = train.cross_validate_model(gb_mod, X_clean, y, cv_folds)
        print(f"\nGradientBoostingModel:")
        for metric, value in cv_gb.items():
            print(f"  {metric:20s}: {value:.4f}")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()


def cmd_ml_list_models(args):
    try:
        import os
        model_dir = 'models'
        if not os.path.exists(model_dir):
            print("No models found. Train models first with 'ml-train'")
            return
        
        models = [f[:-4] for f in os.listdir(model_dir) if f.endswith('.pkl')]
        if not models:
            print("No models found.")
            return
        
        print("Trained Models:")
        for m in sorted(models):
            print(f"  - {m}")
        
    except Exception as e:
        print(f"Error: {e}")


def cmd_ml_delete_model(args):
    try:
        model_name = args.model_name
        import os
        filepath = f"models/{model_name}.pkl"
        
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted {model_name}")
        else:
            print(f"Model not found: {model_name}")
        
    except Exception as e:
        print(f"Error: {e}")


def cmd_ml_ensemble_predict(args):
    try:
        model_names = args.models.split(',') if hasattr(args, 'models') else ['LinearRegression', 'RandomForest', 'GradientBoosting']
        ensemble_method = args.method if hasattr(args, 'method') else 'average'
        
        print(f"Loading ensemble: {', '.join(model_names)}...")
        
        models_dict = predict.load_all_models(model_names, 'models')
        
        df = analytics.df_from_db()
        if df.empty:
            print("No session data available.")
            return
        
        feature_cols = ['focus_level', 'duration_minutes']
        X = df[feature_cols].copy()
        
        X_clean = preprocessing.clean_data(X.assign(test_score=df['test_score'])).drop('test_score', axis=1)
        
        ensemble_preds = predict.ensemble_predict(models_dict, X_clean, ensemble_method)
        
        print(f"\nEnsemble Prediction ({ensemble_method}):")
        print(f"Total predictions: {len(ensemble_preds)}")
        print(f"Average prediction: {ensemble_preds.mean():.2f}")
        
        print(f"Sample predictions (first 5):")
        for i, pred in enumerate(ensemble_preds[:5]):
            print(f"  {i+1}: {pred:.2f}")
        
        if len(ensemble_preds) > 5:
            print(f"  ... and {len(ensemble_preds) - 5} more")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def cmd_ml_info(args):
    try:
        model_name = args.model_name
        mod = predict.load_model(model_name, 'models')
        
        print(f"Model: {model_name}")
        print(f"Type: {type(mod).__name__}")
        print(f"Loaded from: models/{model_name}.pkl")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()