---
description: Set up SentinelQA for the project in the current folder — writes its QA project layer (QA rules section, known-findings ledger, report-shelf name). Run once per project; re-run any time to update.
---

Set up the **SentinelQA project layer** for the project in the current working directory. The
method (the `qa-functional` skill and the agents) is the same on every project; what makes it
strong on *this* project is the project layer it reads first (Step 0b). This command creates it.

Extra input from the user (may be empty, may already contain answers or `--yes`): $ARGUMENTS

## Ground rules for this command

- **Never write a credential** — no passwords, tokens or keys anywhere. Accounts are described by
  **role** plus *where* the credential lives (a vault, a shared file, an env var name).
- **Never commit, push, or create branches.** You only write files; the user decides what to commit.
- **Never rewrite existing content.** Your text lives between the markers
  `<!-- sentinelqa:qa-init:start -->` and `<!-- sentinelqa:qa-init:end -->`. On a re-run, replace only
  what is between them; leave everything else in the file exactly as it is.
- **Show before you write.** Present the full proposed content and wait for an explicit yes, unless
  `$ARGUMENTS` contains `--yes`.

## Step 1 — Inspect first (don't ask what you can find out)

Read, don't assume:
- Is this a git repo? What is the remote? Is there a `CLAUDE.md`, `CLAUDE.local.md`,
  `.claude/qa/known-findings.md`, a `qa/` case-file folder, or existing QA reports?
- The stack: manifest files (`package.json`, `*.csproj`/`*.sln`, `pom.xml`, `build.gradle`,
  `requirements.txt`/`pyproject.toml`, `go.mod`, …) and any test frameworks and automation already present.
- The ticket-key prefix: look at recent branch names and commit messages (e.g. `ABC-123`).
- Does the project's own `CLAUDE.md` forbid commits or writes (a review-only repo)?
- Which tools this session actually has: a browser tool (e.g. Playwright MCP), an API client, a
  ticket-system connector. This decides the capability level the method can reach here.

## Step 2 — Ask ONE batched question for whatever is still unknown

Skip anything already answered in `$ARGUMENTS` or found in Step 1. Number the questions; each must be
answerable in a few words.

1. **Project name** as it should appear on the report shelf, and the **ticket-key prefix(es)**.
2. **Ticket system** (Jira, Azure DevOps, GitHub Issues, Linear, other) and **test-management tool**, if any.
3. **App type**: web, API-only, mobile, desktop, or a mix.
4. **Environments**: name → URL, and which branch/build each normally runs.
5. **How to confirm the deployed build** on each environment, by server behaviour (a version
   endpoint, a build fingerprint, a feature only the new build has). "The footer" alone is not enough.
6. **Test accounts by role**: role → where its credential lives. Never the password itself.
7. **Write rules for this repo**: may QA files be committed here, or is it review-only?
8. **Where QA reports should live** in this repo (or "no convention yet").
9. **Known gotchas** worth recording now: flaky areas, slow environments, shared accounts, data that
   must not be touched. (Optional.)

## Step 3 — Propose (and wait)

Show exactly what you will write:

**A. The QA section**, inside the markers, in this shape:

```markdown
<!-- sentinelqa:qa-init:start -->
## QA (SentinelQA project layer)

- **Project:** <name> · **Ticket prefix:** <ABC> · **Tickets:** <system> · **Test management:** <tool or none>
- **App type:** <web/API/…> · **Execution here:** <named tool, e.g. Playwright MCP> → capability Level <1|2|3>
- **Stack:** <languages / frameworks / test frameworks found>

### Environments
| Env | URL | Normally runs | How to confirm the deployed build |
|---|---|---|---|

### Test accounts (by role — credentials are NEVER written here)
| Role | Where the credential lives |
|---|---|

### Rules for this repo
- <commit rules: e.g. "QA files may be committed" / "review-only: never commit or push">
- QA case files: `qa/<TICKET-KEY>/` · reports: <location>
- Known-findings ledger: `.claude/qa/known-findings.md` — check it before raising anything.

### Known gotchas
- <one line each, or "none recorded yet">
<!-- sentinelqa:qa-init:end -->
```

**B. Where it goes:**
- Into `CLAUDE.md` (create it if missing) — when the team commits project instructions.
- Into **`CLAUDE.local.md`** instead — when the repo is review-only, or the user prefers it private.
  Claude Code loads it automatically. Then also add `CLAUDE.local.md` and `.claude/qa/` to
  `.git/info/exclude`, so they can never be committed by accident.

**C. The known-findings ledger** at `.claude/qa/known-findings.md`, created from the qa-functional
skill's `templates/known-findings-ledger.md` **only if it does not exist** (never overwrite a ledger).

**D. The report-shelf name:** merge `"<PREFIX>": "<Project name>"` into the `ticket_prefixes` object of
`~/.sentinelqa/projects.json` (create the file if missing; keep every existing entry).

Then stop and ask: *"Write these? (yes / change …)"*. Skip the wait only when `$ARGUMENTS` has `--yes`.

## Step 4 — Write, then verify

Write exactly what was approved. Claude Code asks permission before any write inside a `.claude/` folder (the
ledger lives there); that prompt is expected, so tell the user to approve it. Then re-read each file and confirm:
- the markers appear exactly once, and nothing outside them changed;
- no password- or token-like value was written anywhere;
- `projects.json` is valid JSON and still contains every earlier entry.

## Step 5 — Hand over

In plain English:
1. **What was written**, with full paths.
2. **The capability level** this project will run at, and what's missing for Level 3 (e.g. "no browser
   tool: add the Playwright MCP server"). Mobile or desktop apps without a testing tool stay at Level 2.
3. **What makes this project's QA stronger over time (the learning loop):**
   - every investigated non-bug goes into the ledger, so it's never raised twice;
   - after each report, accept the agent's proposed memory entries (environment quirks, account
     gotchas, lessons);
   - re-run `/qa-init` whenever environments, accounts or rules change.
4. **Next step:** `/qa-case <TICKET-KEY>` to run the first ticket.
