from pathlib import Path

from src.data.task_repository import TaskRepository
from src.view.console_view import ConsoleView


def build_storage_path() -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "storage" / "tasks.json"


def main() -> None:
    repository = TaskRepository(build_storage_path())
    view = ConsoleView(repository)
    view.run()


if __name__ == "__main__":
    main()
