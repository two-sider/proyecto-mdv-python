from pathlib import Path
import json

from src.data.settings_repository import SettingsRepository


def test_settings_repository_persists_theme(tmp_path: Path) -> None:
    repository = SettingsRepository(tmp_path / "settings.json")

    assert repository.load_theme() == "clara"

    repository.save_theme("oscura")
    assert repository.load_theme() == "oscura"


def test_settings_repository_falls_back_for_invalid_theme(tmp_path: Path) -> None:
    repository = SettingsRepository(tmp_path / "settings.json")

    repository.save_theme("invalido")
    assert repository.load_theme() == "clara"


def test_settings_repository_persists_sync_folder(tmp_path: Path) -> None:
    repository = SettingsRepository(tmp_path / "settings.json")

    repository.save_sync_folder("C:/Users/x13/Google Drive")

    assert repository.load_sync_folder() == "C:/Users/x13/Google Drive"


def test_settings_repository_preserves_sync_folder_when_saving_theme(tmp_path: Path) -> None:
    repository = SettingsRepository(tmp_path / "settings.json")

    repository.save_sync_folder("C:/Drive")
    repository.save_theme("oscura")

    assert repository.load_theme() == "oscura"
    assert repository.load_sync_folder() == "C:/Drive"


def test_settings_repository_reads_utf8_bom_file(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.json"
    payload = {"theme": "oscura", "sync_folder": "C:/Drive"}
    settings_path.write_text(json.dumps(payload), encoding="utf-8-sig")

    repository = SettingsRepository(settings_path)

    assert repository.load_theme() == "oscura"
    assert repository.load_sync_folder() == "C:/Drive"
