from dataclasses import dataclass
from datetime import datetime

@dataclass
class SessionRecord:
    subject_id: int
    date: str # YYYY-MM-DD
    duration_minutes: int
    focus_level: int
    start_time: str | None = None  # HH:MM
    test_score: int | None = None
    notes: str | None = None
    id: int | None = None
    
    def __post_init__(self):
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"date must be YYYY-MM-DD, got {self.date}")
        if not (1 <= self.focus_level <= 5):
            raise ValueError(f"focus_level must be between 1 and 5, got {self.focus_level}")
        if self.test_score is not None and not (0 <= self.test_score <= 100):
            raise ValueError(f"test_score must be between 0 and 100, got {self.test_score}")
        if self.duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be greater than 0, got {self.duration_minutes}")
    
    def get_start_timestamp(self):
        if self.start_time:
            return f"{self.date} {self.start_time}:00"
        else:
            return f"{self.date} 00:00:00"
    
    def to_tuple(self):
        return (self.subject_id, self.get_start_timestamp(), self.duration_minutes, self.focus_level, self.test_score, self.notes)
    
    @classmethod
    def from_row(cls, row):
        timestamp = row["start_timestamp"]

        date, time = timestamp.split(" ")

        start_time = time[:5]
        return cls(
            subject_id=row["subject_id"],
            date=date,
            start_time=start_time,
            duration_minutes=row["duration_minutes"],
            focus_level=row["focus_level"],
            test_score=row["test_score"],
            notes=row["notes"],
            id=row["id"],)