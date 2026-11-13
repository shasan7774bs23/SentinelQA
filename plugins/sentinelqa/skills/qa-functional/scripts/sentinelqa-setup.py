"""sentinelqa-setup.py — one-time machine setup and the per-machine project profile.

SentinelQA is set up ONCE per machine, for ALL of a person's projects. This script does the
mechanical part so it is identical on every machine; the /qa-setup command holds the conversation.

Subcommands
    doctor [--json]                  check every prerequisite; prints OK / MISSING / WARN with the fix
    show                             summarise the saved profile (never prints anything secret)
    match [--cwd PATH] [--ticket K]  which saved project applies here (JSON); used by every QA run
    import --json '<json>'           merge a profile or one project into the saved profile
                                     (also: import <file>, or import - to read stdin)
    add-rules [--settings PATH]      merge SentinelQA's permission rules into the user's Claude settings
    state rules added|declined       record the permission-rules answer for this machine
    state show

Where things live
    profile   $SENTINELQA_HOME/projects.json   (default ~/.sentinelqa/projects.json)
    state     $SENTINELQA_HOME/state.json
    settings  --settings PATH, else $CLAUDE_CONFIG_DIR/settings.json, else ~/.claude/settings.json

The profile NEVER holds a password, token or key: `import` refuses anything that looks like one.
Accounts are stored as role + WHERE the credential lives (a vault, an env var name).
Standard library only.
"""
import argparse
import datetime
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_MD = os.path.join(HERE, "..", "references", "permission-rules.md")
HOME = os.environ.get("SENTINELQA_HOME") or os.path.join(os.path.expanduser("~"), ".sentinelqa")
PROFILE = os.path.join(HOME, "projects.json")
STATE = os.path.join(HOME, "state.json")
MIN_CLAUDE = (2, 1, 318)

SECRET_KEY = re.compile(r"(^|[_\-])(password|passwd|pwd|secret|api[_-]?key|private[_-]?key|credential_value)$"
                        r"|^(token|access_token|auth_token|bearer)$", re.I)
SECRET_VALUE = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|ATATT3[A-Za-z0-9_\-=]{20,}"
    r"|eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY"
    r"|\b(password|passwd|pwd)\s*[:=]\s*[^\s,;]{6,}(?=\s|$))", re.I)


# ----------------------------------------------------------------------------- helpers
def read_json(path, default):
    if not os.path.exists(path):
        return default
    with io.open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def backup(path):
    if os.path.exists(path):
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        dst = "%s.sentinelqa-backup-%s" % (path, stamp)
        n = 2
        while os.path.exists(dst):
            dst = "%s.sentinelqa-backup-%s-%d" % (path, stamp, n)
            n += 1
        shutil.copy2(path, dst)
        return dst
    return None


def norm(p):
    p = os.path.expanduser(str(p).strip())
    if os.name == "nt":
        m = re.match(r"^/([A-Za-z])(/.*)?$", p.replace("\\", "/"))     # Git Bash form /c/Users/...
        if m:
            p = m.group(1).upper() + ":" + (m.group(2) or "/")
    p = os.path.normpath(os.path.abspath(p))
    return p.lower() if os.name == "nt" or sys.platform == "darwin" else p


def run(cmd):
    try:
        exe = shutil.which(cmd[0])
        if not exe:
            return None
        r = subprocess.run([exe] + cmd[1:], capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr).strip() else ""
    except Exception:
        return None


def version_tuple(text):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(x) for x in m.groups()) if m else None


def find_secrets(obj, path="$"):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if SECRET_KEY.search(str(k)) and v not in (None, "", [], {}):
                hits.append("%s.%s (a field named like a secret)" % (path, k))
            hits += find_secrets(v, "%s.%s" % (path, k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += find_secrets(v, "%s[%d]" % (path, i))
    elif isinstance(obj, str) and SECRET_VALUE.search(obj):
        hits.append("%s (looks like a password, token or key)" % path)
    return hits


# ----------------------------------------------------------------------------- doctor
def doctor(as_json):
    checks = []

    def add(status, name, detail, fix=""):
        checks.append({"status": status, "check": name, "detail": detail, "fix": fix})

    v = sys.version_info
    add("OK" if v >= (3, 10) else "MISSING", "Python 3.10+", "%d.%d.%d (%s)" % (v[0], v[1], v[2], sys.executable),
        "" if v >= (3, 10) else "Install Python 3.10+ from python.org, ticking 'Add python.exe to PATH'")
    g = run(["git", "--version"])
    add("OK" if g else "MISSING", "Git", g or "not found", "" if g else "Install Git (git-scm.com)")
    if os.name == "nt":
        found = shutil.which("bash")
        if found and "system32" in found.lower():
            found = None                                       # that is WSL, not Git Bash
        bash = found or next((p for p in (r"C:\Program Files\Git\bin\bash.exe",
                                                         r"C:\Program Files (x86)\Git\bin\bash.exe") if os.path.exists(p)), None)
        add("OK" if bash else "MISSING", "Git Bash (Windows)", bash or "not found",
            "" if bash else "Install Git for Windows; Claude Code runs commands through Git Bash")
    n = run(["node", "--version"])
    nv = version_tuple(n)
    add("OK" if nv and nv >= (18, 0, 0) else "MISSING", "Node.js 18+ (for SentinelQA's browser)", n or "not found",
        "" if nv and nv >= (18, 0, 0) else "Install Node.js LTS from nodejs.org, then restart Claude Code")
    x = run(["npx", "--version"])
    add("OK" if x else "MISSING", "npx", x or "not found", "" if x else "Comes with Node.js; reinstall Node.js LTS")
    c = run(["claude", "--version"])
    cv = version_tuple(c)
    if cv is None:
        add("WARN", "Claude Code version", "could not read `claude --version` here",
            "Run `claude --version`; it must be %d.%d.%d or newer (`claude update`)" % MIN_CLAUDE)
    else:
        add("OK" if cv >= MIN_CLAUDE else "WARN", "Claude Code version", c,
            "" if cv >= MIN_CLAUDE else "Run `claude update` (tested on %d.%d.%d+)" % MIN_CLAUDE)
    prof = read_json(PROFILE, None) if os.path.exists(PROFILE) else None
    np_ = len((prof or {}).get("projects", []))
    add("OK" if np_ else "MISSING", "Project profile", "%d project(s) in %s" % (np_, PROFILE) if prof else "none yet",
        "" if np_ else "Run /qa-setup (once per machine, covers all your projects)")
    st = read_json(STATE, {})
    pr = st.get("permission_rules")
    add("OK" if pr == "added" else "WARN", "Permission rules", pr or "not decided",
        "" if pr == "added" else "Say yes in /qa-setup, or Claude asks before nearly every QA step")
    has_cloud = bool(os.environ.get("JIRA_EMAIL") and os.environ.get("JIRA_API_TOKEN"))
    has_pat = bool(os.environ.get("JIRA_PAT"))
    add("OK" if (has_cloud or has_pat) else "WARN", "Jira attachment download (optional)",
        "credentials set in environment" if (has_cloud or has_pat) else "no JIRA_EMAIL+JIRA_API_TOKEN or JIRA_PAT",
        "" if (has_cloud or has_pat) else "Optional: set them to let SentinelQA read ticket attachments")
    shelf = os.environ.get("SENTINELQA_DOWNLOADS_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
    ok = os.path.isdir(shelf) and os.access(shelf, os.W_OK)
    add("OK" if ok else "WARN", "Report shelf folder", shelf, "" if ok else "Create it, or set SENTINELQA_DOWNLOADS_DIR")
    add("INFO", "Operating system", "%s %s" % (platform.system(), platform.release()))
    add("CHECK-IN-CLAUDE", "Jira connector",
        "a tool ending in getJiraIssue (Atlassian Rovo recommended)",
        "Claude settings -> Connectors -> Atlassian Rovo. The older 'Atlassian' connector is being retired")
    add("CHECK-IN-CLAUDE", "Browser tool", "tools named mcp__plugin_sentinelqa_playwright__browser_*",
        "Needs Node.js; check /mcp in Claude Code")
    add("CHECK-IN-CLAUDE", "Model", "Opus available (`/model opus`)", "Both SentinelQA agents are pinned to Opus")

    if as_json:
        print(json.dumps({"checks": checks}, indent=2))
    else:
        print("SentinelQA doctor")
        print("-" * 78)
        for ch in checks:
            print("%-16s %-38s %s" % (ch["status"], ch["check"], ch["detail"]))
            if ch["fix"]:
                print("%-16s %-38s -> %s" % ("", "", ch["fix"]))
        print("-" * 78)
        missing = [c["check"] for c in checks if c["status"] == "MISSING"]
        print("RESULT: %s" % ("MISSING: " + ", ".join(missing) if missing else "all required prerequisites present"))
    return 0


# ----------------------------------------------------------------------------- profile
def load_profile():
    return read_json(PROFILE, {"version": 1, "projects": []})


def rebuild_prefix_map(prof):
    names = {p["name"] for p in prof.get("projects", [])}
    m = {k: v for k, v in (prof.get("ticket_prefixes") or {}).items() if v not in names}   # keep hand-made entries
    for p in prof.get("projects", []):
        for k in p.get("ticket_prefixes", []):
            m[k] = p["name"]
    prof["ticket_prefixes"] = m


def normalise_project(p):
    if not isinstance(p, dict) or not str(p.get("name", "")).strip():
        raise ValueError("every project needs a 'name'")
    pref = p.get("ticket_prefixes") or []
    if isinstance(pref, str):
        pref = [pref]
    pref = sorted({str(x).strip().upper().rstrip("-") for x in pref if str(x).strip()})
    if not pref:
        raise ValueError("project '%s' needs at least one ticket prefix (e.g. ABC)" % p["name"])
    p["ticket_prefixes"] = pref
    p["repo_paths"] = [str(x) for x in (p.get("repo_paths") or [])]
    p.setdefault("repo_write_policy", "qa-files-ok")
    if p["repo_write_policy"] not in ("qa-files-ok", "read-only"):
        raise ValueError("repo_write_policy must be 'qa-files-ok' or 'read-only'")
    default_root = "qa" if p["repo_write_policy"] == "qa-files-ok" else os.path.join(HOME, "cases", p["name"])
    p["case_root"] = p.get("case_root") or default_root
    if not p.get("ledger"):
        p["ledger"] = (".claude/qa/known-findings.md" if p["repo_write_policy"] == "qa-files-ok"
                       else os.path.join(os.path.expanduser(p["case_root"]), "known-findings.md"))
    if p["repo_write_policy"] == "read-only" and not os.path.isabs(os.path.expanduser(p["case_root"])):
        raise ValueError("project '%s' is read-only, so case_root must be a folder OUTSIDE the repo "
                         "(an absolute path)" % p["name"])
    if str(p["case_root"]).replace("/", "\\").startswith("\\\\"):
        raise ValueError("project '%s': a network-share case root (\\\\server\\share) is not supported; "
                         "use a local folder" % p["name"])
    for key in ("environments", "accounts", "gotchas", "repo_paths"):
        if p.get(key) is not None and not isinstance(p.get(key), list):
            raise ValueError("project '%s': '%s' must be a list" % (p["name"], key))
    for key in ("environments", "accounts"):
        if any(not isinstance(x, dict) for x in p.get(key) or []):
            raise ValueError("project '%s': every item in '%s' must be an object" % (p["name"], key))
    for e in p.get("environments", []) or []:
        if not e.get("url"):
            raise ValueError("every environment needs a 'url'")
        e.setdefault("production", False)
    for a in p.get("accounts", []) or []:
        if not a.get("role"):
            raise ValueError("every account needs a 'role'")
    return p


def do_import(src, inline=None):
    if inline is not None:
        raw = inline
    elif src == "-":
        raw = sys.stdin.read()
    else:
        raw = io.open(os.path.expanduser(src), encoding="utf-8-sig").read()
    data = json.loads(raw)
    secrets = find_secrets(data)
    if secrets:
        print("REFUSED: the profile must never hold a password, token or key. Found:")
        for s in secrets:
            print("  - " + s)
        print("Store only WHERE the credential lives (a vault name, an env var name).")
        return 2
    incoming = data.get("projects") if isinstance(data, dict) and "projects" in data else [data]
    prof = load_profile()
    if isinstance(data, dict) and data.get("tester"):
        prof["tester"] = data["tester"]
    added, replaced = [], []
    for p in incoming:
        p = normalise_project(dict(p))
        idx = next((i for i, q in enumerate(prof["projects"]) if q["name"].lower() == p["name"].lower()), None)
        if idx is None:
            prof["projects"].append(p)
            added.append(p["name"])
        else:
            prof["projects"][idx] = p
            replaced.append(p["name"])
    clash = {}
    for p in prof["projects"]:
        for k in p["ticket_prefixes"]:
            clash.setdefault(k, []).append(p["name"])
    dup = {k: v for k, v in clash.items() if len(v) > 1}
    if dup:
        print("REFUSED: a ticket prefix may belong to one project only: %s" % json.dumps(dup))
        return 2
    prof["version"] = 1
    rebuild_prefix_map(prof)
    b = backup(PROFILE)
    write_json(PROFILE, prof)
    print("saved %s%s" % (PROFILE, "  (previous version kept as %s)" % b if b else ""))
    print("added: %s | updated: %s | total projects: %d" % (", ".join(added) or "-", ", ".join(replaced) or "-",
                                                          len(prof["projects"])))
    return 0


def show():
    prof = read_json(PROFILE, None)
    if not prof:
        print("No profile yet (%s). Run /qa-setup." % PROFILE)
        return 0
    print("Profile: %s" % PROFILE)
    if prof.get("tester"):
        print("Tester: %s" % prof["tester"].get("name", "-"))
    for p in prof.get("projects", []):
        print("- %s  prefixes=%s  write=%s  case_root=%s" % (p["name"], ",".join(p["ticket_prefixes"]),
                                                           p["repo_write_policy"], p["case_root"]))
        print("    repos: %s" % (", ".join(p.get("repo_paths") or []) or "-"))
        src = p.get("source_code") or {}
        print("    source code: %s" % ("available" if src.get("available") else "NOT available to QA"
                                       if src.get("available") is False else "unknown"))
        for e in p.get("environments") or []:
            print("    env %s: %s%s" % (e.get("name", "?"), e["url"], "  (PRODUCTION - never test)" if e.get("production") else ""))
        for a in p.get("accounts") or []:
            print("    account %s -> %s" % (a["role"], a.get("credential_location", "-")))
    return 0


def match(cwd, ticket):
    prof = read_json(PROFILE, None)
    if not prof or not prof.get("projects"):
        print(json.dumps({"status": "no_profile", "profile": PROFILE,
                          "advice": "Offer /qa-setup (one time, all projects) or ask per ticket"}))
        return 0
    here = norm(cwd or os.getcwd())
    best = None
    for p in prof["projects"]:
        for rp in p.get("repo_paths") or []:
            r = norm(rp)
            if here == r or here.startswith(r.rstrip("\\/") + os.sep):
                if not best or len(r) > best[1]:
                    best = (p, len(r), "working folder is inside %s" % rp)
    if ticket:
        pre = re.match(r"^([A-Za-z][A-Za-z0-9_]*)-\d+$", ticket.strip())
        if pre:
            for p in prof["projects"]:
                if pre.group(1).upper() in p["ticket_prefixes"]:
                    if not best:
                        best = (p, 0, "ticket prefix %s" % pre.group(1).upper())
                    elif best[0]["name"] != p["name"]:
                        best = (p, 0, "ticket prefix %s belongs to %s (the folder belongs to %s; the "
                                      "ticket decides)" % (pre.group(1).upper(), p["name"], best[0]["name"]))
    if not best:
        print(json.dumps({"status": "no_match", "situation": "D", "projects": [p["name"] for p in prof["projects"]],
                          "advice": "New project: ask its project block once (local folder, Jira site, "
                                    "environments, accounts) in the one start-of-run message, then save it"}))
        return 0
    out = {"status": "match", "reason": best[2], "tester": prof.get("tester"), "project": best[0]}
    out.update(folder_situation(best[0], here))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def folder_situation(p, here):
    """Is the session open in this project's folder, and does the saved folder still exist?
    A = open in the project folder (or the project has no local code by design) - continue
    B = the project's folder exists elsewhere - tell the person to open Claude Code there (or continue without code)
    C = the saved folder is gone (moved/renamed) or none is saved - ask where it is now, once"""
    paths = [{"path": rp, "exists": os.path.isdir(os.path.expanduser(rp))} for rp in p.get("repo_paths") or []]
    inside = any(here == norm(x["path"]) or here.startswith(norm(x["path"]).rstrip("\\/") + os.sep) for x in paths)
    no_code = (p.get("source_code") or {}).get("available") is False
    if inside:
        return {"situation": "A", "folders": paths, "advice": "Open in the project folder: continue"}
    existing = [x["path"] for x in paths if x["exists"]]
    if existing:
        return {"situation": "B", "folders": paths, "open_in": existing[0],
                "advice": "Stop once: this ticket belongs to %s, whose folder is %s. Tell the person to open "
                          "Claude Code there and run the command again, or reply 'continue here' to test "
                          "without the source code (requirement-based Pass 1, live testing)." % (p["name"], existing[0])}
    if no_code and not paths:
        return {"situation": "A", "folders": [], "advice": "Source code is recorded as not available to QA: "
                                                            "continue with requirement-based Pass 1 and live testing"}
    return {"situation": "C", "folders": paths,
            "advice": ("The saved folder(s) %s no longer exist. " % ", ".join(x["path"] for x in paths) if paths
                       else "No local folder is saved for %s. " % p["name"])
                      + "Ask once, in the start-of-run message: where is it on this machine now? (path / not on "
                        "this machine). Save the answer with `import`."}


# ----------------------------------------------------------------------------- preflight
def cred_check(loc):
    """Check WHERE a credential lives, never what it is. Values are never read into the output.
    env:USER_VAR,PASS_VAR  |  file:<path>#<key>  |  anything else = manual (vault, password manager)."""
    s = str(loc or "").strip()
    m = re.match(r"^env:\s*(.+)$", s, re.I)
    if m:
        names = [x for x in re.split(r"[,\s;]+", m.group(1)) if x]
        miss = [n for n in names if not os.environ.get(n)]
        if miss:
            return {"status": "missing", "detail": "environment variable(s) not set in this session: %s. "
                    "A variable set after Claude Code started is not visible until Claude Code is restarted; "
                    "a credentials file (file:<path>#<key>) avoids that." % ", ".join(miss)}
        return {"status": "ok", "detail": "environment variable(s) set: %s" % ", ".join(names)}
    m = re.match(r"^file:\s*(.+?)(?:#(.+))?$", s, re.I)
    if m:
        path, key = os.path.expanduser(m.group(1).strip()), (m.group(2) or "").strip()
        if not os.path.isfile(path):
            return {"status": "missing", "detail": "credentials file not found: %s" % m.group(1).strip()}
        warn = ""
        d = os.path.dirname(os.path.abspath(path))
        while True:
            if os.path.isdir(os.path.join(d, ".git")):
                warn = " WARNING: this file is inside a git repository (%s); keep credentials outside repos." % d
                break
            nd = os.path.dirname(d)
            if nd == d:
                break
            d = nd
        if not key:
            return {"status": "ok", "detail": "credentials file exists (no key given)" + warn, "file": path}
        found = key_in_file(path, key)
        if found is None:
            return {"status": "unknown", "detail": "file exists but could not be parsed to look for '%s'" % key + warn,
                    "file": path}
        return {"status": "ok" if found else "missing",
                "detail": ("entry '%s' found" % key if found else "no entry '%s' in the file" % key) + warn,
                "file": path}
    if not s:
        return {"status": "missing", "detail": "no credential location recorded for this role"}
    return {"status": "manual", "detail": "'%s' cannot be checked automatically. Before the run, copy the login "
            "into a credentials file outside any repo (file:<path>#<key>), or confirm the person will type it." % s}


def key_in_file(path, key):
    try:
        raw = io.open(path, encoding="utf-8-sig").read()
    except (OSError, UnicodeDecodeError):
        return None
    if path.lower().endswith(".json"):
        try:
            data = json.loads(raw)
        except ValueError:
            return None
        cur, ok = data, True
        for part in key.split("."):
            if isinstance(cur, dict):
                hit = next((k for k in cur if str(k).lower() == part.lower()), None)
                if hit is None:
                    ok = False
                    break
                cur = cur[hit]
            else:
                ok = False
                break
        if ok:
            return True

        def walk(o):                                     # a list of {"role"/"name"/"key"/"id": key, ...}
            if isinstance(o, dict):
                if any(str(o.get(f, "")).lower() == key.lower() for f in ("role", "name", "key", "id", "username")):
                    return True
                return any(walk(v) for v in o.values())
            if isinstance(o, list):
                return any(walk(v) for v in o)
            return False
        return walk(data)
    for line in raw.splitlines():                        # .env style KEY=... or a plain-text mention
        if re.match(r"^\s*(export\s+)?%s\s*[=:]" % re.escape(key), line, re.I):
            return True
    return key.lower() in raw.lower()


def probe(url, timeout=8):
    """One GET to see whether a NON-production environment answers. Returns status, never the body."""
    import ssl
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "SentinelQA-preflight"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": "ok", "detail": "HTTP %d (final URL %s)" % (r.status, r.geturl())}
    except urllib.error.HTTPError as e:            # 401/403/404 still prove the server answers
        return {"status": "ok" if e.code < 500 else "error", "detail": "HTTP %d" % e.code}
    except ssl.SSLError as e:
        return {"status": "error", "detail": "TLS/certificate error: %s" % e}
    except Exception as e:                          # DNS, refused, timeout, VPN not connected
        return {"status": "error", "detail": "no answer: %s (VPN or network?)" % getattr(e, "reason", e)}


def preflight(cwd, ticket, project, roles, env, do_probe):
    """Everything a run needs, checked BEFORE testing starts, so the person is asked once and the test is
    not interrupted. Prints JSON with an 'ask' list: the only things to put in the one start-of-run message."""
    prof = read_json(PROFILE, None)
    if not prof or not prof.get("projects"):
        print(json.dumps({"status": "no_profile", "situation": "E", "ask": [
            "SentinelQA isn't set up on this machine yet: run /qa-setup now (once, all projects), or continue "
            "and answer only what this ticket needs"]}, indent=2))
        return 0
    here = norm(cwd or os.getcwd())
    targets, situation = [], None
    if project:
        targets = [p for p in prof["projects"] if p["name"].lower() == project.lower()]
    elif ticket:
        pre = re.match(r"^([A-Za-z][A-Za-z0-9_]*)-\d+$", ticket.strip())
        targets = [p for p in prof["projects"] if pre and pre.group(1).upper() in p["ticket_prefixes"]]
        if not targets:                                  # fall back to the folder
            targets = [p for p in prof["projects"] for rp in p.get("repo_paths") or []
                       if here == norm(rp) or here.startswith(norm(rp).rstrip("\\/") + os.sep)][:1]
        if not targets:
            print(json.dumps({"status": "no_match", "situation": "D", "ask": [
                "Ticket %s matches no saved project. Which project is it? If new: its local folder (or 'not on "
                "this machine'), Jira site, test environments (mark production), test accounts by role and "
                "where each login is kept (never the password)" % ticket]}, indent=2))
            return 0
    else:
        targets = prof["projects"]
    wanted_roles = {r.strip().lower() for r in (roles or "").split(",") if r.strip()}
    out, ask = [], []
    for p in targets:
        r = {"project": p["name"]}
        if ticket or project:
            r.update(folder_situation(p, here))
            situation = r["situation"]
            if r["situation"] == "B":
                ask.append(r["advice"])
            elif r["situation"] == "C":
                ask.append("%s: %s" % (p["name"], r["advice"]))
        else:
            r["folders"] = [{"path": x, "exists": os.path.isdir(os.path.expanduser(x))} for x in p.get("repo_paths") or []]
            for f in r["folders"]:
                if not f["exists"]:
                    ask.append("%s: saved folder %s does not exist on this machine - correct the path, or "
                               "remove it" % (p["name"], f["path"]))
        envs = []
        for e in p.get("environments") or []:
            if env and e.get("name", "").lower() != env.lower():
                continue
            row = {"name": e.get("name"), "url": e.get("url"), "production": bool(e.get("production"))}
            if e.get("production"):
                row.update({"status": "skipped", "detail": "production: never probed, never tested"})
            elif do_probe:
                row.update(probe(e["url"]))
                if row["status"] != "ok":
                    ask.append("%s: environment %s (%s) did not answer: %s. Is it up / are you on the VPN? Or "
                               "name another environment." % (p["name"], e.get("name"), e["url"], row["detail"]))
            else:
                row.update({"status": "not-probed", "detail": ""})
            envs.append(row)
        if not [x for x in envs if not x["production"]]:
            ask.append("%s: no test environment is saved%s - give its URL, or say 'no live testing' (cases are "
                       "then Not Executed)" % (p["name"], " with the name '%s'" % env if env else ""))
        r["environments"] = envs
        accts = []
        for a in p.get("accounts") or []:
            if wanted_roles and a["role"].lower() not in wanted_roles:
                continue
            c = cred_check(a.get("credential_location"))
            accts.append(dict({"role": a["role"], "location": a.get("credential_location", "")}, **c))
            if c["status"] in ("missing", "manual", "unknown"):
                ask.append("%s: login for role '%s': %s" % (p["name"], a["role"], c["detail"]))
        for wr in sorted(wanted_roles - {a["role"].lower() for a in p.get("accounts") or []}):
            ask.append("%s: no test account saved for role '%s' - where is its login kept (never the password "
                       "itself), or 'skip' (those cases are Not Executed)" % (p["name"], wr))
        r["accounts"] = accts
        if not (p.get("accounts") or []) and not wanted_roles:
            r["note_accounts"] = "no test accounts saved"
        out.append(r)
    res = {"status": "ok" if not ask else "needs-answers", "projects": out, "ask": ask,
           "rule": "Put every 'ask' item in ONE message before testing starts. Never print a credential value."}
    if situation:
        res["situation"] = situation
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


# ----------------------------------------------------------------------------- rules + state
def settings_path(arg):
    if arg:
        return arg
    if os.environ.get("SENTINELQA_SETTINGS_FILE"):      # used by SentinelQA's own tests
        return os.environ["SENTINELQA_SETTINGS_FILE"]
    if os.environ.get("CLAUDE_CONFIG_DIR"):
        return os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "settings.json")
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def rule_path(p):
    """Absolute folder -> Claude Code permission path syntax (//c/Users/... on Windows)."""
    a = os.path.abspath(os.path.expanduser(p)).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", a)
    return "//%s/%s" % (m.group(1).lower(), m.group(2)) if m else "/" + a


def base_rules():
    t = io.open(RULES_MD, encoding="utf-8").read()
    return json.loads(re.search(r"```json\n(.*?)```", t, re.S).group(1))


def extra_rules():
    rules = []
    prof = read_json(PROFILE, {"projects": []})
    for p in prof.get("projects", []):
        root = os.path.expanduser(p.get("case_root") or "qa")
        if os.path.isabs(root):
            rp = rule_path(root).rstrip("/")
            rules += ["Read(%s/**)" % rp, "Edit(%s/**)" % rp]
        for a in p.get("accounts") or []:                # a credentials FILE is read at login time only
            m = re.match(r"^file:\s*(.+?)(?:#.*)?$", str(a.get("credential_location") or ""), re.I)
            if m and os.path.isabs(os.path.expanduser(m.group(1).strip())):
                rules.append("Read(%s)" % rule_path(m.group(1).strip()))
    prod = {origin(e.get("url", "")) for p in prof.get("projects", []) for e in p.get("environments") or []
            if e.get("production")}
    for p in prof.get("projects", []):
        for e in p.get("environments") or []:
            o = origin(e.get("url", ""))
            if e.get("production") or not o:
                continue
            if o in prod:
                print("NOTE: no curl rule for %s - production uses the same address" % o)
                continue
            rules += ["Bash(curl *%s/*)" % o, "Bash(curl *%s)" % o,
                      "PowerShell(curl *%s/*)" % o, "PowerShell(curl *%s)" % o]
    return rules


def origin(url):
    """scheme://host[:port] - a curl rule is scoped to exactly this, so it cannot cover another site."""
    m = re.match(r"^\s*(https?)://([^/\s?#]+)", url or "", re.I)
    return ("%s://%s" % (m.group(1).lower(), m.group(2).lower())) if m else ""


def set_state(value):
    st = read_json(STATE, {})
    st["permission_rules"] = value
    st["updated"] = datetime.date.today().isoformat()
    write_json(STATE, st)


def add_rules(arg):
    path = settings_path(arg)
    try:
        s = read_json(path, {})
    except ValueError as e:
        print("REFUSED: %s is not valid JSON (%s). Nothing was changed; fix the file first." % (path, e))
        return 2
    if not isinstance(s.get("permissions"), dict):
        s["permissions"] = {}
    perms = s["permissions"]
    if not isinstance(perms.get("allow"), list):
        perms["allow"] = []
    allow = perms["allow"]
    want = list(dict.fromkeys(base_rules() + extra_rules()))     # de-duplicated, order kept
    new = [r for r in want if r not in allow]
    if not new:
        print("already present: all %d SentinelQA rules are in %s" % (len(want), path))
        set_state("added")
        return 0
    b = backup(path)
    allow.extend(new)
    write_json(path, s)
    set_state("added")
    print("added %d rule(s) to %s (kept every existing entry; backup: %s)" % (len(new), path, b or "new file"))
    print("Restart Claude Code so the new rules take effect everywhere.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="SentinelQA one-time setup and project profile")
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("doctor"); d.add_argument("--json", action="store_true")
    sp.add_parser("show")
    m = sp.add_parser("match"); m.add_argument("--cwd"); m.add_argument("--ticket")
    i = sp.add_parser("import"); i.add_argument("src", nargs="?", default=None); i.add_argument("--json")
    r = sp.add_parser("add-rules"); r.add_argument("--settings")
    s = sp.add_parser("state"); s.add_argument("what", choices=["rules", "show"]); s.add_argument("value", nargs="?")
    f = sp.add_parser("preflight", help="check folder, environments and logins before a run (or all projects)")
    f.add_argument("--cwd"); f.add_argument("--ticket"); f.add_argument("--project")
    f.add_argument("--roles", help="comma-separated roles this ticket needs"); f.add_argument("--env")
    f.add_argument("--no-probe", action="store_true", help="do not contact the test environments")
    a = ap.parse_args()
    if a.cmd == "preflight":
        return preflight(a.cwd, a.ticket, a.project, a.roles, a.env, not a.no_probe)
    if a.cmd == "doctor":
        return doctor(a.json)
    if a.cmd == "show":
        return show()
    if a.cmd == "match":
        return match(a.cwd, a.ticket)
    if a.cmd == "import":
        try:
            if a.json is None and a.src is None:
                print("usage: import <file> | import - | import --json '<json>'")
                return 2
            return do_import(a.src, a.json)
        except (ValueError, json.JSONDecodeError) as e:
            print("REFUSED: %s" % e)
            return 2
    if a.cmd == "add-rules":
        return add_rules(a.settings)
    if a.cmd == "state":
        if a.what == "show":
            print(json.dumps(read_json(STATE, {}), indent=2))
            return 0
        if a.value not in ("added", "declined"):
            print("usage: state rules added|declined")
            return 2
        set_state(a.value)
        print("recorded: permission_rules = %s" % a.value)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
