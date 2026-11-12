---
name: zero-cost-x-publisher
description: >-
  Publish approved text and PNG images to X (Twitter) at $0 API cost using X Web Intent URLs,
  OS clipboard image copy (Ctrl+V), and human confirmation. Use when the user wants to share a
  tweet, thread post, screenshot, or chart on X without paying for the X API or risking unapproved auto-posting.
author: "Radhe Wankhade (@RadheWankhade01)"
x_profile: "https://x.com/RadheWankhade01"
---

# Zero-Cost X Publisher ($0 API Workflow)

Publish tweets and visual attachments (charts, screenshots, infographics) to X at **\$0 API cost** while guaranteeing a **human-in-the-loop approval step** before opening the X composer.

## When to Use This Skill
- The user wants to post text + an image/PNG to X without an X Developer billing plan or API credits.
- The user wants to preview text, check the 280-character weighted limit, copy an image to the clipboard for instant `Ctrl+V`, and open the pre-filled X composer.
- You need a standalone browser demo or Python CLI that never auto-posts without explicit operator confirmation.

## Workflow Steps

1. **Validate Length & Draft Text**
   - Keep standard free-tier tweets `<= 280` X-weighted characters (every `http://` or `https://` URL counts as `23` chars due to `t.co` wrapping).
   - If using [scripts/publish_to_x.py](./scripts/publish_to_x.py), inspect the text and character count first without `--open`.

2. **Require Explicit Human Approval**
   - **Never** bypass confirmation or trigger posting automatically on behalf of a user.
   - Always present the final text + image path to the user or pass `--approve` only after the user explicitly approves.

3. **Copy PNG to Clipboard + Build Intent URL**
   - Run:
     ```bash
     python scripts/publish_to_x.py --text "Your approved post text" --image path/to/chart.png --approve --open
     ```
   - Or, for a browser workflow, open [examples/web_composer_demo.html](./examples/web_composer_demo.html) directly in any browser.

4. **Paste & Post**
   - In the opened X composer tab, press `Ctrl+V` (or `Cmd+V` on macOS) to attach the copied PNG, review visually, and click **Post**.
   - Optionally pass `--log publish_audit.jsonl` (and later `--tweet-url https://x.com/...`) to maintain a local \$0 publication record.

## Verification
- Confirm `scripts/publish_to_x.py` prints `Intent URL:` cleanly, reports `Status: READY` or `CLIPBOARD_COPIED`, and exits with code `0`.
- Run `pytest` in the repo root to verify URL weighting, approval gates, and clipboard dispatch helpers.

