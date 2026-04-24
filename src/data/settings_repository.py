import json
from pathlib import Path


class SettingsRepository:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write(self._build_default_payload())

    def load_theme(self) -> str:
        payload = self._read()
        theme = str(payload.get("theme", "clara"))
        return theme if theme in {"clara", "oscura", "blue-coding"} else "clara"

    def save_theme(self, theme: str) -> None:
        payload = self._read()
        safe_theme = theme if theme in {"clara", "oscura", "blue-coding"} else "clara"
        payload["theme"] = safe_theme
        self._write(payload)

    def load_sync_folder(self) -> str:
        payload = self._read()
        return str(payload.get("sync_folder", "")).strip()

    def save_sync_folder(self, sync_folder: str) -> None:
        payload = self._read()
        payload["sync_folder"] = sync_folder.strip()
        self._write(payload)

    def _read(self) -> dict:
        with self.storage_path.open("r", encoding="utf-8-sig") as file:
            payload = json.load(file)

        default_payload = self._build_default_payload()
        if not isinstance(payload, dict):
            return default_payload

        return {
            "theme": str(payload.get("theme", default_payload["theme"])),
            "sync_folder": str(payload.get("sync_folder", default_payload["sync_folder"])).strip(),
        }

    def _write(self, payload: dict) -> None:
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)

    def _build_default_payload(self) -> dict[str, str]:
        return {
            "theme": "clara",
            "sync_folder": "",
        }
