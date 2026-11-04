#!/usr/bin/env python3
"""
report-shelf.py - the single place QA reports land on disk.

Every QA / automation / release report goes onto a per-project shelf instead of
being dumped loose into Downloads:

    <Downloads>/QA-Reports/<PROJECT>/YYYY-MM-DD_<name>.<ext>

The date prefix means sorting by Name IS sorting by date (Name Z->A = newest
first) in Explorer, in a file picker, anywhere. Each project folder and the
root also get an index.html listing reports newest-first.

Subcommands
-----------
  publish <file> [<file>...] [--project P] [--date YYYY-MM-DD] [--no-index]
      Copy finished report(s) onto the shelf. This is what the QA agents call.

  sweep [--apply] [--include-process-docs]
      Move loose report files/folders out of the Downloads root onto the shelf.
      Dry-run by default; --apply moves them and writes an undo manifest.

  reindex
      Rebuild every index.html from what is on disk.

  undo <manifest.csv>
      Reverse a sweep.

Configuration (all optional)
----------------------------
  SENTINELQA_DOWNLOADS_DIR   env var - base folder; default is <your home>/Downloads.
  ~/.sentinelqa/projects.json - map ticket-key prefixes to project names, e.g.
      {"ticket_prefixes": {"ABC": "ABC-Web", "ABCAPI": "ABC-API"},
       "folder_moves": {"some-loose-folder": "ABC-Web"},
       "process_docs": ["qa-handbook.html"]}

Project is resolved from the ticket key in the filename (ABC-123 -> the name
mapped for "ABC" in projects.json, or "ABC" itself when unmapped). Anything it
cannot resolve lands in _Unsorted and is reported loudly - it never guesses
silently.
"""

import argparse
import csv
import datetime as _dt
import html
import json
import os
import re
import shutil
import sys
from collections import Counter

DOWNLOADS = os.environ.get("SENTINELQA_DOWNLOADS_DIR") or os.path.join(os.path.expanduser("~"), "Downloads")
SHELF = os.path.join(DOWNLOADS, "QA-Reports")
MANIFEST_DIR = os.path.join(SHELF, "_manifest")
UNSORTED = "_Unsorted"
PROCESS_DOCS_PROJECT = "_QA-Process"
REPORT_EXTS = (".html", ".md", ".pdf")
# The sweep only ever claims what the QA agents themselves write. PDFs in the
# Downloads root are app output captured during testing, not reports - they
# stay put unless published explicitly.
SWEEP_EXTS = (".html", ".md")
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_")
DATE_IN_NAME_RE = re.compile(r"20\d{2}-\d{2}-\d{2}")

# --- per-user configuration -------------------------------------------------
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".sentinelqa", "projects.json")


def _load_config():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as exc:
        print("WARNING: could not read {0}: {1}".format(CONFIG_PATH, exc), file=sys.stderr)
        return {}


_CFG = _load_config()
# Prefix -> project name. Longest prefix wins, so "ABCAPI" beats "ABC".
TICKET_PREFIXES = {k.upper(): v for k, v in (_CFG.get("ticket_prefixes") or {}).items()}
# Loose folders in the Downloads root that are whole report / evidence sets.
# Moved intact so their internal relative links keep working.
FOLDER_MOVES = dict(_CFG.get("folder_moves") or {})
# Loose files in the Downloads root that are QA material but not ticket reports.
PROCESS_DOCS = set(_CFG.get("process_docs") or [])

# A Jira-style ticket key: LETTERS(+digits) - digits.
TICKET_KEY_RE = re.compile(r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9]*)[-_](\d+)(?![0-9])")


def resolve_project(name, explicit=None):
    """Return (project, how_it_was_decided)."""
    if explicit:
        return explicit, "explicit --project"
    stem = DATE_PREFIX_RE.sub("", os.path.basename(name))
    upper = stem.upper()
    # 1. A configured prefix that starts a ticket key (longest first).
    for prefix in sorted(TICKET_PREFIXES, key=len, reverse=True):
        if re.search(r"(?<![A-Z0-9])" + re.escape(prefix) + r"[-_]?\d+", upper):
            return TICKET_PREFIXES[prefix], "ticket key in filename (projects.json)"
    # 2. Any ticket key: its letter prefix is the project.
    m = TICKET_KEY_RE.search(stem)
    if m and not re.match(r"^20\d{2}$", m.group(2)):
        return m.group(1).upper(), "ticket key prefix in filename"
    return UNSORTED, "UNRESOLVED - pass --project"


def resolve_date(path, explicit=None):
    if explicit:
        return explicit
    base = os.path.basename(path)
    if DATE_PREFIX_RE.match(base):
        return base[:10]
    m = DATE_IN_NAME_RE.search(base)
    if m:
        return m.group(0)
    return _dt.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")


def shelf_name(path, date):
    base = os.path.basename(path)
    if DATE_PREFIX_RE.match(base):
        return base
    return "{0}_{1}".format(date, base)


def unique_target(target):
    if not os.path.exists(target):
        return target
    root, ext = os.path.splitext(target)
    n = 2
    while os.path.exists("{0}-{1}{2}".format(root, n, ext)):
        n += 1
    return "{0}-{1}{2}".format(root, n, ext)


# --- index generation -------------------------------------------------------
# Follows the scroll-root contract: body overflow hidden + one viewport-height
# inner scroller, focusable, with keyboard and wheel fallbacks.
CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%}
body{overflow:hidden;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;
     background:var(--bg);color:var(--fg)}
:root{--bg:#f6f7f9;--fg:#1c2024;--card:#fff;--line:#e3e6ea;--mut:#6b7280;
      --accent:#1f6feb;--chip:#eef2f7}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#13161a;--fg:#e6e9ee;--card:#1b1f25;--line:#2a3038;--mut:#9aa3af;
  --accent:#6ea8fe;--chip:#232932}}
:root[data-theme="dark"]{--bg:#13161a;--fg:#e6e9ee;--card:#1b1f25;
  --line:#2a3038;--mut:#9aa3af;--accent:#6ea8fe;--chip:#232932}
.scroll-root{height:100vh;height:100dvh;overflow-y:auto;
  -webkit-overflow-scrolling:touch;outline:none}
.wrap{max-width:1040px;margin:0 auto;padding:28px 16px 80px}
h1{font-size:24px;margin:0 0 4px}
.sub{color:var(--mut);font-size:13px;margin:0 0 22px}
.sub a{color:var(--accent)}
.day{display:flex;align-items:center;gap:10px;margin:26px 0 10px}
.day b{font-size:12px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--mut)}
.day i{flex:1;height:1px;background:var(--line);font-style:normal}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;
  overflow:hidden}
.row{display:flex;align-items:center;gap:12px;padding:10px 14px;
  border-top:1px solid var(--line)}
.row:first-child{border-top:none}
.row a{color:var(--accent);text-decoration:none;font-weight:500;
  word-break:break-word}
.row a:hover{text-decoration:underline}
.grow{flex:1;min-width:0}
.chip{font-size:11px;padding:2px 8px;border-radius:99px;background:var(--chip);
  color:var(--mut);white-space:nowrap}
.sz{font-size:12px;color:var(--mut);white-space:nowrap;
  font-variant-numeric:tabular-nums}
.proj{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));
  gap:14px}
.proj a{display:block;padding:16px;background:var(--card);
  border:1px solid var(--line);border-radius:10px;text-decoration:none;
  color:var(--fg)}
.proj a:hover{border-color:var(--accent)}
.proj .n{font-weight:600;font-size:16px;margin-bottom:6px}
.proj .m{font-size:12px;color:var(--mut)}
@media(max-width:560px){.row{flex-wrap:wrap;gap:6px}.sz,.chip{font-size:11px}}
"""

JS = """
(function(){
  var s=document.querySelector(".scroll-root");if(!s)return;
  function focusIt(){try{s.focus({preventScroll:true})}catch(e){s.focus()}}
  focusIt();
  window.addEventListener("pointerdown",focusIt);
  window.addEventListener("keydown",function(e){
    if(e.defaultPrevented)return;
    var t=e.target,tag=t&&t.tagName;
    if(tag==="INPUT"||tag==="TEXTAREA"||(t&&t.isContentEditable))return;
    var h=s.clientHeight,k=e.key,d=null;
    if(k==="PageDown"){d=h*0.9}
    else if(k==="PageUp"){d=-h*0.9}
    else if(k===" "||k==="Spacebar"){d=e.shiftKey?-h*0.9:h*0.9}
    else if(k==="ArrowDown"){d=60}
    else if(k==="ArrowUp"){d=-60}
    else if(k==="Home"){s.scrollTo({top:0});e.preventDefault();return}
    else if(k==="End"){s.scrollTo({top:s.scrollHeight});e.preventDefault();return}
    if(d!==null){s.scrollBy({top:d});e.preventDefault()}
  },true);
  window.addEventListener("wheel",function(e){
    if(!s.contains(e.target)){s.scrollBy({top:e.deltaY});e.preventDefault()}
  },{passive:false});
})();
"""


def page(title, body):
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>" + html.escape(title) + "</title><style>" + CSS +
            "</style></head><body><div class=\"scroll-root\" tabindex=\"-1\">"
            "<div class=\"wrap\">" + body + "</div></div><script>" + JS +
            "</script></body></html>\n")


def human(nbytes):
    size = float(nbytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            fmt = "{0:.0f} {1}" if unit == "B" else "{0:.1f} {1}"
            return fmt.format(size, unit)
        size /= 1024.0


def scan_project(proj_dir):
    """Return the project folder contents, newest first."""
    entries = []
    for n in os.listdir(proj_dir):
        if n == "index.html":
            continue
        p = os.path.join(proj_dir, n)
        if os.path.isdir(p):
            inner = sum(len(files) for _, _, files in os.walk(p))
            entries.append({
                "name": n, "href": n + "/",
                "date": _dt.datetime.fromtimestamp(
                    os.path.getmtime(p)).strftime("%Y-%m-%d"),
                "size": None, "kind": "folder",
                "note": "{0} files".format(inner)})
            continue
        if os.path.splitext(n)[1].lower() not in REPORT_EXTS:
            continue
        if DATE_PREFIX_RE.match(n):
            d = n[:10]
        else:
            d = _dt.datetime.fromtimestamp(
                os.path.getmtime(p)).strftime("%Y-%m-%d")
        entries.append({
            "name": n, "href": n, "date": d, "size": os.path.getsize(p),
            "kind": os.path.splitext(n)[1].lower().lstrip("."), "note": None})
    entries.sort(key=lambda e: (e["date"], e["name"]), reverse=True)
    return entries


def write_project_index(proj_dir):
    proj = os.path.basename(proj_dir)
    entries = scan_project(proj_dir)
    parts = [
        "<h1>" + html.escape(proj) + "</h1>",
        "<p class=\"sub\">{0} items &middot; newest first &middot; rebuilt {1}"
        " &middot; <a href=\"../index.html\">all projects</a></p>".format(
            len(entries), _dt.datetime.now().strftime("%Y-%m-%d %H:%M"))]
    cur = None
    open_card = False
    for e in entries:
        if e["date"] != cur:
            if open_card:
                parts.append("</div>")
            cur = e["date"]
            parts.append("<div class=\"day\"><b>{0}</b><i></i></div>"
                         "<div class=\"card\">".format(html.escape(cur)))
            open_card = True
        meta = e["note"] if e["size"] is None else human(e["size"])
        parts.append(
            "<div class=\"row\"><span class=\"chip\">{0}</span>"
            "<span class=\"grow\"><a href=\"{1}\">{2}</a></span>"
            "<span class=\"sz\">{3}</span></div>".format(
                html.escape(e["kind"]), html.escape(e["href"]),
                html.escape(e["name"]), html.escape(meta)))
    if open_card:
        parts.append("</div>")
    if not entries:
        parts.append("<div class=\"card\"><div class=\"row\">"
                     "<span class=\"grow\">No reports yet.</span></div></div>")
    with open(os.path.join(proj_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(proj + " - QA reports", "".join(parts)))


def write_root_index():
    projs = sorted(d for d in os.listdir(SHELF)
                   if os.path.isdir(os.path.join(SHELF, d)) and d != "_manifest")
    cards = []
    recent = []
    for p in projs:
        entries = scan_project(os.path.join(SHELF, p))
        for e in entries:
            if e["size"] is not None:
                item = dict(e)
                item["proj"] = p
                recent.append(item)
        latest = entries[0]["date"] if entries else "-"
        cards.append(
            "<a href=\"{0}/index.html\"><div class=\"n\">{1}</div>"
            "<div class=\"m\">{2} items &middot; latest {3}</div></a>".format(
                html.escape(p), html.escape(p), len(entries), html.escape(latest)))
    recent.sort(key=lambda e: (e["date"], e["name"]), reverse=True)
    body = [
        "<h1>QA Reports</h1>",
        "<p class=\"sub\">{0} projects &middot; rebuilt {1}</p>".format(
            len(projs), _dt.datetime.now().strftime("%Y-%m-%d %H:%M")),
        "<div class=\"proj\">", "".join(cards), "</div>",
        "<div class=\"day\"><b>20 most recent</b><i></i></div><div class=\"card\">"]
    for e in recent[:20]:
        body.append(
            "<div class=\"row\"><span class=\"chip\">{0}</span>"
            "<span class=\"grow\"><a href=\"{1}/{2}\">{3}</a></span>"
            "<span class=\"sz\">{4}</span></div>".format(
                html.escape(e["proj"]), html.escape(e["proj"]),
                html.escape(e["href"]), html.escape(e["name"]), e["date"]))
    body.append("</div>")
    with open(os.path.join(SHELF, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("QA Reports", "".join(body)))


def reindex():
    os.makedirs(SHELF, exist_ok=True)
    for d in sorted(os.listdir(SHELF)):
        p = os.path.join(SHELF, d)
        if os.path.isdir(p) and d != "_manifest":
            write_project_index(p)
    write_root_index()


# --- commands ---------------------------------------------------------------
def cmd_publish(args):
    placed = []
    for src in args.files:
        if not os.path.isfile(src):
            sys.stderr.write("MISSING  {0}\n".format(src))
            return 2
        proj, how = resolve_project(src, args.project)
        date = resolve_date(src, args.date)
        dest_dir = os.path.join(SHELF, proj)
        os.makedirs(dest_dir, exist_ok=True)
        target = unique_target(os.path.join(dest_dir, shelf_name(src, date)))
        shutil.copy2(src, target)
        placed.append((proj, target, how))
        if proj == UNSORTED:
            sys.stderr.write(
                "WARNING  no project resolved for {0} - landed in {1}. "
                "Re-run with --project <NAME>.\n".format(
                    os.path.basename(src), UNSORTED))
    if not args.no_index:
        reindex()
    for proj, target, how in placed:
        print("{0}  ->  {1}   ({2})".format(os.path.basename(target), target, how))
    return 0


def sweep_plan(include_process_docs):
    moves = []
    for n in sorted(os.listdir(DOWNLOADS)):
        src = os.path.join(DOWNLOADS, n)
        if os.path.isdir(src):
            if n in FOLDER_MOVES:
                moves.append((src, os.path.join(SHELF, FOLDER_MOVES[n], n), "folder"))
            continue
        if os.path.splitext(n)[1].lower() not in SWEEP_EXTS:
            continue
        if n in PROCESS_DOCS:
            if include_process_docs:
                d = resolve_date(src)
                moves.append((src, os.path.join(SHELF, PROCESS_DOCS_PROJECT,
                                                shelf_name(src, d)), "process-doc"))
            continue
        proj, _ = resolve_project(n)
        if proj == UNSORTED:
            continue  # not a QA report - leave it where it is
        d = resolve_date(src)
        moves.append((src, os.path.join(SHELF, proj, shelf_name(src, d)), "report"))
    return moves


def cmd_sweep(args):
    moves = sweep_plan(args.include_process_docs)
    tally = Counter(os.path.basename(os.path.dirname(dst)) for _, dst, _ in moves)
    print("{0} - {1} items".format("APPLYING" if args.apply else "DRY RUN",
                                   len(moves)))
    for k in sorted(tally):
        print("  {0:<14} {1}".format(k, tally[k]))
    if not args.apply:
        print("\nNothing moved. Re-run with --apply.")
        for src, dst, kind in moves[:10]:
            print("  {0:<12} {1}".format(kind, os.path.basename(src)))
        if len(moves) > 10:
            print("  ... and {0} more".format(len(moves) - 10))
        return 0

    os.makedirs(MANIFEST_DIR, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    mpath = os.path.join(MANIFEST_DIR, "sweep-{0}.csv".format(stamp))
    done = 0
    failed = []
    with open(mpath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "from", "to"])
        for src, dst, kind in moves:
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if kind == "folder":
                    if os.path.exists(dst):
                        failed.append((src, "target folder already exists"))
                        continue
                else:
                    dst = unique_target(dst)
                shutil.move(src, dst)
                w.writerow([kind, src, dst])
                done += 1
            except Exception as exc:  # noqa: BLE001 - report, never abort the sweep
                failed.append((src, str(exc)))
    reindex()
    print("\nmoved   {0}".format(done))
    print("failed  {0}".format(len(failed)))
    for src, why in failed:
        print("  {0}  <-  {1}".format(why, os.path.basename(src)))
    print("manifest {0}".format(mpath))
    print("undo:    python report-shelf.py undo \"{0}\"".format(mpath))
    return 0


def cmd_undo(args):
    with open(args.manifest, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n = 0
    for r in reversed(rows):
        if os.path.exists(r["to"]):
            os.makedirs(os.path.dirname(r["from"]), exist_ok=True)
            shutil.move(r["to"], r["from"])
            n += 1
    reindex()
    print("restored {0} of {1}".format(n, len(rows)))
    return 0


def cmd_reindex(args):
    reindex()
    print("indexes rebuilt under {0}".format(SHELF))
    return 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("publish", help="copy finished report(s) onto the shelf")
    p.add_argument("files", nargs="+")
    p.add_argument("--project", help="project folder name, e.g. ABC-Web")
    p.add_argument("--date", help="YYYY-MM-DD (default: from filename, else mtime)")
    p.add_argument("--no-index", action="store_true")
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("sweep", help="move loose reports out of the Downloads root")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--include-process-docs", action="store_true")
    p.set_defaults(func=cmd_sweep)

    p = sub.add_parser("reindex", help="rebuild every index.html")
    p.set_defaults(func=cmd_reindex)

    p = sub.add_parser("undo", help="reverse a sweep")
    p.add_argument("manifest")
    p.set_defaults(func=cmd_undo)

    args = ap.parse_args()
    if not getattr(args, "func", None):
        ap.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
