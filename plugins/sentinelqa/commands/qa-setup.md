---
description: ONE-TIME machine setup for SentinelQA — checks every prerequisite, collects all your projects in one go, and saves them so /qa-functional works in every project without asking again. Re-run any time to add or change a project.
---

Set SentinelQA up on **this machine, for all of this person's projects, once**. After this, typing
`/qa-functional <TICKET-KEY>` in any of their projects must work without per-project setup and
without asking again for anything recorded here.

Extra input (may be empty, may already hold answers, or `--yes` to skip the final approval): $ARGUMENTS

`SETUP` below means `python ${CLAUDE_PLUGIN_ROOT}/skills/qa-functional/scripts/sentinelqa-setup.py`.
If `${CLAUDE_PLUGIN_ROOT}` is not expanded, load the `sentinelqa:qa-functional` skill and use its base
directory instead. If `python` does not work, try `py -3`, then `python3`, and use whichever works.

## Ground rules

- **Run each `SETUP` command as its own tool call**: no `;`, `&&`, pipes, heredocs or variables in
  front of it. A plain single command is what the permission rules (and the person's one-time
  approvals) match.

- **Never ask for, store or print a password, token or key.** Accounts are recorded as role +
  WHERE the credential lives (a vault name, an env var name). `SETUP import` refuses secrets anyway.
- **Never run a login or re-authentication command**, and never ask the person to log in. A
  connector that needs authentication is reported as missing, with the fix.
- **One conversation, not an interrogation.** One message with everything you need; then at most
  one follow-up for answers that are missing or contradictory.
- Nothing is written before the person approves the summary (unless `$ARGUMENTS` has `--yes`).
- Never commit or push anything.

## Step 1 — Check the machine (silently)

1. Run `SETUP doctor`. It checks Python, Git, Git Bash (Windows), Node.js and npx (needed for the
   browser SentinelQA installs), the Claude Code version, any saved profile and permission decision,
   the optional Jira attachment credentials, and the report-shelf folder.
2. Check inside this session yourself:
   - **Jira:** is any tool ending in `getJiraIssue` available? Which connector (Atlassian Rovo /
     Atlassian / local)? If one exists, call its `getAccessibleAtlassianResources` to read the site(s).
     If it fails with *"deprecated HTTP+SSE transport"*, the old "Atlassian" connector is being
     retired: the fix is to add **Atlassian Rovo** in Claude settings → Connectors.
   - **Browser:** are `mcp__plugin_sentinelqa_playwright__browser_*` tools available? (If not, Node.js
     is usually the cause; the fix is in the doctor output, then restart Claude Code.)
   - **Model:** both agents are pinned to Opus. Note the session's model.
3. Run `SETUP show` to see any profile already saved (a re-run updates it; never drop a project the
   person did not ask to remove).

## Step 2 — One message: what's missing, and everything about their projects

Start with a short **readiness table**: each prerequisite as ✅ / ❌ / ⚠️ with the exact fix for anything
not ✅. For each ❌, ask: *"Will you fix this now? (yes / no — SentinelQA works without it, but <what is
lost>)"*.

Then ask, numbered, skipping anything already known from the profile or from `$ARGUMENTS`:

**About you (once)**
1. Your name, as it should appear as reviewer at the QA gates.
2. **Permission rules:** add SentinelQA's permission rules to your user settings, so QA runs stop
   asking before each step, in every project? (yes / no). Skip this if the session is in *auto* mode.
3. Optional: will you set `JIRA_EMAIL` + `JIRA_API_TOKEN` (Jira Cloud) or `JIRA_PAT` (Server/Data
   Center) so SentinelQA can read ticket attachments? (Never paste the token here.)

**About each project you test** (repeat the block per project; "same as previous" is fine):
4. Project name, and its **ticket key prefix(es)** (e.g. `ABC` for `ABC-123`).
5. **Is it set up on this machine?** The local folder(s) where you open Claude Code for it (or "not on
   this machine"). Every QA run for this project should be started from that folder.
6. Ticket system and **Jira site** (offer the sites the connector listed in Step 1), and the
   test-management tool if any.
7. **Source code:** is the application's source code available to QA? (this folder / another path / no)
8. **May QA files be written inside the repo?** If not (a review-only repo), where should case files
   and reports live instead? (default: `~/.sentinelqa/cases/<Project>`)
9. **Test environments:** name → URL → which build it normally runs → how to confirm the deployed build
   by server behaviour (a version endpoint, a feature only the new build has). Mark any **production**
   URL as production: SentinelQA never tests it.
10. **Test accounts by role:** role → **where its login is kept**, never the login itself. Two forms
    can be checked and used without asking again:
    - `file:<path>#<key>`: a credentials file **outside any repo** that the person keeps, e.g.
      `file:C:/Users/me/qa-secrets/test-accounts.json#admin` (JSON, `.env` or text). Recommended: it
      can be edited during a session, no restart needed.
    - `env:USER_VAR,PASS_VAR`: environment variables (only seen after Claude Code is restarted).
    Anything else (a password manager) is recorded, but the person will be asked for it at each run.
11. App type (web / API / mobile / desktop) and anything to know: shared accounts, slow environments,
    data that must not be touched, flaky areas.

## Step 3 — Show the summary, then write

Show, in plain English, per project: prefixes, repo folders, source code yes/no, where case files
go, environments (production flagged), accounts by role and credential location. Then ask
*"Save this? (yes / change …)"*.

On yes, in this order (the profile first, so the rules can include its case folders and test hosts):
1. **Profile:** write the JSON with the **Write tool** to `~/.sentinelqa/import.json` (as an absolute
   path; under `$SENTINELQA_HOME` if that is set). Write Windows paths with forward slashes
   (`C:/Work/shop`). Then run `SETUP import <that file>` as one command. Never pass the JSON on the
   command line: Windows shells mangle quotes and backslashes in it. Shape:
   ```json
   {"tester": {"name": "<name>"},
    "projects": [{"name": "<Project>", "ticket_prefixes": ["ABC"], "repo_paths": ["<folder>"],
      "ticket_system": "Jira", "jira_site": "<site>", "test_management": "<tool or none>",
      "app_type": "web", "source_code": {"available": true, "path": "<folder>"},
      "repo_write_policy": "qa-files-ok | read-only", "case_root": "qa | <absolute folder outside the repo>",
      "environments": [{"name": "QA", "url": "<url>", "runs": "<build/branch>", "build_check": "<how>", "production": false}],
      "accounts": [{"role": "<role>", "credential_location": "file:<path>#<key> | env:USER_VAR,PASS_VAR"}],
      "gotchas": ["<one line each>"]}]}
   ```
   It validates the profile, refuses secrets, keeps every other project, and keeps a backup.
2. **Permission rules:** on yes, run `SETUP add-rules` (after the import). It merges the rules into the user settings,
   adds read/write access for any external case folder and `curl` for each non-production test host,
   keeps every existing entry, and keeps a backup. On no, run `SETUP state rules declined`.
3. Nothing else is written: each run creates its own case folder (with a one-line `qa/.gitignore` for
   in-repo case folders). **Never create any file inside a read-only repo.**

## Step 4 — Verify and hand over

Run `SETUP show`, `SETUP doctor` and `SETUP preflight` (all projects: checks that every saved folder
exists, every test environment answers (production is never contacted) and every login location can
be found, without printing any credential). For each Jira prefix, confirm with the connector that the
project is visible on its site (`searchJiraIssuesUsingJql` with `project = <PREFIX>`, 1 result).
Show anything that failed, with its fix, in one list. Then tell the person, briefly:
- what was saved, where (`~/.sentinelqa/projects.json`), and that it holds no secrets;
- anything still missing, with its fix, and what SentinelQA does without it;
- **restart Claude Code** if permission rules were added;
- **how to use it:** open Claude Code in the project's folder and type `/qa-functional <TICKET-KEY>`.
  Each run first checks the folder, the environment and the logins, asks once for anything missing,
  then tests without stopping except at the sign-off gates.
  `/qa-automate` is for test automation. Re-run `/qa-setup` to add or change a project.
