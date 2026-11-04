# SentinelQA

**No proof, no pass.** A gated, evidence-first QA process for Claude Code, packaged as one plugin: every
ticket runs through the same stations and gates, and every claim in a report is backed by
evidence.

## What you get

| Piece | What it does | How to use it |
|---|---|---|
| `qa-functional` skill | The full method: S0 triage → requirement analysis → test design → two-pass verification → report, with five human gates | Ask Claude to QA a ticket, or run `/qa-case <TICKET-KEY>` |
| `qa-functional` agent | A senior functional QA engineer that runs the method on its own and stops at every gate | "use the qa-functional subagent for ABC-123" |
| `lead-test-automation-engineer` agent | Builds, runs and debugs real automated tests in the project's own stack | `/qa-automate <request>` |
| `release-gate` skill | Rolls up per-ticket QA reports into one release go/no-go | "is fix-version 2.4.0 ready to ship?" |
| `/qa-case`, `/qa-automate` | Slash commands that start the two workflows above | Type them in Claude Code |
| Audit scripts | `case-file-audit.py` proves the stations ran; `report-audit.py` proves the report is complete | The skill and agents run them automatically |
| `report-shelf.py` | Files every finished report under `~/Downloads/QA-Reports/<PROJECT>/` with a newest-first index | Run automatically at the end of a QA run |

## Prerequisites

1. **Claude Code** installed and signed in.
2. **Python 3.10+** on your `PATH` as `python`. Check with `python --version`.
3. **Git** installed (Claude Code uses it to download the plugin). The repo is public, so no
   GitHub login or invitation is needed.
4. **Optional, recommended:**
   - The **Atlassian (Jira/Confluence) connector** in Claude, so the agents can read tickets
     (read-only). Without it, paste the ticket text into the chat.
   - The **Playwright MCP server** for browser testing:
     `claude mcp add playwright -- npx @playwright/mcp@latest`

## Install (2 commands, inside Claude Code)

```
/plugin marketplace add shasan7774bs23/SentinelQA
/plugin install sentinelqa@sentinelqa
```

Restart Claude Code. Then check it worked: `/qa-case` should appear when you type `/qa`, and
`/agents` should list `qa-functional` and `lead-test-automation-engineer`.

## Update

```
/plugin marketplace update sentinelqa
```

Then restart Claude Code. Each update is announced with a short note on what changed.

## Uninstall

```
/plugin uninstall sentinelqa@sentinelqa
```

Nothing outside the plugin is touched, except the reports you published to
`~/Downloads/QA-Reports/` (those are yours to keep).

## First run, start to finish

1. Open Claude Code **in the project repo** you are testing.
2. Run `/qa-case ABC-123` (use your real ticket key).
3. Claude creates `qa/ABC-123/` (the case file) and starts at S0. Answer its run-context
   questions: ticket, branch, deployed site, build, test account, scope.
4. At each gate it **stops and waits for you**. Approve, or reject with a reason.
5. At the end you get `ABC-123-QA-Report.md` plus a self-contained `.html` with screenshots, both
   audited, and both filed on the report shelf.

## Optional configuration

**Report shelf location.** The default is `<your home>/Downloads/QA-Reports`. To change the base
folder, set the `SENTINELQA_DOWNLOADS_DIR` environment variable.

**Project names on the shelf.** By default, `ABC-123-QA-Report.html` is filed under a project
folder named `ABC`. To give a ticket prefix a friendlier name, create
`~/.sentinelqa/projects.json`:

```json
{
  "ticket_prefixes": { "ABC": "ABC-Web", "ABCAPI": "ABC-API" }
}
```

**Per-project memory.** The method reads each project's own `CLAUDE.md` and its known-findings
ledger at `.claude/qa/known-findings.md`. The template is in
`skills/qa-functional/templates/known-findings-ledger.md`. Start one per project, so a finding
that was already investigated is never raised twice.

## Optional: git-write guard

`extras/hooks/block-git-writes.js` makes Claude **ask before** any git commit, push, reset,
branch or tag command, and any `gh` write command. Read-only git stays allowed. It is **not**
switched on by the plugin, because it applies to every repo you open. To opt in, copy it to
`~/.claude/hooks/` and add this to `~/.claude/settings.json` (it needs Node.js):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          { "type": "command", "command": "node ~/.claude/hooks/block-git-writes.js" }
        ]
      }
    ]
  }
}
```

## Ground rules the process enforces

- Acceptance criteria come from the real spec, decomposed into numbered rules.
- Coverage is a ratio ("18 of 26"), never an adjective.
- The build under test is confirmed by server behaviour, with a negative control.
- Pass 1 predictions are written **before** execution and never edited.
- Every executed case, passes included, has Steps / Expected / Actual / Evidence and a screenshot.
- No bug carries a severity unless it was reproduced.
- Agents **never** file tickets, comment, commit or push on their own. They draft; you decide.

## Changing the process

Do not edit your installed copy, because the next update overwrites it. To propose a change,
open an issue on this repo: what you would change, and the run that showed why.
