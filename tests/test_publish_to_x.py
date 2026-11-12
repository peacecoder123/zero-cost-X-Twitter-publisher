import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_to_x as px  # noqa: E402


def test_weighted_char_count_uses_23_for_urls():
    long_url = "https://example.com/some/very/long/path?with=query&params=1234567890"
    text = f"Check out {long_url}"
    assert px.count_x_weighted_chars(text) == len("Check out ") + 23


def test_build_x_intent_url_encodes_safely():
    url = px.build_x_intent_url("Hello #world & @dev!")
    assert url.startswith("https://x.com/intent/tweet?text=")
    assert "%23world" in url
    assert "%26" in url


def test_open_blocked_without_explicit_approval(monkeypatch):
    called = []
    monkeypatch.setattr(px.webbrowser, "open", lambda u: called.append(u) or True)
    rc = px.main(["--text", "Unapproved post", "--open"])
    assert rc == 3
    assert called == []


def test_approved_open_copies_image_logs_and_opens_browser(tmp_path, monkeypatch):
    img = tmp_path / "chart.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    audit = tmp_path / "audit.jsonl"

    copied = []
    opened = []
    monkeypatch.setattr(
        px,
        "copy_image_to_clipboard",
        lambda p: copied.append(p) or {"status": "CLIPBOARD_COPIED", "backend": "mock", "path": p},
    )
    monkeypatch.setattr(px.webbrowser, "open", lambda u: opened.append(u) or True)

    rc = px.main(
        [
            "--text",
            "Approved post https://github.com/example/repo",
            "--image",
            str(img),
            "--approve",
            "--open",
            "--log",
            str(audit),
        ]
    )
    assert rc == 0
    assert copied == [str(img)]
    assert len(opened) == 1
    assert audit.exists()
    row = json.loads(audit.read_text(encoding="utf-8").strip())
    assert row["approved_by_human"] is True
    assert row["api_cost_usd"] == 0.0
    assert row["opened_browser"] is True
