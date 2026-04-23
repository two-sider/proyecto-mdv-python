import json
from pathlib import Path

from src.model.task import Task


class TaskRepository:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write([])

    def list_tasks(self) -> list[Task]:
        raw_tasks = self._read()
        return [Task.from_dict(item) for item in raw_tasks]

    def add_task(self, title: str) -> Task:
        tasks = self.list_tasks()
        next_id = max((task.task_id for task in tasks), default=0) + 1
        new_task = Task(task_id=next_id, title=title.strip())
        tasks.append(new_task)
        self._write([task.to_dict() for task in tasks])
        return new_task

    def complete_task(self, task_id: int) -> bool:
        tasks = self.list_tasks()
        updated = False

        for task in tasks:
            if task.task_id == task_id:
                task.completed = True
                updated = True
                break

        if updated:
            self._write([task.to_dict() for task in tasks])

        return updated

    def _read(self) -> list[dict]:
        with self.storage_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write(self, payload: list[dict]) -> None:
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
