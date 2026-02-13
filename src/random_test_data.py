import random
from src.db.database import DatabaseManager
from src.models.session import SessionRecord

db = DatabaseManager()
db.migrate()
conn = db._connect()
cur = conn.cursor()

cur.execute("DELETE FROM learning_sessions")
cur.execute("DELETE FROM subjects")

cur.execute("DELETE FROM sqlite_sequence WHERE name='subjects'")
cur.execute("DELETE FROM sqlite_sequence WHERE name='learning_sessions'")

conn.commit()
conn.close()
subjects = ["Math","History","Physics","Chemistry","English"]
for name in subjects:
    db.add_subject(name)

for i in range(100):
    s = SessionRecord(
        subject_id=random.randint(1,5),
        date=f"2026-02-{random.randint(1,28):02d}",
        start_time=f"{random.randint(6,22):02d}:{random.choice([0,30]):02d}",
        duration_minutes=random.choice([30,45,60,90]),
        focus_level=random.randint(1,5),
        test_score=random.randint(50,100)
    )
    db.add_session(s)