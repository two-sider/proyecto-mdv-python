from pathlib import Path

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
