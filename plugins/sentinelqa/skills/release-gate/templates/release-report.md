# Release Quality Report Template

The deliverable. Every section appears — if one doesn't apply, say "None" rather than dropping
it. A silently omitted section reads as "nothing to report" when it may mean "not checked".

Sections 1 and 2 come first for a reason: **what the release contains, and what we don't know
about it, outrank every metric below them.**

---

```markdown
# Release Quality Report — <fix-version>

**Fix version:** <version>
**Build:** <build/branch — and how it was confirmed>
**Environment assessed:** <name, URL>
**Capability level:** 1 Scope only | 2 Reports | 3 Reports + repo/CI/production
**Date:** <absolute date>
**Prepared for:** <the person who owns the release decision>

## Release Recommendation

> **RELEASE READY** | **RELEASE READY WITH ACCEPTED ISSUES** | **NOT RELEASE READY** | **BLOCKED — QA INCOMPLETE**

<Two or three sentences. What drove the verdict, and what specifically would change it.>

---

## 1. What this release contains

**Tickets in fix-version:** <n> (enumerated from Jira, not from the reports received)

| Ticket | Title | Per-ticket verdict | Report | Level |
|--------|-------|--------------------|--------|-------|

<One row per ticket in the fix-version — including every ticket with no report.>

## 2. QA coverage of the release itself

| | Count | Tickets |
|---|---|---|
| Executed QA report (Level 3) | | |
| Report exists, analysis only — never executed | | |
| **No QA report found** | | |

<If either of the last two rows is non-empty, the verdict cannot be a clean RELEASE READY.
Say here what must be produced to close it, per ticket.>

## 3. Verdict rollup

| Per-ticket verdict | Count | Tickets |
|---|---|---|
| READY | | |
| READY WITH KNOWN ISSUES | | |
| NOT READY | | |
| BLOCKED — CLARIFICATION REQUIRED | | |
| No verdict (no report) | | |

**Worst-case constraint applied:** <which row set the ceiling on the release verdict>

## 4. Open defects across the release

### User-reachable bugs
| ID | Ticket | Severity | Priority | Summary | Status |

### Edge / validation bugs
| ID | Ticket | Severity | Priority | Summary | Status |

### Role / permission findings
| ID | Ticket | Severity | Summary | Status |

### System-flaw findings
| ID | Ticket | Severity | Summary | Status |

<Classes stay separate, exactly as in the per-ticket reports. Never merge them to shorten
the list.>

### Accepted for this release
| ID | Severity | Summary | Accepted by | Rationale |

<Every accepted issue is named with who accepted it. An unnamed "known issue" is an
unresolved defect — put it in the tables above instead.>

### Known — not re-raised
| KF ID | Symptom | Verdict | Ledger reference |

## 5. Coverage debt

| Ticket | Blocked | Not Executed | Reason |

**Total across release:** Pass <n> · Fail <n> · Blocked <n> · Not Executed <n>

<Every Blocked and Not Executed keeps its reason. Never net these out into a pass rate.>

**Areas deliberately not tested this release:** <what and why>

## 6. Cross-ticket interaction risk

<Per references/interaction-risk.md>

| Shared surface | Tickets | Combined scenario | Tested? | Assessment |

<Every module touched by 2+ tickets appears here — either with a named scenario or an explicit
"no interaction identified". Findings here are Potential unless reproduced.>

**Confidence in this section:** <state plainly if it rests on thin regression sections>

## 7. Regression and production signals

**Regression suite:** <executed / not executed — results, and against which build>
**Flaky or quarantined tests affecting this scope:** <list, or None>
**Production signals:** <error rates, incidents, monitoring for the touched surfaces — or
"not available">

<At Level 1 or 2 say "not available" rather than omitting the section.>

## 8. Unresolved requirement gaps

| # | Ticket | Question | Why it matters | Blocking? |

<Carried forward from the per-ticket reports. Any row marked Blocking means the release
verdict cannot be READY.>

## 9. Evidence and provenance

**Reports read in full:** <n of n>
**Reports available only as summaries:** <which — and note the rollup is weaker for them>
**AI-drafted artifacts in this release's QA:** <which, and that a human reviewed them, or None>
**Ledger consulted:** <yes/no — path>
```

---

## Choosing the recommendation

| Verdict | When |
|---|---|
| **RELEASE READY** | Every ticket has an executed report and a READY verdict. No open defects above trivial. No blocking gaps. No untested interaction risk. |
| **RELEASE READY WITH ACCEPTED ISSUES** | Works for the intended use. Every open defect is listed and explicitly accepted by a named person. Recording a decision, not making an observation. |
| **NOT RELEASE READY** | Defects block the intended use, or core coverage failed, and nobody has accepted them. |
| **BLOCKED — QA INCOMPLETE** | Coverage is unknown for part of the release. The question is upstream, not in the build — different problem, different fix, so never collapse it into NOT RELEASE READY. |

Two rules carried over from the per-ticket report, and one that is specific to this one:

- **Never RELEASE READY over unexecuted coverage.**
- **The verdict is a recommendation, not a decision.** Shipping is the user's call.
- **The unknown outranks the known.** A release with three documented bugs is in better shape
  than a release with four untested tickets. Order the report so the reader sees that first —
  it is the fact most often lost in a metrics summary.
