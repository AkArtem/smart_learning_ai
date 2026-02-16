# Smart Learning AI

An intelligent learning tracker with analytics, machine learning predictions,
and a personalized recommendation system.

## What it does
- Tracks study sessions (duration, focus level, test scores), manage subjects, store in SQLite
- Analyzes study patterns and performance, create visual dashboards
- Predicts test scores based on focus + study time, train / evaluate / save models
- Personalize study advice, provide daily and weekly planning, learning dashboard

## How Predictions Work
Models learn from study history to predict scores:
- Input: focus level (1-5) + study duration (minutes)
- Output: predicted test score

## Setup
```
pip install -r requirements.txt
```

## Quick Commands

**Manage Sessions:**
```
python -m src.cli.main add-subject Math
python -m src.cli.main add-session 1 2026-02-11 --start-time 18:30 --duration 60 --focus 4
python -m src.cli.main list-sessions
```

**Analytics:**
```
python -m src.cli.main analytics-summary
python -m src.cli.main analytics-dashboard
```

**ML Predictions:**
```
python -m src.cli.main ml-train
python -m src.cli.main ml-predict
python -m src.cli.main ml-ensemble-predict
```

**Recommendations:**
```
python -m src.cli.main analytics-recommendations
python -m src.cli.main recommend-daily-plan
python -m src.cli.main recommend-weekly-plan
python -m src.cli.main recommend-dashboard
```

## Testing
```
pytest -q
```