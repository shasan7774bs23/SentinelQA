#!/usr/bin/env python3
"""
QA report closeout audit — EXECUTABLE, not a checklist you tick from memory.

    python report-audit.py <TICKET>-QA-Report.md [evidence_dir]

Exit 0 = clean. Exit 1 = gaps found; fix the FILE and re-run. Never hand-wave a FAIL.
The whole point: you cannot "remember" having done this. It either ran and passed, or it did not.

Checks encode the hard rules in SKILL.md. When a rule changes, change this too.

"""
import os
import re
import sys
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESET, RED, GRN, YEL, DIM = "\033[0m", "\033[31m", "\033[32m", "\033[33m", "\033[2m"
fails, warns = [], []


def fail(code, msg):
    fails.append(f"{code}: {msg}")


def warn(code, msg):
    warns.append(f"{code}: {msg}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"{RED}report not found: {path}{RESET}")
        return 2
    t = open(path, encoding="utf-8").read()
    ev_dir = sys.argv[2] if len(sys.argv) > 2 else None
    if not ev_dir:
        for c in ("04-evidence", "evidence"):
            for base in (os.path.dirname(path) or ".", "."):
                p = os.path.join(base, c)
                if os.path.isdir(p):
                    ev_dir = p
                    break

    # Screenshots may be cited as `name.png`, as a Markdown image ![x](path/name.png), or as <img src>.
    # All three count everywhere below, so the audit and report-html.py never disagree.
    def image_refs(text):
        names = set(re.findall(r"`([^`\n]+\.(?:png|jpg|jpeg|gif|webp))`", text, re.I))
        for m in re.finditer(r"!\[[^\]]*\]\(\s*<?([^)>\n]+?)>?(?:\s+\"[^\"]*\")?\s*\)", text):
            names.add(os.path.basename(urllib.parse.unquote(m.group(1).strip())))
        for m in re.finditer(r"<img[^>]+src=[\"']([^\"']+)[\"']", text, re.I):
            if not m.group(1).startswith("data:"):
                names.add(os.path.basename(urllib.parse.unquote(m.group(1))))
        return {n for n in names if re.search(r"\.(png|jpe?g|gif|webp)$", n, re.I)}

    no_execution = bool(re.search(r"No execution evidence\s*[—\-]", t))

    # ---- R9b: every executed case carries full anatomy, passes included -------------
    case_hdr = re.compile(r"\n#{2,4} +((?:TC|EX|BUG|LIVE|S|N|O|F)-[\w.]+)[ ·:—-]")
    secs = case_hdr.split(t)
    cases = [(secs[i], secs[i + 1]) for i in range(1, len(secs) - 1, 2)]
    if not cases:
        fail("R9b", "no per-case sections found — a results table is an index, never the record")
    for cid, body in cases:
        body = body.split("\n## ")[0]
        has_steps = bool(re.search(r"\*\*Steps (to reproduce|attempted)\*\*", body)) and \
                    bool(re.search(r"^\s*1\. ", body, re.M))
        missing = [n for n, ok in (
            ("numbered Steps", has_steps),
            ("Expected", "**Expected" in body),
            ("Actual", "**Actual" in body),
            ("Evidence", "**Evidence" in body),
        ) if not ok]
        if missing:
            fail("R9b", f"{cid} missing: {', '.join(missing)}")

    # ---- R9b-i: EVERY executed case needs a SCREENSHOT — passes as well as failures ---
    # Added after a past release run shipped several reports that proved their
    # PASSES with JSON and carried almost no images. Rule: a screenshot
    # for passes and failures alike, beside the reproduction steps.
    # A case may omit a screenshot ONLY by stating why, in that case's own body.
    NO_SHOT_REASON = re.compile(
        r"(no screenshot|not rendered|HTTP[- ]level only|status code only|redirect(s)? (back |to )"
        r"|bounce[sd]? to|cannot be photograph|nothing to photograph|not visible in (the )?UI"
        r"|blocked by|refused by|classifier|not reachable|does not exist|not executed)", re.I)
    for cid, body in cases:
        body = body.split("\n## ")[0]
        has_shot = bool(image_refs(body))
        if not has_shot and not NO_SHOT_REASON.search(body):
            fail("R9b-i", f"{cid} has NO screenshot and no stated reason — a passing case needs a "
                          f"picture of it passing, not just an API response. Capture one, or say in "
                          f"that case why a screenshot is impossible.")

    # ---- R9b-i (report level): no report may be entirely screenshot-free ---------------
    # Calibration note: the per-case check above is the strict one — every case needs a screenshot
    # OR an explicit reason. This report-level check deliberately only requires that the report is
    # not ENTIRELY image-free, because a ticket can legitimately have just one UI surface (e.g. an
    # HTTP-only permission denial + a SQL script + a blocked case). It is NOT a licence to justify
    # everything away: a run where most cases have a UI and none has a picture will still fail the
    # per-case check, case by case.
    shots_in_report = image_refs(t)
    if cases and not shots_in_report and no_execution:
        warn("R9b-i", "no screenshot at all - accepted because the report states 'No execution "
                      "evidence'; every case must be Not Executed with its blocker named")
    elif cases and not shots_in_report:
        fail("R9b-i", "this report contains NO screenshot at all. Every report must carry visual "
                      "evidence for what it executed — passes included. Drive the UI and capture it.")

    # ---- R9b-render: numbered steps must RENDER as a list, not a paragraph ----------
    # Markdown needs a BLANK LINE between a bold label and a following list item. Without one,
    # a bold "Steps to reproduce" label followed directly by "1. ..." renders as a single <p>
    # paragraph: the source looks numbered but the reader sees a wall of text.
    # Caught in the field when the rendered HTML contained almost no <ol> elements.
    step_label = r"^\*\*Steps (?:to reproduce|attempted)\*\*[^\n]*\n(?!\s*\n)(\s*\d+\. )"
    for m in re.finditer(step_label, t, re.M):
        ln = t[:m.start()].count("\n") + 1
        fail("R9b-render", f"line {ln}: numbered steps follow the bold label with no blank line — "
                           f"they will render as ONE PARAGRAPH, not a list. Insert a blank line.")

    # Same trap for any bold label immediately followed by a list anywhere in the report.
    generic_label = r"^\*\*[^*\n]+\*\*(?: *\*\([^)]*\)\*)? *\n(?!\s*\n)\s*(?:\d+\.|[-*+]) "
    extra = [t[:m.start()].count("\n") + 1 for m in re.finditer(generic_label, t, re.M)]
    for ln in extra[:10]:
        warn("R9b-render", f"line {ln}: a bold label is followed directly by a list item — "
                           f"check it renders as a list, not a paragraph")

    # ---- R9: defects also need severity + priority ----------------------------------
    for cid, body in cases:
        if cid.split("-")[0] in ("BUG", "S", "F"):
            b = body.split("\n## ")[0]
            if not re.search(r"\bS[1-4]\b", b) or not re.search(r"\bP[0-3]\b", b):
                fail("R9", f"{cid} is a defect but lacks Severity (S1-S4) and/or Priority (P0-P3)")

    # ---- R9d: an UNREPRODUCED finding must not be filed as a severity-carrying BUG ----
    # Added after several "defects" were raised from source reading alone on a past release run
    # and later tested and found NOT to exist. A BUG-n carrying S/P reads as established fact about
    # the product; a source-only prediction is a hypothesis and belongs in "Unverified predictions".
    SEV_RE = re.compile(r"\bS[1-4]\b")
    PRI_RE = re.compile(r"\bP[0-3]\b")
    ATTEMPT_RE = re.compile(
        r"(not reproduced|could not be (attempted|executed|reproduced)|blocked by|refused by"
        r"|classifier|attempted and|verified by|reproduced on verification|confirmed by"
        r"|NOT executed|unverified)", re.I)
    for cid, body in cases:
        if not cid.upper().startswith("BUG"):
            continue
        b = body.split("\n### ")[0]
        has_sev = bool(SEV_RE.search(b) and PRI_RE.search(b))
        reproduced = "Confirmed (reproduced)" in b
        explained = bool(ATTEMPT_RE.search(b))
        if has_sev and not reproduced and not explained:
            fail("R9d", f"{cid} carries a severity/priority but is NOT labelled "
                        f"Confirmed (reproduced) and never says it was attempted or why it could "
                        f"not be. A PREDICTION IS NOT A DEFECT - reproduce it, withdraw it, or move "
                        f"it to an 'Unverified predictions' section with no severity.")

    # ---- R9c: evidence index, cross-checked against the folder BOTH ways ------------
    if not re.search(r"#+ *\d*\.? *Evidence index", t, re.I):
        fail("R9c", "no Evidence index section")
    listed = set(re.findall(r"`([\w][\w\-.]*\.(?:png|jpg|jpeg|gif|webp|pdf|har|json|txt|log))`", t))
    # Any backticked file name counts as a reference (an execution-log.md, a .csv, a .sql...).
    # Only the strict list above is used for "cited but missing", so naming 02-plan.md is not a failure.
    mentioned = set(re.findall(r"`([\w][\w\-.]*\.[A-Za-z0-9]{1,5})`", t)) | image_refs(t)
    if ev_dir and os.path.isdir(ev_dir):
        on_disk = {f for f in os.listdir(ev_dir) if not f.startswith(".")}
        for f in sorted(on_disk - listed - mentioned):
            fail("R9c", f"evidence file on disk but never referenced: {f} "
                        f"(an untold finding, or dead weight — resolve it)")
        for f in sorted(listed - on_disk):
            fail("R9c", f"report cites evidence that does not exist on disk: {f}")
    else:
        warn("R9c", "evidence dir not found — cross-check skipped, do it by hand")

    # ---- R12: no blanket status claim that can drift from its rows ------------------
    for m in re.finditer(r"^.*\b(nothing (in this list )?has been actioned|all (items? )?(are )?drafts?|"
                         r"everything (is )?verified|all checks? passed|no outstanding)\b.*$",
                         t, re.I | re.M):
        warn("R12", f"blanket status claim — re-derive from its rows or delete: {m.group(0).strip()[:90]}")

    # ---- R13: blocked items must name what blocks them ------------------------------
    # Scoped to TABLE ROWS only — prose uses "blocked" to mean "correctly refused", which is
    # not a status. An unscoped scan floods the output with false positives and trains you to
    # ignore warnings, which is worse than not checking.
    for m in re.finditer(r"^\|.*$", t, re.M):
        row = m.group(0)
        if re.search(r"\*\*(blocked|pending|not done)\*\*|(BLOCKED|Pending|Not done)", row) and            not re.search(r"(awaiting|human|decision|approval|permission|outage|disconnect|"
                         r"unavailable|tool|environment|instruction|review|reconnect|not requested)",
                         row, re.I):
            warn("R13", f"status row without a named blocker: {row.strip()[:90]}")

    # ---- Evidence-label discipline ---------------------------------------------------
    if "Confirmed (reproduced)" not in t and "Confirmed (source)" not in t:
        fail("LBL", "no evidence labels (Confirmed (reproduced) / Confirmed (source) / Observed / ...)")

    # ---- Verdict ---------------------------------------------------------------------
    if not re.search(r"\b(READY WITH KNOWN ISSUES|NOT READY|BLOCKED — CLARIFICATION REQUIRED|READY)\b", t):
        fail("VRD", "no explicit verdict (READY / READY WITH KNOWN ISSUES / NOT READY / BLOCKED)")

    # ---- Standard sections required by templates/test-summary.md ----------------
    for label, pat in (
        ("what was NOT tested / coverage not achieved", r"coverage not achieved|not executed|residual risk"),
        ("ledger check", r"ledger check"),
        ("test data left behind", r"test data (left|created)"),
        ("Pass 1 vs Pass 2 reconciliation / own-prediction corrections", r"reconcil|corrections to my own"),
        ("what passed — do not re-test without cause", r"what passed|verified-good|do not re-test"),
        ("colleague-reported issues / prior reports on this ticket", r"colleague|previously reported|prior report|reporter'?s? (own )?(comment|claim)"),
        ("open decisions awaiting the human", r"open decisions|needs? (the lead|the human)|awaiting approval"),
    ):
        if not re.search(pat, t, re.I):
            fail("SEC", f"missing standard section: {label}")

    # ---- The QA canon: "the same standard pattern everywhere,
    #      for all QA agents, in any project." Each check exists because its absence caused a real
    #      failure on a past release run. Matched against HEADINGS, not loose body text: an earlier
    #      draft of these checks passed a weak report because a stray "5/03" date satisfied a ratio regex and
    #      a stray "Not a defect" table cell satisfied a ruled-out regex. A rule that can be
    #      satisfied incidentally is not enforcement.
    headings = re.findall(r"^#{2,4}\s+(.+?)\s*$", t, re.M)
    head_blob = "\n".join(headings)

    def has_heading(pat):
        return bool(re.search(pat, head_blob, re.I))

    # Build confirmation: a heading, OR a probe stated together with its control.
    probe_with_control = bool(
        re.search(r"(route probe|build confirmed|how the build)", t, re.I)
        and re.search(r"(negative control|positive control|\bcontrol\b)", t, re.I))
    if not (has_heading(r"build (was )?confirmed|how the (deployed )?build") or probe_with_control):
        fail("SEC", "no build confirmation WITH A CONTROL. Identify the running binary by server "
                    "behaviour and show the negative control that makes the probe mean something - "
                    "a branch containing a fix is not a build running it, and the footer has been "
                    "wrong on a past run.")

    if not has_heading(r"ruled out|not a defect|do not re-raise|refuted|withdrawn|investigated and"):
        fail("SEC", "no 'suspicions investigated and RULED OUT' section. Every theory you formed "
                    "and then disproved - your own included - belongs in its own section, or the "
                    "next run rediscovers it. A run with nothing ruled out usually means "
                    "suspicions were filed instead of tested.")

    # ---- R9e: a BLOCKED / not-executed case must name its blocker ----
    # "Blocked by a tool" is not "awaiting a human". An unexplained BLOCKED row reads as coverage.
    BLOCKWORDS = re.compile(
        r"(permission|account|role|fixture|irreversible|outage|unreachable|not provisioned"
        r"|awaiting|decision|needs? (a|an|the)|requires|no .{0,24}(control|path|access)"
        r"|depends on|same blocker|environment|scenario (does not|doesn't) exist|absent)", re.I)
    for cid, body in cases:
        b = body.split("\n### ")[0]
        if re.search(r"\b(BLOCKED|Not Executed|NOT EXECUTED)\b", b) and not BLOCKWORDS.search(b):
            fail("R9e", f"{cid} is BLOCKED/Not Executed but names no blocker. Say WHICH: a human "
                        f"decision, a missing permission/account/fixture, or a tool/environment "
                        f"outage. A blocked case is not evidence the feature works.")

    # ---- R9f: coverage stated as a COUNT, in a coverage context ----
    # "comprehensive coverage" is unfalsifiable. "18 of 26 rules" can be checked - and it is the
    # denominator that exposed a 19%-coverage run reading as six green passes.
    ratio_line = None
    for line in t.splitlines():
        if re.search(r"\b\d+\s*(?:of|/)\s*\d+\b", line) and \
           re.search(r"(rule|criteri|coverage|scenario|requirement|AC-)", line, re.I):
            ratio_line = line.strip()
            break
    if not ratio_line:
        fail("R9f", "coverage is never stated as a ratio against the rules extracted "
                    "(e.g. '18 of 26 rules'). A table of passes is not a coverage figure: without "
                    "a denominator, six passes read as complete when they were 19%.")

    # ---- Report ----------------------------------------------------------------------
    print(f"\n{DIM}report:{RESET} {path}   {DIM}cases parsed:{RESET} {len(cases)}   "
          f"{DIM}evidence listed:{RESET} {len(listed)}")
    for w in warns:
        print(f"{YEL}  WARN  {w}{RESET}")
    if fails:
        for f in fails:
            print(f"{RED}  FAIL  {f}{RESET}")
        print(f"\n{RED}AUDIT FAILED — {len(fails)} gap(s). Fix the FILE and re-run. "
              f"Do not paper over this in prose.{RESET}\n")
        return 1
    print(f"\n{GRN}AUDIT PASSED{RESET} ({len(warns)} warning(s) to eyeball)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
