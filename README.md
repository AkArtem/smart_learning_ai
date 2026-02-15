# Smart Learning AI

A learning tracker with ML-powered score predictions.

## What it does
- Tracks study sessions (duration, focus level, test scores)
- Analyzes study patterns and performance
- Predicts test scores based on focus + study time

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

## Testing
```
pytest -q
```