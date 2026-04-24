from src.update_checker import (
    is_newer_version,
    normalize_version,
    parse_latest_release_payload,
)


def test_normalize_version_handles_prefix_and_padding() -> None:
    assert normalize_version("v0.5.0") == (0, 5, 0)
    assert normalize_version("1.2") == (1, 2)


def test_is_newer_version_compares_semver_like_values() -> None:
    assert is_newer_version("0.5.0", "0.6.0") is True
    assert is_newer_version("0.5.0", "0.5.0") is False
    assert is_newer_version("0.5.1", "0.5.0") is False


def test_parse_latest_release_payload_extracts_required_fields() -> None:
    release = parse_latest_release_payload(
        {
            "tag_name": "v0.6.0",
            "html_url": "https://github.com/two-sider/proyecto-mdv-python/releases/tag/v0.6.0",
        }
    )

    assert release.version == "0.6.0"
    assert release.url.endswith("/v0.6.0")
