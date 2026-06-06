# AGENTS.md — Hermes Agent Rules

## Hard rules (non-negotiable)

- **Do NOT auto-push/commit/deploy unless explicitly asked.** All changes stay local until BT says so. (Exception: post-commit hook auto-deploys on commit — that's fine, it's the git hook, not the agent.)
- **Generator reads from `why-not-christianity.xml`** (the single canonical XML source). After editing the XML, always copy it to `~/hermes_workspace/why-not-christianity/why-not-christianity.xml` (to match generator path) and run `python3 ~/hermes_workspace/why-not-christianity/generate_why_not_christianity.py` to regenerate the HTML.

## Presentation conventions

- **Single canonical XML:** `why-not-christianity.xml` (no `-slides` suffix). The generator reads `why-not-christianity.xml` and writes `why-not-christianity.html`.
- **Version:** Bump `<version>` in the XML before regenerating. Generator reads it from XML.
- **Theme:** `theme-verdict-dark` (dark #12100e bg, gold #c9953c accent, Playfair Display + DM Sans). All bottom-line/conclusion cards get `verdict="bad"` for the red left-border styling.
- BT prefers `frontend-slides` (fixed 1920×1080 stage, uniform scaling) over `html-ppt` for tablet-friendly presentations.

## Deploy workflow

- After deploying, curl the deployed URL and check for expected content, then report success/failure.
- Deploy via `git commit` (post-commit hook runs `wrangler pages deploy`) or manually via `bash deploy.sh`.
- Live at: https://whynotx.pages.dev/

## File bridge

- **WSL path:** `~/hermes_workspace/` → **Windows path:** `C:\Users\bengt\hermes_workspace\`
- `/mnt/c/Users/bengt/hermes_workspace/` is the same files as `~/hermes_workspace/` via WSL mount. Either path works.
- Deliverables (decks, exports, HTML) go here.

## User profile

- **Name:** BT Ong
- **Email:** bengtiong@email.com
- **GitHub:** ongbt
- **Timezone:** Asia/Singapore (GMT+8)
- Values accuracy over convenience. Short direct commands, action over explanation.
- Systematic changes: think through side effects, plan, verify after.
- Two-phase: review first, then batched implementation.
- Full substantive text on slides — do NOT auto-condense card content.
