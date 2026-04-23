import logging
import sys
from pathlib import Path

from src.data.settings_repository import SettingsRepository
from src.data.task_repository import TaskRepository
from src.logging_config import configure_logging
from src.view.task_manager_view import TaskManagerView


def get_runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def build_storage_path() -> Path:
    project_root = get_runtime_root()
    return project_root / "storage" / "tasks.json"


def build_log_path() -> Path:
    project_root = get_runtime_root()
    return project_root / "logs" / "taskflow.log"


def build_settings_path() -> Path:
    project_root = get_runtime_root()
    return project_root / "storage" / "settings.json"


def main() -> None:
    configure_logging(build_log_path())
    logger = logging.getLogger(__name__)
    repository = TaskRepository(build_storage_path())
    settings_repository = SettingsRepository(build_settings_path())
    view = TaskManagerView(repository, settings_repository=settings_repository, logger=logger)
    logger.info("Aplicacion iniciada")
    view.run()


if __name__ == "__main__":
    main()
