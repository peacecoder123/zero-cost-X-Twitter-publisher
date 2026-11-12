#!/usr/bin/env python3
"""
Zero-Cost X (Twitter) Publisher CLI.

Generates an X Web Intent URL for any text, validates X-weighted character length
(t.co counts every http(s) URL as 23 characters), optionally copies a PNG/JPG image
to the OS clipboard for instant Ctrl+V pasting inside X, and enforces an explicit
human-approval gate before opening the browser composer.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.parse
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
X_TCO_URL_LENGTH = 23
X_STANDARD_LIMIT = 280
X_INTENT_BASE = "https://x.com/intent/tweet"


def count_x_weighted_chars(text: str) -> int:
    """Calculate X character length counting each http(s) URL as 23 chars."""
    if not text:
        return 0
    normalized = URL_PATTERN.sub("X" * X_TCO_URL_LENGTH, text)
    return len(normalized)


def build_x_intent_url(text: str) -> str:
    """Build a properly percent-encoded X Web Intent URL."""
    clean = (text or "").strip()
    if not clean:
        raise ValueError("Post text cannot be empty.")
    encoded = urllib.parse.quote(clean, safe="")
    return f"{X_INTENT_BASE}?text={encoded}"


def copy_image_to_clipboard(image_path: str) -> Dict[str, str]:
    """
    Copy an image file (PNG/JPG/BMP/GIF) to the OS clipboard so the user
    can paste it with Ctrl+V directly inside the X composer window.
    """
    resolved = Path(image_path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Image file not found: {resolved}")

    system = platform.system()

    if system == "Windows":
        escaped = str(resolved).replace("'", "''")
        ps_script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "Add-Type -AssemblyName System.Drawing; "
            f"$img = [System.Drawing.Image]::FromFile('{escaped}'); "
            "try { [System.Windows.Forms.Clipboard]::SetImage($img) } "
            "finally { $img.Dispose() }"
        )
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-STA", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Windows clipboard copy failed: {proc.stderr.strip()}")
        return {"status": "CLIPBOARD_COPIED", "backend": "powershell-winforms", "path": str(resolved)}

    if system == "Darwin":
        escaped = str(resolved).replace('"', '\\"')
        ext = resolved.suffix.lower()
        clip_class = "JPEG picture" if ext in (".jpg", ".jpeg") else "«class PNGf»"
        apple_script = f'set the clipboard to (read (POSIX file "{escaped}") as {clip_class})'
        proc = subprocess.run(
            ["osascript", "-e", apple_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"macOS clipboard copy failed: {proc.stderr.strip()}")
        return {"status": "CLIPBOARD_COPIED", "backend": "osascript", "path": str(resolved)}

    # Linux / BSD (Wayland or X11)
    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy"):
        with open(resolved, "rb") as f:
            proc = subprocess.run(["wl-copy", "--type", "image/png"], stdin=f, capture_output=True, timeout=15)
        if proc.returncode == 0:
            return {"status": "CLIPBOARD_COPIED", "backend": "wl-copy", "path": str(resolved)}

    if shutil.which("xclip"):
        proc = subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "image/png", "-i", str(resolved)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0:
            return {"status": "CLIPBOARD_COPIED", "backend": "xclip", "path": str(resolved)}

    return {
        "status": "CLIPBOARD_UNSUPPORTED",
        "backend": "none",
        "path": str(resolved),
        "hint": "Install wl-copy (Wayland) or xclip (X11), or attach the image manually in X.",
    }


def append_audit_log(
    log_path: str,
    text: str,
    intent_url: str,
    image_path: Optional[str],
    approved: bool,
    opened_browser: bool,
    tweet_url: Optional[str] = None,
) -> None:
    """Append a local JSONL audit record of the $0 publication event."""
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "ZERO_COST_WEB_INTENT",
        "api_cost_usd": 0.0,
        "approved_by_human": approved,
        "opened_browser": opened_browser,
        "weighted_chars": count_x_weighted_chars(text),
        "text_preview": text[:280],
        "image_path": image_path,
        "tweet_url": tweet_url,
        "intent_url": intent_url,
    }
    target = Path(log_path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare or open a $0 human-approved X Web Intent post with optional clipboard PNG copy."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Post text to publish on X.")
    group.add_argument("--text-file", help="Path to UTF-8 text file containing the post.")

    parser.add_argument("--image", help="Optional PNG/JPG image path to copy to the OS clipboard for Ctrl+V.")
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Explicit human-approval gate required before --open launches the browser.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for [y/N] confirmation in terminal before copying clipboard/opening X.",
    )
    parser.add_argument("--open", action="store_true", help="Open X Web Intent URL in default browser (requires --approve).")
    parser.add_argument("--log", help="Optional JSONL file path to record $0 publication audit logs.")
    parser.add_argument("--tweet-url", help="Optional live tweet URL to save in the audit log.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output.")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    if args.text_file:
        text = Path(args.text_file).expanduser().read_text(encoding="utf-8").strip()
    else:
        text = (args.text or "").strip()

    if not text:
        print("Error: Post text is empty.", file=sys.stderr)
        return 2

    weighted_len = count_x_weighted_chars(text)
    intent_url = build_x_intent_url(text)
    warning = None
    if weighted_len > X_STANDARD_LIMIT:
        warning = (
            f"Weighted length is {weighted_len} chars (exceeds {X_STANDARD_LIMIT}-char standard X limit; "
            "fits X Premium or trim before posting)."
        )

    approved = bool(args.approve)
    if args.open and not approved:
        if args.interactive and sys.stdin.isatty():
            print(f"\n--- POST PREVIEW ({weighted_len} weighted chars) ---\n{text}\n")
            if warning:
                print(f"WARNING: {warning}")
            ans = input("Approve and open in X composer? [y/N]: ").strip().lower()
            approved = ans in ("y", "yes")
        if not approved:
            print(
                "BLOCKED: Refusing to open X composer without explicit approval (--approve or --interactive confirmation).",
                file=sys.stderr,
            )
            return 3

    clipboard_result = None
    if args.image and (approved or not args.open):
        clipboard_result = copy_image_to_clipboard(args.image)

    opened = False
    if args.open and approved:
        opened = bool(webbrowser.open(intent_url))

    if args.log:
        append_audit_log(
            log_path=args.log,
            text=text,
            intent_url=intent_url,
            image_path=args.image,
            approved=approved,
            opened_browser=opened,
            tweet_url=args.tweet_url,
        )

    result = {
        "status": "OPENED_IN_BROWSER" if opened else ("APPROVED_READY" if approved else "PREVIEW_ONLY"),
        "weighted_chars": weighted_len,
        "within_standard_limit": weighted_len <= X_STANDARD_LIMIT,
        "warning": warning,
        "intent_url": intent_url,
        "clipboard": clipboard_result,
        "opened_browser": opened,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Status: {result['status']}")
        print(f"Weighted chars: {weighted_len} / {X_STANDARD_LIMIT}")
        if warning:
            print(f"Warning: {warning}")
        if clipboard_result:
            print(f"Clipboard: {clipboard_result['status']} ({clipboard_result['backend']})")
        print(f"Intent URL: {intent_url}")
        if opened and clipboard_result and clipboard_result["status"] == "CLIPBOARD_COPIED":
            print("Next step: Press Ctrl+V (Cmd+V on macOS) inside the X composer tab to paste your image!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
