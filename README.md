# Zero-Cost X Publisher

> **Developer:** Radhe Wankhade · [@RadheWankhade01](https://x.com/RadheWankhade01) on X

1.
<img width="1822" height="902" alt="Screenshot 2026-11-13 021239" src="https://github.com/user-attachments/assets/edbc3880-7202-47e6-9dc5-845d2289e4ca" />
2.
<img width="1812" height="903" alt="Screenshot 2026-11-13 021256" src="https://github.com/user-attachments/assets/6baa93a8-0725-4d53-bb26-b9b2219438de" />
3.
<img width="1812" height="912" alt="Screenshot 2026-11-13 021320" src="https://github.com/user-attachments/assets/daeffd37-6a59-438e-935e-8103ad15665b" />

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python) ![Zero pip deps](https://img.shields.io/badge/pip%20deps-zero%20(stdlib%20only)-brightgreen) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey) ![API Cost](https://img.shields.io/badge/X%20API%20cost-%240-success)

Publish text posts **and PNG images/charts** to X (Twitter) at **\$0 API cost** using **X Web Intent URLs** + **OS Clipboard (`Ctrl+V`)** + a **mandatory human-approval gate** that blocks all auto-posting.

> **Why this exists:** X killed the free API tier in 2023 and moved to pay-per-use (\$0.10–\$0.15 per tweet via API). This tool uses X's own web intent system — a standard browser URL — to pre-fill the composer so you post for free, every time, with zero API billing.

---

## How It Works

```
Your text + image
      │
      ▼
┌─────────────────────────────────────┐
│  1. Validate X weighted char count  │  ← Counts URLs as 23 chars (t.co)
│  2. Human approval gate             │  ← BLOCKS if --approve not passed
│  3. Copy PNG to OS clipboard        │  ← PowerShell / osascript / wl-copy
│  4. Build x.com/intent/tweet?text=  │  ← URL-encoded, opens in browser
│  5. User presses Ctrl+V in X tab   │  ← Image attaches, human clicks Post
│  6. Append audit log (JSONL)        │  ← api_cost_usd: 0.0, approved: true
└─────────────────────────────────────┘
```

**Zero API calls are made.** The browser opens X's standard compose page — the same one you'd use manually. The difference: your text is pre-filled and your image is on the clipboard.

---

## Features

| Feature | Detail |
|---|---|
| **\$0 Publishing** | Uses `x.com/intent/tweet?text=...` — no `POST /2/tweets`, no billing |
| **Clipboard PNG** | Copies chart/screenshot to OS clipboard so you just press `Ctrl+V` |
| **Exact t.co Counting** | Every `http(s)://...` URL counted as exactly **23 chars**, matching X's real composer |
| **Hard Approval Gate** | Refuses to open browser without `--approve` or interactive `[y/N]` confirmation |
| **Audit Log (JSONL)** | Appends every session to a local `.jsonl` with timestamp, char count, `api_cost_usd: 0.0` |
| **Browser Demo HTML** | Offline `examples/web_composer_demo.html` — works in Chrome/Edge/Firefox, no server |
| **Agent Skill Ready** | `SKILL.md` at repo root — works with Antigravity, Gemini CLI, Claude Code, Cursor |

---

## Quick Start

### 1. Dry Run — Preview character count only (no browser opens)

```bash
python scripts/publish_to_x.py \
  --text "Shipping our open-source release today! Check it out 👉 https://github.com/example/repo"
```

**Terminal output:**

```
Status: PREVIEW_ONLY
Weighted chars: 65 / 280
Intent URL: https://x.com/intent/tweet?text=Shipping%20our%20open-source...
```

---

### 2. Approve and open X composer (text only)

```bash
python scripts/publish_to_x.py \
  --text "Big news: our open-source tool just hit 1,000 GitHub stars 🚀 https://github.com/example/repo" \
  --approve \
  --open
```

**Terminal output:**

```
Status: OPENED_IN_BROWSER
Weighted chars: 71 / 280
Intent URL: https://x.com/intent/tweet?text=Big%20news%3A%20our%20open-source...
```

The X composer tab opens in your default browser with the text already filled in. Click **Post**.

---

### 3. Full workflow — text + image (most common use case)

```bash
python scripts/publish_to_x.py \
  --text "WHEELS.NS breakout setup: Base coiling near ₹2507 resistance. ADR 6.8%, ATR ₹152." \
  --image ./charts/WHEELS_NS_chart.png \
  --approve \
  --open \
  --log ./logs/x_audit.jsonl
```

**Terminal output:**

```
Status: OPENED_IN_BROWSER
Weighted chars: 83 / 280
Clipboard: CLIPBOARD_COPIED (powershell-winforms)
Intent URL: https://x.com/intent/tweet?text=WHEELS.NS%20breakout%20setup%3A...
Next step: Press Ctrl+V (Cmd+V on macOS) inside the X composer tab to paste your image!
```

> **What happens next:**
> 1. X opens in your browser with the text pre-filled ✅
> 2. Click inside the tweet text area
> 3. Press **`Ctrl+V`** (Windows/Linux) or **`Cmd+V`** (macOS) — your chart pastes in ✅
> 4. Click **Post** ✅

---

### 4. Interactive approval (no --approve flag needed)

```bash
python scripts/publish_to_x.py \
  --text "My post text here..." \
  --image ./chart.png \
  --interactive \
  --open
```

**Terminal output:**

```
--- POST PREVIEW (83 weighted chars) ---
My post text here...

Approve and open in X composer? [y/N]: y
Status: OPENED_IN_BROWSER
Weighted chars: 83 / 280
Clipboard: CLIPBOARD_COPIED (powershell-winforms)
```

---

### 5. JSON output (for piping into other scripts)

```bash
python scripts/publish_to_x.py \
  --text "Post text here https://example.com" \
  --approve \
  --json
```

**Terminal output:**

```json
{
  "status": "APPROVED_READY",
  "weighted_chars": 50,
  "within_standard_limit": true,
  "warning": null,
  "intent_url": "https://x.com/intent/tweet?text=Post%20text%20here%20https%3A%2F%2Fexample.com",
  "clipboard": null,
  "opened_browser": false
}
```

---

### 6. Read post text from a file

```bash
python scripts/publish_to_x.py \
  --text-file ./drafts/my_post.txt \
  --image ./charts/chart.png \
  --approve \
  --open \
  --log ./logs/audit.jsonl
```

---

### 7. Browser Demo — Zero server, offline

Open `examples/web_composer_demo.html` in any browser:

1. Type or paste your post text
2. Drag and drop any PNG/JPG chart or screenshot
3. Click **"Approve, Copy PNG & Open X ($0)"**
4. Press `Ctrl+V` inside the X tab → your image is there
5. Click **Post**

---

## Clipboard Requirements by OS

| OS | Backend | Install needed? |
|---|---|---|
| **Windows** | PowerShell + `.NET System.Windows.Forms.Clipboard` | ❌ Built-in |
| **macOS** | `osascript` (AppleScript) | ❌ Built-in |
| **Linux (Wayland)** | `wl-copy` | `sudo apt install wl-clipboard` |
| **Linux (X11)** | `xclip` | `sudo apt install xclip` |

If no clipboard backend is detected on Linux, the tool prints `CLIPBOARD_UNSUPPORTED` and continues — you can still attach the image manually in X.

---

## Character Counting — Why It Matters

X's composer counts characters differently than `len()`:

```
"Check this out https://github.com/example/very-long-repo-name"
                 ↑──────────────────────────────────────────────
                 This whole URL is counted as only 23 chars (t.co wraps it)
```

This tool replicates that logic exactly:

```python
# Every http(s) URL is replaced with 23 placeholder chars before counting
count_x_weighted_chars("Hello https://example.com/long/url")
# → 6 ("Hello ") + 23 (URL) = 29 chars  ✅ matches X composer
```

---

## Audit Log Format

Each `--log` append writes one JSONL line per session:

```json
{
  "timestamp_utc": "2026-11-13T02:15:00+00:00",
  "mode": "ZERO_COST_WEB_INTENT",
  "api_cost_usd": 0.0,
  "approved_by_human": true,
  "opened_browser": true,
  "weighted_chars": 83,
  "text_preview": "WHEELS.NS breakout setup...",
  "image_path": "/charts/WHEELS_NS_chart.png",
  "tweet_url": null,
  "intent_url": "https://x.com/intent/tweet?text=..."
}
```

---

## CLI Reference

```
usage: publish_to_x.py [--text TEXT | --text-file FILE]
                        [--image IMAGE]
                        [--approve] [--interactive]
                        [--open]
                        [--log LOG]
                        [--tweet-url TWEET_URL]
                        [--json]

Options:
  --text TEXT          Post text to publish on X
  --text-file FILE     Path to UTF-8 .txt file with post text
  --image IMAGE        PNG/JPG to copy to clipboard for Ctrl+V paste in X
  --approve            Explicit human approval gate (required for --open)
  --interactive        Prompt [y/N] in terminal before opening X
  --open               Open X Web Intent URL in default browser (needs --approve)
  --log FILE           Append JSONL audit record to this file
  --tweet-url URL      Save live tweet URL in audit log
  --json               Print structured JSON output instead of plain text
```

---

## Install as an Agent Skill

```bash
# Workspace-level skill (project-specific)
git clone https://github.com/RadheWankhade01/zero-cost-x-publisher.git \
  .agents/skills/zero-cost-x-publisher

# Global skill (Antigravity / Gemini CLI)
git clone https://github.com/RadheWankhade01/zero-cost-x-publisher.git \
  ~/.gemini/config/skills/zero-cost-x-publisher
```

Once installed, any coding agent that reads `SKILL.md` will automatically know how to use this tool to post to X.

---

## Running Tests

```bash
pytest -v
```

**Expected output:**

```
tests/test_publish_to_x.py::test_weighted_char_count_no_url PASSED
tests/test_publish_to_x.py::test_weighted_char_count_with_url PASSED
tests/test_publish_to_x.py::test_build_intent_url_basic PASSED
tests/test_publish_to_x.py::test_approval_gate_blocks_without_approve PASSED

4 passed in 0.03s
```

---

## Project Structure

```
zero-cost-x-publisher/
├── SKILL.md                        ← Agent skill definition (Antigravity / Claude / Cursor)
├── README.md                       ← This file
├── LICENSE                         ← MIT
├── .gitignore
├── scripts/
│   └── publish_to_x.py             ← Main CLI (zero pip dependencies)
├── examples/
│   └── web_composer_demo.html      ← Offline browser UI demo
└── tests/
    └── test_publish_to_x.py        ← Pytest tests (stdlib only)
```

---

## 🔗 Connected Skills Ecosystem

This tool is part of a modular **Open-Source Content & Intelligence Pipeline**. Each tool works 100% standalone, or combines seamlessly with the others:

```
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│     Safe RSS News Ingestor           │       │       Trading Chart Exporter         │
│  (SSRF-safe news & feeds)            │       │   (High-res headless chart capture)  │
└──────────────────┬───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   ▼                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          QC Tweet & Thread Composer                                 │
│         (Deterministic numeric grounding & anti-hallucination verification)         │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         Publishing Eligibility Gate                                 │
│            (DRAFT ➔ PENDING_REVIEW ➔ APPROVED ➔ PUBLISHED state machine)            │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            Zero-Cost X Publisher                                    │
│             (Web Intent + OS Clipboard PNG Ctrl+V @ $0 API cost)                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                           ▲
                                           │ Orchestrated by
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    FastAPI + Celery + Docker Starter                                │
│             (Production async backend, Redis task queue & PostgreSQL)               │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

| Pipeline Stage | Repository | Purpose |
|---|---|---|
| **1. News Ingestion** | [📰 safe-rss-news-ingestor](https://github.com/peacecoder123/A-production-safe-RSS-Atom-news-aggregator) | Hardened RSS/Atom aggregator that prevents SSRF attacks and strips junk HTML |
| **2. Chart Visuals** | [📊 trading-chart-exporter](https://github.com/peacecoder123/Trading-chart-exporter-Trading-view-alternative-Skill-) | Headless Playwright exporter for TradingView charts & financial visuals |
| **3. AI Content QC** | [✍️ qc-tweet-composer](https://github.com/peacecoder123/Quality-Control-gate-for-AI-drafted-tweets-threads-Ai-Skill-) | Fact-checks AI post drafts against sources, catches fake metrics & splits threads |
| **4. Editorial Gate** | [🚦 publishing-eligibility-gate](https://github.com/peacecoder123/publishing-eligibility-gate) | Content review state machine with audit history preventing unapproved releases |
| **5. $0 Distribution** | [🚀 zero-cost-x-publisher](https://github.com/peacecoder123/zero-cost-X-Twitter-publisher) *(This repo)* | Publishes text + image to X at $0 cost via web intent + clipboard Ctrl+V |
| **6. Backend Engine** | [⚡ fastapi-celery-docker-starter](https://github.com/peacecoder123/Production-ready-FastAPI-Celery-Redis-PostgreSQL-Docker-starter) | Production async backend stack with Celery workers, Redis, and PostgreSQL |

---

## License

MIT — free to use, modify, and distribute.

---

> Built by [Radhe Wankhade](https://x.com/RadheWankhade01) as an open-source contribution.
> Star ⭐ the repo if it saved you from an X API bill!
