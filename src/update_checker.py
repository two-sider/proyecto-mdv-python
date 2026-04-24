import json
from dataclasses import dataclass
from urllib.request import Request, urlopen

from src.app_info import APP_NAME, LATEST_RELEASE_API_URL


@dataclass
class ReleaseInfo:
    version: str
    url: str


def normalize_version(version: str) -> tuple[int, ...]:
    clean_version = version.strip().lower().removeprefix("v")
    parts = []
    for raw_part in clean_version.split("."):
        digits = "".join(character for character in raw_part if character.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def is_newer_version(current_version: str, latest_version: str) -> bool:
    current_parts = normalize_version(current_version)
    latest_parts = normalize_version(latest_version)
    max_length = max(len(current_parts), len(latest_parts))
    padded_current = current_parts + (0,) * (max_length - len(current_parts))
    padded_latest = latest_parts + (0,) * (max_length - len(latest_parts))
    return padded_latest > padded_current


def parse_latest_release_payload(payload: dict) -> ReleaseInfo:
    tag_name = str(payload.get("tag_name", "")).strip()
    html_url = str(payload.get("html_url", "")).strip()
    if not tag_name or not html_url:
        raise ValueError("La release mas reciente no tiene la informacion esperada.")
    return ReleaseInfo(version=tag_name.removeprefix("v"), url=html_url)


def fetch_latest_release(api_url: str = LATEST_RELEASE_API_URL) -> ReleaseInfo:
    request = Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{APP_NAME} Update Checker",
        },
    )
    with urlopen(request, timeout=5) as response:
        payload = json.load(response)
    return parse_latest_release_payload(payload)
