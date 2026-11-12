# Zero-Cost X Publisher

> **Developer:** Radhe Wankhade · [@RadheWankhade01](https://x.com/RadheWankhade01) on X

Publish text posts and PNG images/charts to X (Twitter) at **$0 API cost** using **X Web Intent URLs** + **OS Clipboard PNG (`Ctrl+V`)** + **strict human-in-the-loop approval**.

> Built as a practical workaround to X removing the free developer API tier and moving to Pay-Per-Use API credits. Works on Windows, macOS, Linux, and in any modern browser.

## Features

- **$0 Publishing:** Uses `https://x.com/intent/tweet?text=...` instead of paid `POST /2/tweets` API calls.
- **Instant `Ctrl+V` Image Workflow:** Copies any PNG/JPG image straight to your system clipboard right before opening the pre-filled X composer.
- **Exact X `t.co` Length Accounting:** Counts every `http(s)://...` URL as 23 characters so your character budget matches X's composer.
- **Human Approval Gate:** Refuses to open the composer unless `--approve` is explicitly passed (or interactively confirmed), preventing accidental posts.
- **Browser Demo Included:** Zero-backend [`examples/web_composer_demo.html`](./examples/web_composer_demo.html) works offline in Chrome/Edge/Firefox.
- **Agent Skill Ready:** Includes [`SKILL.md`](./SKILL.md) at repo root so coding agents (Antigravity, Gemini CLI, Claude Code, Cursor) can use it immediately.

## Quick Start

### 1. Standalone CLI (Zero pip dependencies on Windows)

```bash
# Preview character count and generate Web Intent URL (dry run)
python scripts/publish_to_x.py --text "Shipping our open-source release today! https://github.com/example/repo"

# Copy image to clipboard, approve explicitly, and open X composer
python scripts/publish_to_x.py \
  --text "Shipping our open-source release today! https://github.com/example/repo" \
  --image ./chart.png \
  --approve \
  --open \
  --log ./x_audit_log.jsonl
```

Then just press **`Ctrl+V`** (`Cmd+V` on macOS) inside the X composer window to attach your image and click **Post**.

### 2. Browser UI Demo (Zero server needed)

Open [`examples/web_composer_demo.html`](./examples/web_composer_demo.html) in your browser:
1. Type/paste your post text.
2. Drop in any PNG chart/screenshot.
3. Click **Approve, Copy PNG & Open X ($0)**.
4. Hit `Ctrl+V` in X!

### 3. Install as an Agent Skill

```bash
# Workspace skill
git clone https://github.com/<your-username>/zero-cost-x-publisher.git .agents/skills/zero-cost-x-publisher

# Or global skill (Antigravity / Gemini CLI)
git clone https://github.com/<your-username>/zero-cost-x-publisher.git ~/.gemini/config/skills/zero-cost-x-publisher
```

## Clipboard Requirements by OS

- **Windows:** Built-in PowerShell + `.NET System.Windows.Forms.Clipboard` (no extra install needed).
- **macOS:** Built-in `osascript` (no extra install needed).
- **Linux:** Requires `wl-copy` (Wayland) or `xclip` (X11).

## Running Tests

```bash
pytest -v
```

## License

MIT

