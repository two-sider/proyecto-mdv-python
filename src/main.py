import logging
from pathlib import Path

from src.data.task_repository import TaskRepository
from src.logging_config import configure_logging
from src.view.task_manager_view import TaskManagerView


def build_storage_path() -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "storage" / "tasks.json"


def build_log_path() -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "logs" / "taskflow.log"


def main() -> None:
    configure_logging(build_log_path())
    logger = logging.getLogger(__name__)
    repository = TaskRepository(build_storage_path())
    view = TaskManagerView(repository, logger=logger)
    logger.info("Aplicacion iniciada")
    view.run()


if __name__ == "__main__":
    main()
