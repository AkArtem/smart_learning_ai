from dataclasses import dataclass


@dataclass
class Subject:
    id: int | None = None
    name: str = ""

    def __repr__(self) -> str:
        return f"Subject(id={self.id}, name='{self.name}')"

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError(f"Subject name must be a non-empty string, got: {self.name!r}")
