from pathlib import Path

from src.data.task_repository import TaskRepository


def test_add_and_complete_task(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")

    task = repository.add_task(
        "Preparar documentacion",
        priority="Alta",
        due_date="2026-04-30",
        notes="Preparar resumen del avance",
    )
    assert task.task_id == 1
    assert task.title == "Preparar documentacion"
    assert task.completed is False
    assert task.priority == "Alta"
    assert task.due_date == "2026-04-30"
    assert task.notes == "Preparar resumen del avance"

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
        notes="Ahora con detalle ampliado",
    ) is True

    updated = repository.find_task(task.task_id)
    assert updated is not None
    assert updated.title == "Actualizada"
    assert updated.priority == "Alta"
    assert updated.due_date == "2026-05-10"
    assert updated.notes == "Ahora con detalle ampliado"


def test_export_tasks_writes_current_payload(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")
    repository.add_task("Preparar release", priority="Alta", notes="Exportar respaldo")
    repository.add_task("Validar UI", priority="Media", due_date="2026-05-15")

    exported_count = repository.export_tasks(tmp_path / "backup" / "tasks-export.json")

    exported_repository = TaskRepository(tmp_path / "backup" / "tasks-export.json")
    tasks = exported_repository.list_tasks()

    assert exported_count == 2
    assert [task.title for task in tasks] == ["Preparar release", "Validar UI"]


def test_import_tasks_replace_reorders_ids_from_file(tmp_path: Path) -> None:
    source_repository = TaskRepository(tmp_path / "source.json")
    imported_task = source_repository.add_task(
        "Tarea importada",
        priority="Baja",
        due_date="2026-06-01",
        notes="Llega desde backup",
    )
    assert imported_task.task_id == 1

    target_repository = TaskRepository(tmp_path / "target.json")
    target_repository.add_task("Tarea local")

    imported_count = target_repository.import_tasks(tmp_path / "source.json", mode="replace")
    tasks = target_repository.list_tasks()

    assert imported_count == 1
    assert len(tasks) == 1
    assert tasks[0].task_id == 1
    assert tasks[0].title == "Tarea importada"


def test_import_tasks_merge_appends_with_new_ids(tmp_path: Path) -> None:
    current_repository = TaskRepository(tmp_path / "current.json")
    current_repository.add_task("Tarea local")

    import_repository = TaskRepository(tmp_path / "import.json")
    import_repository.add_task("Tarea externa A", priority="Alta")
    import_repository.add_task("Tarea externa B", priority="Baja")

    imported_count = current_repository.import_tasks(tmp_path / "import.json", mode="merge")
    tasks = current_repository.list_tasks()

    assert imported_count == 2
    assert [task.task_id for task in tasks] == [1, 2, 3]
    assert [task.title for task in tasks] == [
        "Tarea local",
        "Tarea externa A",
        "Tarea externa B",
    ]


def test_duplicate_task_creates_new_copy_with_new_id(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")
    original = repository.add_task(
        "Preparar demo",
        priority="Alta",
        due_date="2026-06-10",
        notes="Con datos reales",
    )

    duplicated = repository.duplicate_task(original.task_id)
    tasks = repository.list_tasks()

    assert duplicated is not None
    assert duplicated.task_id == 2
    assert duplicated.title == "Copia de Preparar demo"
    assert duplicated.priority == "Alta"
    assert duplicated.due_date == "2026-06-10"
    assert duplicated.notes == "Con datos reales"
    assert [task.task_id for task in tasks] == [1, 2]


def test_duplicate_task_returns_none_for_unknown_id(tmp_path: Path) -> None:
    repository = TaskRepository(tmp_path / "tasks.json")

    assert repository.duplicate_task(999) is None
