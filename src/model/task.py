from dataclasses import dataclass, asdict


@dataclass
class Task:
    task_id: int
    title: str
    completed: bool = False
    priority: str = "Media"
    due_date: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            task_id=int(data["task_id"]),
            title=str(data["title"]),
            completed=bool(data.get("completed", False)),
            priority=str(data.get("priority", "Media")),
            due_date=str(data.get("due_date", "")),
        )
