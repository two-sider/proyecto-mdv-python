import json
from pathlib import Path


class SettingsRepository:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write({"theme": "clara"})

    def load_theme(self) -> str:
        payload = self._read()
        theme = str(payload.get("theme", "clara"))
        return theme if theme in {"clara", "oscura", "blue-coding"} else "clara"

    def save_theme(self, theme: str) -> None:
        safe_theme = theme if theme in {"clara", "oscura", "blue-coding"} else "clara"
        self._write({"theme": safe_theme})

    def _read(self) -> dict:
        with self.storage_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write(self, payload: dict) -> None:
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
