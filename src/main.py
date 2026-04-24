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


def build_drive_storage_path(sync_folder: str) -> Path:
    return Path(sync_folder) / "TaskFlowMDV" / "tasks.json"


def main() -> None:
    configure_logging(build_log_path())
    logger = logging.getLogger(__name__)
    settings_repository = SettingsRepository(build_settings_path())
    local_storage_path = build_storage_path()
    sync_folder = settings_repository.load_sync_folder()
    storage_path = build_drive_storage_path(sync_folder) if sync_folder else local_storage_path
    repository = TaskRepository(storage_path)
    view = TaskManagerView(
        repository,
        settings_repository=settings_repository,
        local_storage_path=local_storage_path,
        logger=logger,
    )
    logger.info("Aplicacion iniciada")
    view.run()


if __name__ == "__main__":
    main()
