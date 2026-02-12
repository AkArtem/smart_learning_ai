# smart_learning_ai
Smart learning analytics and recommendation system using Python, SQL, and Machine Learning.

What is this project:
- Simple learning tracker that stores study subjects and learning sessions in SQLite.
- Small CLI to initialize the database and add/list/delete subjects and sessions.

Quick start:
- Install dependencies from requirements.txt

Commands to work with project
```
python -m src.cli.main add-subject Math
python -m src.cli.main list-subjects
python -m src.cli.main add-session 1 2026-02-11 --start-time 18:30 --duration 60 --focus 4
python -m src.cli.main list-sessions
python -m src.cli.main show-session 1
python -m src.cli.main delete-session 1
```

Tests:
- Run pytest to execute the unit tests (there are tests for models, database, and CLI)