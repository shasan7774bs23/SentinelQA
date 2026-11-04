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

## How the process works

Every ticket goes through **six stations**. At **five gates** the agent stops, and **you** decide.

```
 S0 INTAKE ──► S1 UNDERSTAND ──► S2 DESIGN ──► S3 EXECUTE ──► S4 REPORT ──► S5 RELEASE
                    │                │              │              │             │
                 GATE A           GATE B         GATE C         GATE D        GATE E
             requirements      test plan        defects       verdict &      go / no-go
              sign-off         approval        validation      filing
```

| Station | What happens | Output (in `qa/<TICKET>/`) |
|---|---|---|
| **S0 Intake** | Confirms ticket, branch, environment, **the build actually deployed**, account, re-test or not. Sets the stakes tier (1–3) and the risk score | `00-intake.yml` |
| **S1 Understand** | Turns the real acceptance criteria into numbered IF/THEN rules, finds gaps, asks precise questions | `01-requirement.md` |
| **S2 Design** | The complete test suite for the tier, self-reviewed by a second model. Then the case-file audit | `02-plan.md` |
| **S3 Execute** | **Pass 1:** predict from the code (write-once). **Pass 2:** run it live with screenshots. Reconcile the two | `03-pass1.md`, `04-evidence/` |
| **S4 Report** | Full report from the template, checked by the closeout audit, delivered as `.md` + `.html` | `05-report.md` |
| **S5 Release** | `release-gate` rolls up every ticket in a fix-version. A ticket with no report is UNKNOWN, never a pass | release report |

| Gate | The question you answer |
|---|---|
| **A** | Are these the right business rules, and are the gaps real? |
| **B** | Is this the right test coverage? (approve, or reject with reasons) |
| **C** | Is each candidate really a defect, at this severity and priority? |
| **D** | Do you sign this verdict, and what gets filed? (each Jira write approved separately) |
| **E** | Knowing what was not tested, do we ship? |

All five gates fire on **every** ticket. The tier changes how much gets *tested*, never how many
*decisions* are yours. Every decision is logged in `06-decisions.md`.

📖 **Full walkthrough, with the reason behind every rule: [docs/PROCESS.md](docs/PROCESS.md)**

## Which tool when

| You want to… | Use |
|---|---|
| QA one ticket, step by step, approving each gate as you go | `/qa-case <TICKET-KEY>` |
| Hand a ticket to an agent that works on its own until it hits a gate | "use the qa-functional subagent for <TICKET-KEY>" |
| Ask whether something you saw is really a bug, or review a test suite | Just ask. The `qa-functional` skill loads by itself |
| Write, run or debug automated tests | `/qa-automate <what you need>` |
| Decide whether a fix-version can ship | "is fix-version <X> ready to ship?" (loads `release-gate`) |

## Prerequisites

1. **Claude Code** installed and signed in.
2. **Python 3.10+** on your `PATH` as `python`. Check with `python --version`.
   - **Windows:** if `python` opens the Microsoft Store or isn't found but `py` works, reinstall
     Python from python.org with **"Add python.exe to PATH"** ticked. Or turn off the `python.exe`
     alias under *Settings → Apps → Advanced app settings → App execution aliases*.
3. **Git** installed (Claude Code uses it to download the plugin). The repo is public, so no
   GitHub login or invitation is needed. On Windows, Git for Windows also provides Git Bash,
   which Claude Code and the agents use to run commands.
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

## Settings for identical behaviour

SentinelQA behaves the same on every machine only if these match. Set them once:

| Setting | Use | Why |
|---|---|---|
| **Model** | Both agents are pinned to **Opus**. Run your main session on Opus too: `/model opus` | Defect calls and verdicts need the strongest model; a weaker one changes results |
| **Effort** | `/effort` → **xhigh** (or `"effortLevel": "xhigh"` in `~/.claude/settings.json`) | Deeper reasoning on gates, reconciliation and reports |
| **Claude Code version** | Keep it updated (`claude update`). Tested on 2.1.318 | The skill relies on recent plugin features |
| **Git-write guard** | Turn it on (see *Optional: git-write guard* below) | Claude asks before every commit/push, matching the lead's setup |
| **Permission mode** | Your choice. In the default mode Claude asks before each action; *auto* mode asks less | Same logic either way, only fewer prompts |
| **Project context** | Load your project's layer: its `CLAUDE.md`, the known-findings ledger at `.claude/qa/known-findings.md`, and any team context pack you were given | The method reads the project layer first (Step 0b); without it, already-ruled-out issues get raised again |

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

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/qa-case` doesn't appear after installing | Restart Claude Code. Then run `/plugin`: SentinelQA should show as installed and enabled. If it's disabled, enable it there |
| `/plugin marketplace add` fails | Check that `git --version` works and that you can open github.com. Then retry |
| Audit scripts fail with "python not found" | See the Windows note under Prerequisites. `python --version` must work in a new terminal |
| The agent says it can't read the ticket | Connect the Atlassian connector in Claude, or paste the ticket text (description **and** comments) into the chat |
| The agent says Level 1 or 2 and can't execute tests | No browser tool is connected. Add the Playwright MCP server (see Prerequisites) and restart |
| A report landed in `QA-Reports/_Unsorted` | The file name had no ticket key. Re-publish with `--project <NAME>` |
| Updates don't show up | `/plugin marketplace update sentinelqa`, then restart Claude Code |

## Changing the process

Do not edit your installed copy, because the next update overwrites it. To propose a change,
open an issue on this repo: what you would change, and the run that showed why.
