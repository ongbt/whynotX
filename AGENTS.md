# AGENTS.md — Hermes Agent Rules

## Hard rules (non-negotiable)

- **NEVER access /mnt/c/ directly.** Only read files staged into the WSL filesystem (e.g. ~/hermes_workspace/). For anything else, ask BT to copy over.
- **Do NOT auto-push/commit/deploy unless explicitly asked.** This includes Cloudflare Pages deploys. All changes stay local until BT says so.

## Presentation conventions

- `why-not-christianity-slides.html`: Bump the version badge (v# · date time SGT) on EVERY edit.
- BT prefers `frontend-slides` (fixed 1920×1080 stage, uniform scaling) over `html-ppt` for tablet-friendly presentations.
- Chose "Verdict" style: dark #12100e bg, gold #c9953c accent, Playfair Display + DM Sans. Low density / speaker-led is default.

## Deploy workflow

- Website deploys must be followed immediately by curling the deployed URL, checking for expected content (not just HTTP 200), and reporting success/failure. Never finish a deploy step without verify.

## User profile

- **Name:** BT Ong
- **Email:** bengtiong@email.com
- **GitHub:** ongbt
- **Timezone:** Asia/Singapore (GMT+8)
- **Windows user:** bengt. File bridge: ~/hermes_workspace/ → C:\Users\bengt\hermes_workspace\. Deliverables (decks, exports) go here.
- Values accuracy over convenience. Short direct commands, action over explanation. Systematic changes: think through side effects, plan, verify after.
- Wants proactive health monitoring with clear resolved vs active distinction.
- Two-phase: review first, then batched implementation.
