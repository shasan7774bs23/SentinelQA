"""jira-attachments.py — download a Jira ticket's attachments into the case file.

Usage:
    python jira-attachments.py <TICKET-KEY> --site <your-site.atlassian.net> [--out DIR] [--list]

Credentials come ONLY from environment variables, never from arguments or files:
    JIRA_EMAIL + JIRA_API_TOKEN   Jira Cloud (basic auth with an API token)
    JIRA_PAT                      Jira Server / Data Center (bearer personal access token)

Exit codes:
    0  done (or nothing to download)
    2  usage error
    3  no credentials set -> NOT an error for the QA run. The method asks the user once whether they
       will drop the files into the folder by hand, and otherwise continues, listing every attachment
       as "Not reviewed". Never ask anyone to log in because of this.
    4  Jira answered with an error (wrong site, no access, ticket not found)

Writes <out>/INDEX.md listing every file with its size and SHA-256, so the report can cite exactly
which file was reviewed. Existing files are never overwritten (pass --force to replace them).
The token is never printed, logged or written anywhere.

Why this exists: the ticket's DB scripts, specs and screenshots often decide the verdict, and the
Jira connectors return only attachment metadata, not the file contents.
"""
import argparse
import base64
import hashlib
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def auth_header():
    pat = os.environ.get("JIRA_PAT", "").strip()
    if pat:
        return "Bearer " + pat
    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    if email and token:
        raw = (email + ":" + token).encode("utf-8")
        return "Basic " + base64.b64encode(raw).decode("ascii")
    return None


def base_url(site):
    site = site.strip().rstrip("/")
    if not re.match(r"^https?://", site):
        site = "https://" + site
    return site


def get(url, auth, accept="application/json"):
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth)
    req.add_header("Accept", accept)
    return urllib.request.urlopen(req, timeout=60)


def safe_name(name):
    name = os.path.basename(name.replace("\\", "/"))
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")
    return name or "attachment"


def main():
    ap = argparse.ArgumentParser(description="Download a Jira ticket's attachments.")
    ap.add_argument("key", help="ticket key, e.g. ABC-123")
    ap.add_argument("--site", required=True, help="Jira site, e.g. your-site.atlassian.net")
    ap.add_argument("--out", help="folder to write into (default qa/<KEY>/attachments)")
    ap.add_argument("--list", action="store_true", help="list attachments only, download nothing")
    ap.add_argument("--force", action="store_true", help="overwrite files that already exist")
    a = ap.parse_args()

    if not re.match(r"^[A-Za-z][A-Za-z0-9_]*-\d+$", a.key):
        print("usage error: '%s' does not look like a ticket key (ABC-123)" % a.key)
        return 2

    auth = auth_header()
    if not auth:
        print("NO CREDENTIALS: JIRA_EMAIL + JIRA_API_TOKEN (or JIRA_PAT) are not set in this session.")
        print("Nothing was downloaded. This is not an error for the QA run: ask the user once whether")
        print("they will drop the attachments into the case file by hand; otherwise continue and mark")
        print("each attachment 'Not reviewed' in the report.")
        return 3

    root = base_url(a.site)
    out = a.out or os.path.join("qa", a.key, "attachments")
    url = "%s/rest/api/%s/issue/%s?fields=attachment" % (
        root, "2" if os.environ.get("JIRA_PAT") else "3", urllib.parse.quote(a.key))
    try:
        with get(url, auth) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("JIRA ERROR %s for %s: %s" % (e.code, a.key, {
            401: "credentials rejected", 403: "no permission to this ticket",
            404: "ticket not found on this site"}.get(e.code, e.reason)))
        return 4
    except (urllib.error.URLError, ValueError) as e:
        print("JIRA ERROR: could not reach %s (%s)" % (root, e))
        return 4

    atts = (data.get("fields") or {}).get("attachment") or []
    if not atts:
        print("%s has no attachments." % a.key)
        return 0

    print("%s has %d attachment(s):" % (a.key, len(atts)))
    for x in atts:
        print("  - %s  (%s bytes, %s)" % (x.get("filename"), x.get("size"), x.get("mimeType")))
    if a.list:
        return 0

    os.makedirs(out, exist_ok=True)
    rows, failed, used = [], 0, set()
    for x in atts:
        name = safe_name(x.get("filename") or "attachment")
        base, ext = os.path.splitext(name)
        n = 2
        while name.lower() in used:            # two attachments with the same name
            name = "%s (%d)%s" % (base, n, ext)
            n += 1
        used.add(name.lower())
        dest = os.path.join(out, name)
        if os.path.exists(dest) and not a.force:
            data_b = io.open(dest, "rb").read()
            rows.append((name, len(data_b), hashlib.sha256(data_b).hexdigest(), "already present"))
            continue
        try:
            with get(x["content"], auth, accept="*/*") as r:
                data_b = r.read()
        except (urllib.error.URLError, KeyError, ValueError) as e:
            failed += 1
            rows.append((name, 0, "-", "FAILED: %s" % getattr(e, "code", e)))
            continue
        with io.open(dest, "wb") as f:
            f.write(data_b)
        rows.append((name, len(data_b), hashlib.sha256(data_b).hexdigest(), "downloaded"))

    idx = os.path.join(out, "INDEX.md")
    with io.open(idx, "w", encoding="utf-8") as f:
        f.write("# Attachments of %s\n\n| File | Bytes | SHA-256 | Status |\n|---|---|---|---|\n" % a.key)
        for name, size, sha, st in rows:
            f.write("| %s | %s | `%s` | %s |\n" % (name, size, sha[:16], st))
    new = sum(1 for r in rows if r[3] == "downloaded")
    kept = sum(1 for r in rows if r[3] == "already present")
    print("%d downloaded, %d already present, %d failed -> %s (index: %s)" % (
        new, kept, failed, out, idx))
    return 4 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
