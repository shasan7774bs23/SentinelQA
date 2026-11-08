# SentinelQA

**No proof, no pass.** A gated, evidence-first QA process for Claude Code, packaged as one plugin: every
ticket runs through the same stations and gates, and every claim in a report is backed by
evidence.

## What you get

| Piece | What it does | How to use it |
|---|---|---|
| `qa-functional` skill | The full method, **live browser testing included**: S0 triage → requirement analysis → test design → two-pass verification → report, with five human gates | **`/qa-functional <TICKET-KEY>`** |
| `qa-functional` agent | Background helper: prepares the analysis and complete test plan on its own, then you continue with `/qa-functional` for the live testing | "use the qa-functional subagent for ABC-123" |
| `lead-test-automation-engineer` agent | Builds, runs and debugs real automated tests in the project's own stack | `/qa-automate <request>` |
| `release-gate` skill | Rolls up per-ticket QA reports into one release go/no-go | "is fix-version 2.4.0 ready to ship?" |
| Playwright browser | Installed **with the plugin**, so live testing works in every project with no extra setup (needs Node.js) | Used automatically |
| `/qa-automate` · `/qa-case` · `/qa-init` | Automation work · the same as `/qa-functional` · optional pre-fill of a project's details | Type them in Claude Code |
| Audit scripts | `case-file-audit.py` proves the stations ran; `report-audit.py` proves the report is complete | The skill and agents run them automatically |
| `report-html.py` | Builds the self-contained `.html` report (screenshots embedded, light and dark mode, scrolls in any viewer) from the Markdown report, so every teammate's HTML is identical | The skill runs it automatically |
| `jira-attachments.py` | Downloads the ticket's attachments (DB scripts, specs, screenshots) into the case file | Automatic, if you set the optional Jira token (see *Optional configuration*) |
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
| **QA one ticket end to end, including live testing** (the normal way) | **`/qa-functional <TICKET-KEY>`** |
| Get the analysis and test plan prepared in the background first | "use the qa-functional subagent for <TICKET-KEY>", then `/qa-functional <TICKET-KEY>` to test. It continues from the agent's case file |
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
   - A **Jira connector**, so the agents can read tickets (read-only). Use **"Atlassian Rovo"**
     (Claude settings → Connectors). SentinelQA uses whichever Jira connector you have, including
     the older **"Atlassian"** one or a locally added server named `atlassian`. **But Atlassian is
     shutting down the older "Atlassian" connector:** it now answers *"deprecated HTTP+SSE transport
     … is being phased out"* and can't read tickets. If you have only that one, add "Atlassian Rovo".
     Without any connector, paste the ticket (description **and** comments) into the chat.
   - **Node.js** (LTS), for the browser that SentinelQA installs. Check with `node --version`.
     Without it, testing falls back to HTTP checks and visual cases are marked Not Executed.

## Install (2 commands, inside Claude Code)

```
/plugin marketplace add shasan7774bs23/SentinelQA
/plugin install sentinelqa@sentinelqa
```

Restart Claude Code. Then check it worked: `/qa-functional` should appear when you type `/qa`,
`/agents` should list `qa-functional` and `lead-test-automation-engineer`, and `/mcp` should list
SentinelQA's `playwright` server.

**That's the whole setup: once per machine, for every project.** There is nothing to set up per
project. The first time you run `/qa-functional`, it offers once to add SentinelQA's permission rules
to your user settings, so it stops asking before each step, in every project.

## Settings for identical behaviour

SentinelQA behaves the same on every machine only if these match. Set them once:

| Setting | Use | Why |
|---|---|---|
| **Model** | Both agents are pinned to **Opus**. Run your main session on Opus too: `/model opus` | Defect calls and verdicts need the strongest model; a weaker one changes results |
| **Effort** | `/effort` → **xhigh** (or `"effortLevel": "xhigh"` in `~/.claude/settings.json`) | Deeper reasoning on gates, reconciliation and reports |
| **Claude Code version** | Keep it updated (`claude update`). Tested on 2.1.318 | The skill relies on recent plugin features |
| **Git-write guard** | Turn it on (see *Optional: git-write guard* below) | Claude asks before every commit/push, matching the lead's setup |
| **Permission rules** | Say **yes** when the first run offers them (once per machine, all projects). Not needed in *auto* permission mode | In the default permission mode, Claude otherwise asks before nearly every step: reading the plugin's own templates, saving each case-file file, running each audit. In a test, the rules cut those prompts from 6 to 0 |
| **Project memory** | At the end of a run, accept the proposed memory entries (environments, accounts, how to confirm the build) | The next ticket in that project then asks only what's new, exactly as on the lead's machine |

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
2. Run **`/qa-functional ABC-123`** (use your real ticket key).
3. Claude reads the ticket, checks what this session has (Jira, attachments, source code,
   environment, accounts, browser, Python), and creates `qa/ABC-123/`. Two one-line `.gitignore`
   files (in `qa/` and in the browser tool's `.playwright-mcp/` folder) keep them out of git, so it never shows
   up as a change to commit. Then it asks **one** message with
   everything it couldn't find. Answer what you can. For anything you can't provide, say no and it
   continues with what exists.
   - **No source code available to QA?** Confirm that, and it tests from the requirement and the
     live application: browser, HTTP and API, roles, boundaries.
4. At each gate it **stops and waits for you**. Approve, or reject with a reason.
5. At the end you get `ABC-123-QA-Report.md` plus a self-contained `.html` with screenshots, both
   audited, and both filed on the report shelf. It then proposes what to remember about this
   project, so the next ticket asks less.

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

**Jira attachments (optional).** To let SentinelQA download the ticket's attachments (DB scripts,
specs, screenshots), set two environment variables. On Jira Cloud these are `JIRA_EMAIL` and
`JIRA_API_TOKEN`; create the token at *id.atlassian.com → Security → API tokens*. On Jira Server or
Data Center, set `JIRA_PAT` instead. The token is read from the environment only, and never printed
or saved. Without it, SentinelQA asks you once to drop the files into `qa/<KEY>/attachments/`, or
continues and lists them as *Not reviewed* in the report.

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
| `/qa-functional` doesn't appear after installing | Restart Claude Code. Then run `/plugin`: SentinelQA should show as installed and enabled. If it's disabled, enable it there |
| `/plugin marketplace add` fails | Check that `git --version` works and that you can open github.com. Then retry |
| Audit scripts fail with "python not found" | See the Windows note under Prerequisites. `python --version` must work in a new terminal |
| The agent says "No Jira tool in this session" | Connect **Atlassian Rovo** in Claude's settings, then restart Claude Code. Or paste the ticket text (description **and** comments) |
| "deprecated HTTP+SSE transport … is being phased out" | You're on the older "Atlassian" connector, which Atlassian is retiring. Add **Atlassian Rovo** in Claude's settings → Connectors, then restart |
| The `qa-functional` agent returned a plan but ran no tests | That is its job. Run `/qa-functional <KEY>` next: it continues from the same case file and runs the live tests |
| `/qa-functional` can't execute tests | SentinelQA's browser didn't start. Check `node --version` (install Node.js LTS if missing), restart Claude Code, then check `/mcp`. Until then it tests over HTTP where it can |
| Claude asks for permission at almost every step | Say yes when `/qa-functional` offers SentinelQA's permission rules, or add the list in `skills/qa-functional/references/permission-rules.md` to `~/.claude/settings.json` |
| Attachments listed as "Not reviewed" | Set the Jira token (*Optional configuration*), or drop the files into `qa/<KEY>/attachments/` and say so |
| `qa/` or `.playwright-mcp/` shows up in `git status` | Create `qa/.gitignore` (and `.playwright-mcp/.gitignore`) containing a single `*` line |
| A report landed in `QA-Reports/_Unsorted` | The file name had no ticket key. Re-publish with `--project <NAME>` |
| Updates don't show up | `/plugin marketplace update sentinelqa`, then restart Claude Code |

## Changing the process

Do not edit your installed copy, because the next update overwrites it. To propose a change,
open an issue on this repo: what you would change, and the run that showed why.
