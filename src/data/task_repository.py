import json
from pathlib import Path

from src.model.task import Task


class TaskRepository:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.set_storage_path(storage_path)

    def set_storage_path(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write([])

    def list_tasks(self) -> list[Task]:
        raw_tasks = self._read()
        return [Task.from_dict(item) for item in raw_tasks]

    def add_task(
        self,
        title: str,
        priority: str = "Media",
        due_date: str = "",
        notes: str = "",
    ) -> Task:
        tasks = self.list_tasks()
        next_id = max((task.task_id for task in tasks), default=0) + 1
        new_task = Task(
            task_id=next_id,
            title=title.strip(),
            priority=priority.strip() or "Media",
            due_date=due_date.strip(),
            notes=notes.strip(),
        )
        tasks.append(new_task)
        self._write([task.to_dict() for task in tasks])
        return new_task

    def complete_task(self, task_id: int) -> bool:
        return self.set_task_completed(task_id, True)

    def set_task_completed(self, task_id: int, completed: bool) -> bool:
        tasks = self.list_tasks()
        updated = False

        for task in tasks:
            if task.task_id == task_id:
                task.completed = completed
                updated = True
                break

        if updated:
            self._write([task.to_dict() for task in tasks])

        return updated

    def update_task(
        self,
        task_id: int,
        title: str,
        priority: str,
        due_date: str,
        notes: str,
    ) -> bool:
        tasks = self.list_tasks()
        updated = False

        for task in tasks:
            if task.task_id == task_id:
                task.title = title.strip()
                task.priority = priority.strip() or "Media"
                task.due_date = due_date.strip()
                task.notes = notes.strip()
                updated = True
                break

        if updated:
            self._write([task.to_dict() for task in tasks])

        return updated

    def delete_task(self, task_id: int) -> bool:
        tasks = self.list_tasks()
        remaining_tasks = [task for task in tasks if task.task_id != task_id]
        deleted = len(remaining_tasks) != len(tasks)

        if deleted:
            self._write([task.to_dict() for task in remaining_tasks])

        return deleted

    def duplicate_task(self, task_id: int) -> Task | None:
        source_task = self.find_task(task_id)
        if source_task is None:
            return None

        return self.add_task(
            f"Copia de {source_task.title}",
            priority=source_task.priority,
            due_date=source_task.due_date,
            notes=source_task.notes,
        )

    def find_task(self, task_id: int) -> Task | None:
        for task in self.list_tasks():
            if task.task_id == task_id:
                return task
        return None

    def export_tasks(self, export_path: Path) -> int:
        tasks = self.list_tasks()
        export_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_payload(export_path, [task.to_dict() for task in tasks])
        return len(tasks)

    def import_tasks(self, import_path: Path, mode: str = "replace") -> int:
        raw_tasks = self._read_payload(import_path)
        if not isinstance(raw_tasks, list):
            raise ValueError("El archivo importado debe contener una lista de tareas.")

        imported_tasks = [Task.from_dict(item) for item in raw_tasks]

        if mode == "replace":
            tasks_to_save = self._normalize_task_ids(imported_tasks)
        elif mode == "merge":
            current_tasks = self.list_tasks()
            next_id = max((task.task_id for task in current_tasks), default=0) + 1
            tasks_to_save = current_tasks[:]
            for task in imported_tasks:
                tasks_to_save.append(
                    Task(
                        task_id=next_id,
                        title=task.title,
                        completed=task.completed,
                        priority=task.priority,
                        due_date=task.due_date,
                        notes=task.notes,
                    )
                )
                next_id += 1
        else:
            raise ValueError("Modo de importacion no soportado.")

        self._write([task.to_dict() for task in tasks_to_save])
        return len(imported_tasks)

    def _read(self) -> list[dict]:
        return self._read_payload(self.storage_path)

    def _write(self, payload: list[dict]) -> None:
        self._write_payload(self.storage_path, payload)

    def _read_payload(self, path: Path) -> list[dict] | dict:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_payload(self, path: Path, payload: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)

    def _normalize_task_ids(self, tasks: list[Task]) -> list[Task]:
        normalized_tasks: list[Task] = []
        for index, task in enumerate(tasks, start=1):
            normalized_tasks.append(
                Task(
                    task_id=index,
                    title=task.title,
                    completed=task.completed,
                    priority=task.priority,
                    due_date=task.due_date,
                    notes=task.notes,
                )
            )
        return normalized_tasks
