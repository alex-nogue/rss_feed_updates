# RSS → Discord Notifier

Simple Python app that fetches an RSS feed, filters entries by keywords or regular expressions and sends matched new entries to a Discord webhook.

Features

- Parse RSS feeds (feedparser)
- Persist seen entries in `data/seen.json` between runs
- Filters: simple keywords (case-insensitive) and regexes (prefix `r:` in `keywords.txt`)
- Editable keywords via `keywords.txt` in the repo — no redeploy needed
- GitHub Actions workflow example to run hourly and commit `data/seen.json`

Quick start

1. Edit `keywords.txt` (one entry per line; prefix regex with `r:`)
2. Add your Discord webhook URL as a secret in GitHub Actions named `DISCORD_WEBHOOK_URL` or in environment variable `DISCORD_WEBHOOK_URL` when running locally.
3. Run locally:

```bash
python -m rss_notifier.main
```

Or enable the provided GitHub Actions workflow to run hourly. The workflow will attempt to commit `data/seen.json` back to the repo so subsequent runs only process new items.

Files of note

- `keywords.txt` — editable list of keywords/regexes
- `src/rss_notifier` — package source
- `.github/workflows/rss-notify.yml` — example workflow

License: MIT

<!-- Progress update — what I did and next steps

I scaffolded a small Python project that:

fetches the RSS feed (default: https://myanimelist.net/rss/news.xml)
loads editable keywords/regexes from keywords.txt
deduplicates entries using a stored seen.json
filters entries by keywords/regexes
sends matching items to a Discord webhook (placeholder taken from env var DISCORD_WEBHOOK_URL)
includes a GitHub Actions workflow to run hourly and commit the updated seen.json
I added unit tests and ran them in a virtual env; all tests passed (3 passed).

Files added (key ones)

README.md — overview & usage
requirements.txt — dependencies
keywords.txt — editable list of keywords/regexes
Format: one entry per line; prefix with r: for regex lines; lines starting with # are ignored
seen.json — stores seen entry ids and last_run (committed by the workflow)
/home/alex/Projects/Perso_Apps/Manga-Updates/src/rss_notifier/* — package source:
config.py — loads keywords and webhook env placeholder
state.py — JSON-based state persistence and unique entry id maker
rss_fetcher.py — wrapper around feedparser
filters.py — keyword/regex matching logic
discord.py — message builder and webhook sender (uses requests)
main.py — runner that ties everything together
test_filters.py — simple tests for filters
rss-notify.yml — workflow to run hourly and commit seen.json
How keywords are editable without redeploy

Edit keywords.txt directly in the repository (via the GitHub UI, clone + edit, or PR). The GitHub Actions workflow reads that file on each run, so changes take effect on the next scheduled run.
Format recap: plain keywords (case-insensitive substring match) or regex patterns by prefixing a line with r:.
How persistence between runs works (GitHub Actions)

The workflow runs hourly, executes the script, and then stages & commits seen.json if it changed.
The commit is pushed using the workflow runner’s credentials (persist-credentials).
This lets the next run compare against the previous run's seen state.
Note: if you prefer not to commit state to the repo, other options include using external storage (S3, Gist, a small DB) or GitHub Issue/Gist-based storage; I can add that if you prefer.
Secrets and webhook

Locally: set DISCORD_WEBHOOK_URL env var before running.
In GitHub Actions: add a repository secret named DISCORD_WEBHOOK_URL and the workflow sets it into env.
Run locally (quick)

Create and use a python venv, then install deps:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Run:
python -m rss_notifier.main
Or set DISCORD_WEBHOOK_URL to your webhook to actually send messages:
export DISCORD_WEBHOOK_URL='https://discordapp.com/api/webhooks/...'
python -m rss_notifier.main
Notes on behavior and edge cases

Deduplication: entries are considered new when their computed id (link/id/title+published) isn't in seen.json. When a run sees a new entry, it will be added to seen even if it does not match the filter — this prevents repeated re-processing.
If the webhook isn't configured, the script will print a dry-run message and still update seen.json so you don't get duplicates later.
Regex lines are compiled with case-insensitive flag; invalid regexes are ignored quietly.
The feed parser (feedparser) may set a bozo flag on parse errors; we still attempt to read entries.
What I ran and verification

Created files and tests.
Configured the Python environment and installed packages.
Ran pytest with PYTHONPATH=src; result: 3 passed.
Next steps (I can do any or all)

Wire an optional richer Discord embed format (title + description + thumbnail + author).
Add retries and backoff for webhook sends and network issues.
Improve logging (structured logs, file/console).
Replace repo-based state with an alternative store (Gist/S3/DB) if you don't want commits to repo.
Add more feeds and a config file (YAML) to manage multiple feeds.
Add richer tests for parsing and main-run integration (mocking network).
Questions for you (few points)

Do you want the GitHub Actions approach (commit state to the repo) or would you prefer an external store (I can implement Gist or S3)? The current flow commits seen.json.
Do you want to send a single webhook per matched entry (current behavior), or aggregate multiple matches into one message per run?
Any preferred message format for Discord (plain text, embeds, attachments)?
If you'd like, I can now:

Change message format to Discord embeds (nicer formatting).
Implement an alternate state storage (Gist) so the workflow does not commit to the repo.
Add a small CLI arg to run in dry-run mode, or more robust logging.
Which of those would you like me to implement next? -->
