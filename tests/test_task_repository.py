from pathlib import Path

from src.data.task_repository import TaskRepository


def test_add_and_complete_task(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")

    task = repository.add_task("Preparar documentacion", priority="Alta", due_date="2026-04-30")
    assert task.task_id == 1
    assert task.title == "Preparar documentacion"
    assert task.completed is False
    assert task.priority == "Alta"
    assert task.due_date == "2026-04-30"

    assert repository.complete_task(1) is True

    tasks = repository.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].completed is True


def test_reopen_and_delete_task(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")

    task = repository.add_task("Preparar interfaz visual")
    assert repository.set_task_completed(task.task_id, True) is True
    assert repository.set_task_completed(task.task_id, False) is True

    tasks = repository.list_tasks()
    assert tasks[0].completed is False

    assert repository.delete_task(task.task_id) is True
    assert repository.list_tasks() == []


def test_find_task_returns_none_for_unknown_id(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")

    repository.add_task("Tarea existente")
    assert repository.find_task(999) is None


def test_update_task_changes_main_fields(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")

    task = repository.add_task("Original", priority="Baja", due_date="2026-05-01")
    assert repository.update_task(
        task.task_id,
        title="Actualizada",
        priority="Alta",
        due_date="2026-05-10",
    ) is True

    updated = repository.find_task(task.task_id)
    assert updated is not None
    assert updated.title == "Actualizada"
    assert updated.priority == "Alta"
    assert updated.due_date == "2026-05-10"
