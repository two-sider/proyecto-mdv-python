from pathlib import Path

from src.data.task_repository import TaskRepository


def test_add_and_complete_task(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")

    task = repository.add_task("Preparar documentacion")
    assert task.task_id == 1
    assert task.title == "Preparar documentacion"
    assert task.completed is False

    assert repository.complete_task(1) is True

    tasks = repository.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].completed is True
