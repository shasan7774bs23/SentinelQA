"""case-file-audit.py — prove the STATIONS ran, not just that the report looks right.

Usage:  python case-file-audit.py qa/ABC-123
        python case-file-audit.py qa/ABC-123 --pre-s3   (gates A+B only; run BEFORE executing)

Why this exists
---------------
on a past multi-ticket run, every ticket's report passed report-audit.py,
while 00-intake.yml / 01-requirement.md / 02-plan.md / 06-decisions.md were missing on every one.
S1 and S2 never ran; Gates A, B and C never fired. report-audit.py could not see that, because it
only ever opens the report. A report can be perfectly structured and still be built on a plan that
was never written, never reviewed and never approved.

This audit opens the CASE FILE. Run it twice:
  * --pre-s3  after S2, before any live execution  -> proves Gate A and Gate B fired
  * full      before S4 closeout                   -> proves Gate C fired and evidence exists

Exit code 1 on any failure. A failure is a STOP, not a warning.
"""
import io
import os
import re
import sys

REQUIRED = [
    ("00-intake.yml",     "S0", "triage + run context"),
    ("01-requirement.md", "S1", "business rules + gaps"),
    ("02-plan.md",        "S2", "the suite approved at Gate B"),
    ("03-pass1.md",       "S3", "codebase predictions, write-once"),
    ("05-report.md",      "S4", "report + verdict"),
    ("06-decisions.md",   "--", "APPEND-ONLY gate decisions"),
]
PRE_S3 = {"00-intake.yml", "01-requirement.md", "02-plan.md", "06-decisions.md"}

# An unfilled template placeholder means the file was created but never actually written.
PLACEHOLDER = re.compile(r"<[A-Za-z0-9 _/|.-]{2,40}>")
OUTCOME = re.compile(r"\b(APPROVED|REJECTED|CLARIFICATION REQUIRED|WITHDRAWN|CONFIRMED)\b")

fails = []
warns = []


def fail(code, msg):
    fails.append((code, msg))


def warn(code, msg):
    warns.append((code, msg))


def read(p):
    try:
        return io.open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pre_s3 = "--pre-s3" in sys.argv
    if not args:
        print("usage: case-file-audit.py qa/<TICKET-KEY> [--pre-s3]")
        return 2
    case = args[0].rstrip("/\\")
    ticket = os.path.basename(case)

    if not os.path.isdir(case):
        print("FAIL C0  case file directory does not exist: " + case)
        print("         The run has no spine. Open qa/<TICKET>/ at S0 before anything else.")
        return 1

    present = set(os.listdir(case))

    # ---- C1: the required artifacts exist --------------------------------------------------
    for name, station, what in REQUIRED:
        if pre_s3 and name not in PRE_S3:
            continue
        if name not in present:
            fail("C1", "%-18s MISSING  -> station %s (%s) did not run" % (name, station, what))

    # ---- C2: evidence directory exists and is not empty ------------------------------------
    if not pre_s3:
        ev = os.path.join(case, "04-evidence")
        if not os.path.isdir(ev):
            fail("C2", "04-evidence/ MISSING -> no live execution evidence was captured")
        else:
            n = len([f for f in os.listdir(ev) if not f.startswith(".")])
            if n == 0:
                fail("C2", "04-evidence/ is EMPTY -> every case in this run is an assertion, "
                           "not a result")
            elif n < 3:
                warn("C2", "04-evidence/ holds only %d file(s) - thin for a full run" % n)

    # ---- C3: the intake actually carries a confirmed run context ---------------------------
    ipath = os.path.join(case, "00-intake.yml")
    if os.path.exists(ipath):
        txt = read(ipath)
        for key in ("build_deployed", "build_confirmed_how", "test_account", "deployed_site"):
            m = re.search(r"^\s*%s:\s*(.+)$" % key, txt, re.M)
            if not m:
                fail("C3", "00-intake.yml has no '%s' - the run context was never confirmed" % key)
            elif PLACEHOLDER.search(m.group(1)) or m.group(1).strip() in ('""', "''", ""):
                fail("C3", "00-intake.yml '%s' is still a template placeholder -> "
                           "assumed, not confirmed" % key)

    # ---- C4: the decisions log records a real outcome per gate -----------------------------
    dpath = os.path.join(case, "06-decisions.md")
    if os.path.exists(dpath):
        d = read(dpath)
        gates = ["A", "B"] if pre_s3 else ["A", "B", "C"]
        for g in gates:
            m = re.search(r"##\s*Gate\s*%s\b(.*?)(?=\n##\s|\Z)" % g, d, re.S | re.I)
            if not m:
                fail("C4", "06-decisions.md has no 'Gate %s' section -> that gate never fired" % g)
                continue
            body = m.group(1)
            if not OUTCOME.search(body):
                fail("C4", "Gate %s is present but records no outcome "
                           "(APPROVED / REJECTED / CLARIFICATION REQUIRED) -> "
                           "it was documented, not decided" % g)
            if not re.search(r"\b20\d\d-\d\d-\d\d\b", body):
                warn("C4", "Gate %s carries no date - an approval with no timestamp is not "
                           "traceable" % g)
            if not re.search(r"(Reviewer|Approver|Decided by)\s*:", body, re.I):
                fail("C4", "Gate %s names no reviewer -> 'a human approved this' is a claim, "
                           "not a fact" % g)

    # ---- C5: no BUG reached the report without passing Gate C ------------------------------
    if not pre_s3:
        rpath = os.path.join(case, "05-report.md")
        if os.path.exists(rpath) and os.path.exists(dpath):
            bugs = set(re.findall(r"\bBUG-\d+\b", read(rpath)))
            dtxt = read(dpath)
            unvalidated = sorted(b for b in bugs if b not in dtxt)
            if unvalidated:
                fail("C5", "filed without a Gate C decision: %s  -> A PREDICTION IS NOT A DEFECT. "
                           "Validate it, withdraw it, or move it to 'Unverified predictions' with "
                           "no severity." % ", ".join(unvalidated))

    # ---- report -----------------------------------------------------------------------------
    mode = "PRE-S3 (gates A+B)" if pre_s3 else "FULL"
    print("case-file-audit  %s  [%s]" % (ticket, mode))
    print("-" * 72)
    for code, msg in fails:
        print("FAIL %-4s %s" % (code, msg))
    for code, msg in warns:
        print("warn %-4s %s" % (code, msg))
    print("-" * 72)
    if fails:
        print("RESULT: %d FAILURE(S). The run is NOT complete - do not write or ship the report." % len(fails))
        print("        A station that did not run cannot be back-filled from the report.")
        return 1
    print("RESULT: PASS%s" % ("  (%d warning(s))" % len(warns) if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
