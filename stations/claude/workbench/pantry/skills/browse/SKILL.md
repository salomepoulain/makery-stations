---
name: browse
description: Browse the live web: load a page, read its content, click and type, search a site, extract links or a YouTube transcript, download a file. Also useful for finding and downloading academic papers (ACM, arXiv, journal sites) where the PDF sits behind a JS-rendered viewer. Runs on a camofox-browser HTTP server installed once globally at ~/camofox-browser, shared across projects. Use whenever a task needs real browser interaction (JS-rendered pages, logins, clicking through a flow), not a plain WebFetch of static HTML.
metadata:
  author: salomepoulain
  source: makery-bakery
---

# Browse the web with camofox-browser

`camofox-browser` (github.com/jo-inc/camofox-browser) is a small HTTP server that drives a real,
anti-detection Firefox instance. It gives back accessibility-tree snapshots with stable element
refs (`e1`, `e2`, ...) instead of raw HTML or screenshots, which is what makes it usable as a
tool: read the snapshot, act on a ref, repeat.

**Credit:** this skill is a thin wrapper around `camofox-browser` by jo-inc
(https://github.com/jo-inc/camofox-browser) — all the actual browser-automation work happens
there, not in this skill.

This skill installs camofox-browser once, globally, at `~/camofox-browser`, the same pattern
as `~/.claude`. Every project using this skill shares that one install instead of each getting
its own copy. The server, its `node_modules`, the ~700MB Camoufox browser binary, and per-user
session storage all live there, not under this skill folder and not scattered into
`~/.cache`/`~/.camofox`.

## 0. Get a server running

```bash
REPO="$HOME/camofox-browser"
CACHE="$REPO/.cache/camoufox"       # Camoufox browser binary lives here
PROFILES="$REPO/.profiles/profiles" # per-user persisted session storage
```

Check if a server is already up:

```bash
curl -sf http://localhost:9377/health && echo "already running"
```

If not: **look for the global install first.** Only clone if it's genuinely missing.

```bash
if [ ! -d "$REPO/.git" ]; then
  git clone https://github.com/jo-inc/camofox-browser.git "$REPO"
  cd "$REPO"

  # Skip the postinstall's own binary download. It ignores CAMOUFOX_INSTALL_DIR
  # and always writes to ~/.cache/camoufox regardless.
  CAMOFOX_SKIP_DOWNLOAD=1 npm install

  # Fetch the Camoufox binary directly into the global cache instead
  CAMOUFOX_INSTALL_DIR="$CACHE" npx camoufox-js fetch
fi
```

Start (or restart) the server:

```bash
cd "$REPO"
CAMOUFOX_INSTALL_DIR="$CACHE" CAMOFOX_PROFILE_DIR="$PROFILES" node bin/camofox-browser.js &
```

If `$REPO/.git` already exists but `$REPO/node_modules` doesn't (e.g. a half-finished prior
setup), just run the `npm install` + `npx camoufox-js fetch` steps above without re-cloning.

Notes:

- **Use `node bin/camofox-browser.js`, not `npx camofox-browser` or executing the bin
  directly.** In a sandboxed shell, directly exec'ing a freshly-installed/downloaded binary can
  fail with `EACCES` even though file permissions look correct. Running it through the `node`
  interpreter sidesteps that.
- If `/health` returns `{"error":"port in use"}`-style startup failure, another instance (maybe
  from a previous session) is already bound to 9377. Check for it before assuming this one is
  live: `curl -sf http://localhost:9377/health`.
- Default base URL is `http://localhost:9377` (override with `CAMOFOX_PORT`).
- When done with the task, kill the process. This is meant to be started per-task and torn
  down after, not left running. (`POST /stop` requires auth and isn't the casual way to do this.)

## Core workflow

1. **Create a tab** → get back a `tabId`.
2. **Navigate** → go to a URL, or use a search macro.
3. **Get a snapshot** → accessibility tree with element refs.
4. **Interact** → click/type using a ref.
5. Repeat 3-4. Refs reset on navigation, so re-snapshot after navigating before using a
   ref again.
6. **Close the tab** (or the whole session) when done.

Every request needs a `userId`, which isolates cookies/storage between callers. Use a stable,
descriptive id (e.g. `"agent1"`) rather than inventing a new one per request. `sessionKey`
optionally groups tabs by conversation/task. Sessions time out after 30 minutes of inactivity.

## API reference

### Tabs

| Method | Endpoint | Notes |
|---|---|---|
| `POST` | `/tabs` | `{"userId", "sessionKey"?, "url"?}` → `{"tabId", "url", "title"}` |
| `GET` | `/tabs?userId=X` | List open tabs |
| `GET` | `/tabs/:id/stats` | Tool calls, visited URLs |
| `DELETE` | `/tabs/:id?userId=X` | Close one tab |
| `DELETE` | `/tabs/group/:groupId` | Close all tabs in a group |
| `DELETE` | `/sessions/:userId` | Close every tab for a user |

### Interaction

| Method | Endpoint | Notes |
|---|---|---|
| `GET` | `/tabs/:id/snapshot?userId=X` | Accessibility tree with refs. `includeScreenshot=true`, `offset=N` for pagination |
| `POST` | `/tabs/:id/navigate` | `{"userId", "url"}` or `{"userId", "macro": "@google_search", "query": "..."}` |
| `POST` | `/tabs/:id/click` | `{"userId", "ref": "e1"}` or `{"userId", "selector": "button.submit"}` |
| `POST` | `/tabs/:id/type` | `{"userId", "ref": "e2", "text": "...", "pressEnter"?: true}` |
| `POST` | `/tabs/:id/press` | Press a single keyboard key |
| `POST` | `/tabs/:id/scroll` | `{"userId", "direction": "down", "amount": 500}` |
| `POST` | `/tabs/:id/wait` | Wait for a selector or a timeout |
| `GET` | `/tabs/:id/links?userId=X&limit=50` | Extract links |
| `GET` | `/tabs/:id/images` | `includeData=true`, `maxBytes`, `limit` |
| `GET` | `/tabs/:id/downloads` | See "Downloads" below |
| `GET` | `/tabs/:id/screenshot` | PNG screenshot |
| `POST` | `/tabs/:id/back` \| `/forward` \| `/refresh` | `{"userId"}` |

### Downloads

Navigating a tab straight to a file URL (e.g. a PDF's `?download=true` link) makes
`page.goto` fail with `"Download is starting"`. That's expected, not a real failure: the tab
still exists and the server has already captured the download server-side. List and fetch it:

```bash
# after navigate errors with "Download is starting":
curl "http://localhost:9377/tabs/$TAB_ID/downloads?userId=agent1"
# -> {"downloads":[{"id":"...","suggestedFilename":"paper.pdf","bytes":123, ...}]}

curl "http://localhost:9377/tabs/$TAB_ID/downloads?userId=agent1&includeData=true&consume=true" \
  | python3 -c "import json,sys,base64; d=json.load(sys.stdin)['downloads'][0]; open(d['suggestedFilename'],'wb').write(base64.b64decode(d['dataBase64']))"
```

`includeData=true` returns base64 file bytes; `consume=true` clears it from the buffer after
read; `maxBytes=N` caps what's returned.

### Academic papers

This is a solid fit for finding and pulling academic sources. Publisher sites (ACM, IEEE,
Springer, arXiv, journal pages behind a DOI) usually render the PDF through a JS viewer rather
than serving it as a plain link, so a static fetch won't get you the text. The pattern that
works:

1. Navigate to the DOI or article URL. Dismiss any cookie banner / access-notice modal from the
   snapshot (`click` on the relevant ref).
2. Look for a "PDF", "Download PDF", or "View with eReader" link in the snapshot, then click it.
3. If it opens an in-page reader, the paper's text (abstract, body, references) shows up
   directly in the next `/snapshot` call, no download needed.
4. To get the actual file bytes, re-snapshot the reader page and find the *page's own* download
   link, not the PDF viewer's built-in save button. ACM's eReader, for example, has a toolbar
   link literally labeled something like "Download PDF - 986.2 KB" with a real `href` (e.g.
   `/doi/pdf/{doi}?download=true`). Click that ref, or `navigate` straight to that href, and use
   the Downloads flow above to pull the bytes.

   Do not try to click a PDF.js/native viewer's own "Save" icon. That one hands off to the
   browser's OS-level file picker instead of firing a page download event, so it won't show up
   in the accessibility snapshot and camofox-browser can't intercept it. If the only save
   affordance you can find is inside the rendered PDF viewer itself rather than the surrounding
   page, look harder for a page-level download link before giving up. If there truly isn't one,
   this site's PDF is inline-only and won't cooperate with the download endpoint.

Only download or save papers you have the right to access: open access, a subscription that
covers you, or similar. Respect the site's terms.

### YouTube transcript

```bash
curl -X POST http://localhost:9377/youtube/transcript \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://www.youtube.com/watch?v=...", "languages": ["en"]}'
```

Fast path uses `yt-dlp`; falls back to a browser-based capture (slower, less reliable) if it's
missing.

### Server / sessions

| Method | Endpoint | Notes |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/start` \| `/stop` | Start/stop the browser engine (auth-gated) |
| `POST` | `/sessions/:userId/cookies` | Import Playwright-format cookies |
| `GET` | `/sessions/:userId/storage_state` | Export persisted storage |
| `DELETE` | `/sessions/:userId/storage_state` | Reset session, delete persisted storage |

Endpoint set drifts over time. If something 404s, check the live spec at
`GET /openapi.json` (or browse `GET /docs`) rather than trusting this list blindly.

## Search macros

Use these in `navigate` instead of constructing a search URL by hand:

`@google_search` · `@youtube_search` · `@amazon_search` · `@reddit_search` · `@reddit_subreddit`
· `@wikipedia_search` · `@twitter_search` · `@yelp_search` · `@spotify_search` ·
`@netflix_search` · `@linkedin_search` · `@instagram_search` · `@tiktok_search` ·
`@twitch_search`

```json
{"userId": "agent1", "macro": "@google_search", "query": "weather today"}
```

`@reddit_search` and `@reddit_subreddit` (query = subreddit name, e.g. `"programming"`) return
Reddit's JSON directly, no HTML parsing needed.

## Element refs

- Refs (`e1`, `e2`, ...) are stable identifiers assigned by the most recent `/snapshot` call.
- Get a snapshot, use a ref in `/click` or `/type`.
- Refs reset on navigation. Always take a fresh snapshot after a page changes before using
  a ref again, or the ref will point at the wrong element (or nothing).

## Example: search and read a result

```bash
curl -X POST http://localhost:9377/tabs \
  -d '{"userId": "agent1", "sessionKey": "task1"}' -H 'Content-Type: application/json'
# -> {"tabId": "abc123", ...}

curl -X POST http://localhost:9377/tabs/abc123/navigate \
  -d '{"userId": "agent1", "macro": "@google_search", "query": "best coffee beans"}' \
  -H 'Content-Type: application/json'

curl "http://localhost:9377/tabs/abc123/snapshot?userId=agent1"
# -> "[link e3] Best Coffee Beans 2026 - ..."

curl -X POST http://localhost:9377/tabs/abc123/click \
  -d '{"userId": "agent1", "ref": "e3"}' -H 'Content-Type: application/json'

curl "http://localhost:9377/tabs/abc123/snapshot?userId=agent1"
# fresh refs for the loaded page, read this before clicking again

curl -X DELETE "http://localhost:9377/tabs/abc123?userId=agent1"
```
