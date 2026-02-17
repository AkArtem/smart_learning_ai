Simple recommendation system based on learning patterns.

## How it works

Analyzes study data and generates:
- Recommendations based on focus and performance
- Daily study plans (optimized schedule)
- Weekly plans (subject-focused)
- Reports and dashboards

## Commands

```bash
python -m src.cli.main analytics-recommendations
python -m src.cli.main recommend-daily-plan [--date YYYY-MM-DD]
python -m src.cli.main recommend-weekly-plan
python -m src.cli.main recommend-dashboard
```

## Examples

### Recommendations
```
Recommendations:
[1] Boost Math
  Your score in Math is low (59%). Try 2-3 focused sessions this week.

[2] Focus Could Be Better
  Moderate focus. Consider 40-min sessions with 10-min breaks.
```

### Daily Plan
```
Daily Plan - 2026-02-16

Sessions:
  09:00 - Math (40 min)
  14:00 - English (40 min)
  18:00 - Chemistry (40 min)

Total: 120 minutes
```

### Weekly Plan
```
Weekly Plan - 2026-W07
Daily target: 90 minutes

1. Math - 3 sessions, 120 min
2. English - 3 sessions, 120 min
3. Chemistry - 3 sessions, 120 min
4. History - 3 sessions, 120 min
5. Physics - 3 sessions, 120 min
```

### Dashboard
```
Learning Dashboard
Status: Needs Attention

Metrics:
  Focus Level: 2.83
  Avg Score: 71.8
  Study Consistency: 29 days
  Recommendations: 2

Top Subjects: History (30), Math (28), Chemistry (23)
Recommendations: High(1) | Medium(1) | Low(0)
```

## Code

- `analyze()` - Run all analysis
- `generate_daily_plan(date)` - Daily schedule
- `generate_weekly_plan()` - Weekly schedule
- `get_text_advice()` - CLI text
- `get_dashboard()` - Dashboard data

## Testing

```bash
pytest tests/test_recommender.py -v
```