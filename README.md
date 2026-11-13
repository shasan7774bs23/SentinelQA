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
| `/qa-setup` · `/qa-automate` · `/qa-case` · `/qa-init` | One-time machine setup for all your projects · automation work · the same as `/qa-functional` · add or update one project | Type them in Claude Code |
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
| Set SentinelQA up on a new machine (once, all projects) | **`/qa-setup`** |
| **QA one ticket end to end, including live testing** (the normal way) | **`/qa-functional <TICKET-KEY>`** |
| Get the analysis and test plan prepared in the background first | "use the qa-functional subagent for <TICKET-KEY>", then `/qa-functional <TICKET-KEY>` to test. It continues from the agent's case file |
| Ask whether something you saw is really a bug, or review a test suite | Just ask. The `qa-functional` skill loads by itself |
| Write, run or debug automated tests | `/qa-automate <what you need>` |
| Decide whether a fix-version can ship | "is fix-version <X> ready to ship?" (loads `release-gate`) |

## Prerequisites (each machine)

`/qa-setup` checks all of these for you and tells you exactly what to fix.

| # | Needed | Why | Check | Fix |
|---|---|---|---|---|
| 1 | **Claude Code** 2.1.318 or newer, signed in | Runs everything | `claude --version` | `claude update` |
| 2 | **Opus** available on your plan | Both agents are pinned to Opus; verdicts need it | `/model opus` | Ask your admin for a plan with Opus |
| 3 | **Python 3.10+** on `PATH` | The audit, report and setup scripts | `python --version` | python.org, tick **"Add python.exe to PATH"**. On Windows, if `python` opens the Microsoft Store, turn off the alias under *Settings → Apps → Advanced app settings → App execution aliases* |
| 4 | **Git** (on Windows, **Git for Windows**, which includes Git Bash) | Downloads the plugin; Claude Code runs commands through Git Bash | `git --version` | git-scm.com |
| 5 | **Node.js 18+** (LTS) | Runs the browser SentinelQA installs for live testing | `node --version` | nodejs.org, then restart Claude Code |
| 6 | **Jira connector: "Atlassian Rovo"** | Reads tickets, comments and linked tickets (read-only) | Claude settings → Connectors | Connect **Atlassian Rovo**. The older "Atlassian" connector is being shut down by Atlassian (*"deprecated HTTP+SSE transport"*) and can't read tickets. Without any connector, paste the ticket text |
| 7 | *Optional:* Jira API credentials as environment variables | Lets SentinelQA read ticket **attachments** (DB scripts, specs) | — | Jira Cloud: `JIRA_EMAIL` + `JIRA_API_TOKEN` (create at *id.atlassian.com → Security → API tokens*). Server/Data Center: `JIRA_PAT`. Never paste a token into the chat |

No GitHub account or invitation is needed: the repo is public.

**Operating systems:** tested on **Windows 11**. macOS and Linux should work (the scripts fall back
from `python` to `python3`), but have not been tested yet; please report anything that breaks.

## Install (3 steps, once per machine)

**1. Add and install the plugin** (inside Claude Code):

```
/plugin marketplace add shasan7774bs23/SentinelQA
/plugin install sentinelqa@sentinelqa
```

**2. Restart Claude Code.** Check: `/qa-functional` appears when you type `/qa`, `/agents` lists
`qa-functional` and `lead-test-automation-engineer`, and `/mcp` lists SentinelQA's `playwright` server.

**3. Run `/qa-setup` once.** It takes about 5 minutes and covers **all** your projects:
- checks every prerequisite above and tells you the fix for anything missing;
- asks, in one message, about each project you test: ticket prefix, Jira site, local folder, whether
  QA can see the source code, whether QA files may be written in the repo (if not, where they go
  instead), test environments and how to confirm the deployed build, and test accounts **by role**
  (where each login is kept, never the login itself; see *Test logins* below);
- offers to add SentinelQA's permission rules to your user settings, so QA runs stop asking before
  every step;
- saves it all to `~/.sentinelqa/projects.json` (no secrets; it refuses anything that looks like one).

After that, `/qa-functional <TICKET-KEY>` works in every saved project without asking again for
anything you told it. Re-run `/qa-setup` (or `/qa-init` inside one project folder) to add or change
a project.

## Settings for identical behaviour

SentinelQA behaves the same on every machine only if these match. Set them once:

| Setting | Use | Why |
|---|---|---|
| **Model** | Both agents are pinned to **Opus**. Run your main session on Opus too: `/model opus` | Defect calls and verdicts need the strongest model; a weaker one changes results |
| **Effort** | `/effort` → **xhigh** (or `"effortLevel": "xhigh"` in `~/.claude/settings.json`) | Deeper reasoning on gates, reconciliation and reports |
| **Claude Code version** | Keep it updated (`claude update`). Tested on 2.1.318 | The skill relies on recent plugin features |
| **Git-write guard** | Turn it on (see *Optional: git-write guard* below) | Claude asks before every commit/push, matching the lead's setup |
| **Permission rules** | Say **yes** when `/qa-setup` offers them (once per machine, all projects). Not needed in *auto* permission mode | In the default permission mode, Claude otherwise asks before nearly every step: reading the plugin's own templates, saving each case-file file, running each audit. In a test, the rules cut those prompts from 6 to 0 |
| **Project profile** | Run `/qa-setup` once; accept its offer at the end of a run to save anything new | Every ticket in that project then asks only what's new, exactly as on the lead's machine |

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

## Test logins: where SentinelQA finds them

SentinelQA never stores a password. `/qa-setup` records, per role, **where** the login is kept. Two
forms are checked before every run and then used without asking:

| Form | Example | Notes |
|---|---|---|
| A credentials file you keep **outside any repo** (recommended) | `file:C:/Users/me/qa-secrets/test-accounts.json#admin` | JSON (`{"admin": {"user": "...", "password": "..."}}`), `.env` (`ADMIN_PASS=...`) or text. You can fix it mid-session; no restart |
| Environment variables | `env:QA_ADMIN_USER,QA_ADMIN_PASS` | Claude Code only sees variables that existed when it started: restart after setting them |

A password-manager entry can be recorded too, but then SentinelQA asks for the login at each run. A
login is only ever typed into the **test application's** login form. It is never written into a case
file, report or screenshot, and SentinelQA never logs you in or out of Claude, Jira or Git.

## First run, start to finish

1. Open Claude Code **in the project folder** you are testing (one you saved in `/qa-setup`). If you
   start it somewhere else, SentinelQA tells you which folder the ticket's project is in, so you can
   reopen there (or continue without the source code).
2. Run **`/qa-functional ABC-123`** (use your real ticket key).
3. Claude reads your saved project details, reads the ticket, checks what this session has (Jira,
   attachments, source code, environment, accounts, browser, Python), and creates the case file:
   `qa/ABC-123/` in the repo, or in your external case folder for a read-only repo (then nothing at
   all is written in the repo). For an in-repo case folder, a one-line `qa/.gitignore` keeps it out of
   git, so it never shows up as a change to commit.
   **Before testing starts it checks everything the run needs:** the project folder, the ticket, the
   test environment (one request; production is never contacted) and each role's login (one test
   login per role). Then it asks **one** message with everything it couldn't find or that failed.
   Answer what you can; for anything you can't provide, say no and it continues with what exists.
   After that the test runs through; if something unexpected breaks mid-run, those cases are marked
   *Not executed* with the reason, and the rest carries on.
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
or saved. Without it, SentinelQA asks you once to drop the files into the case folder's `attachments/`, or
continues and lists them as *Not reviewed* in the report.

**Per-project memory.** The method reads each project's own `CLAUDE.md` and its known-findings
ledger (`.claude/qa/known-findings.md` in the repo, or `known-findings.md` in the external case folder
for a read-only project). The template is in
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
- Production is never tested. Passwords are never printed, stored or committed.
- Test browsers it opens are closed when the run ends.
- Before starting several agents at once it tells you what would run and on which model, and waits
  for your yes (cost control). Commits it makes carry your name only.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/qa-functional` doesn't appear after installing | Restart Claude Code. Then run `/plugin`: SentinelQA should show as installed and enabled. If it's disabled, enable it there |
| `/plugin marketplace add` fails | Check that `git --version` works and that you can open github.com. Then retry |
| Audit scripts fail with "python not found" | See the Windows note under Prerequisites. `python --version` must work in a new terminal |
| The agent says "No Jira tool in this session" | Connect **Atlassian Rovo** in Claude's settings, then restart Claude Code. Or paste the ticket text (description **and** comments) |
| Atlassian Rovo warns about a "deprecated V1 endpoint" (removed 2027-03-01) | In Claude settings → Connectors, remove Atlassian Rovo and add it again from the directory (or ask your admin if your organisation manages it). Nothing in SentinelQA changes |
| "deprecated HTTP+SSE transport … is being phased out" | You're on the older "Atlassian" connector, which Atlassian is retiring. Add **Atlassian Rovo** in Claude's settings → Connectors, then restart |
| The `qa-functional` agent returned a plan but ran no tests | That is its job. Run `/qa-functional <KEY>` next: it continues from the same case file and runs the live tests |
| `/qa-functional` can't execute tests | SentinelQA's browser didn't start. Check `node --version` (install Node.js LTS if missing), restart Claude Code, then check `/mcp`. Until then it tests over HTTP where it can |
| `/qa-functional` keeps asking about environments or accounts | Run `/qa-setup` once (or `/qa-init` in that project folder) so they're saved |
| "`ABC-123` belongs to *Project*, whose code is at …" | You started Claude Code in another folder. Open it in that folder and run the command again, or reply *continue here* to test without the source code |
| "Where is *Project* on this machine now?" | The saved folder was moved or renamed. Give the new path once; it is saved |
| A login is reported missing although you set the variable | Restart Claude Code (it reads environment variables only at start), or use a credentials file instead |
| An environment "did not answer" | Check the VPN / that the environment is up, or name another environment |
| Setup says a prerequisite is MISSING | Follow the fix it prints, restart Claude Code, run `/qa-setup` again; it keeps what you already saved |
| Claude asks for permission at almost every step | Run `/qa-setup` and say yes to the permission rules, or add the list in `skills/qa-functional/references/permission-rules.md` to `~/.claude/settings.json` |
| Attachments listed as "Not reviewed" | Set the Jira token (*Optional configuration*), or drop the files into the case folder's `attachments/` and say so |
| `qa/` shows up in `git status` | Create `qa/.gitignore` containing a single `*` line. If the repo must stay untouched, re-run `/qa-setup` and mark the project read-only |
| A report landed in `QA-Reports/_Unsorted` | The file name had no ticket key. Re-publish with `--project <NAME>` |
| Updates don't show up | `/plugin marketplace update sentinelqa`, then restart Claude Code |

## Changing the process

Do not edit your installed copy, because the next update overwrites it. To propose a change,
open an issue on this repo: what you would change, and the run that showed why.
