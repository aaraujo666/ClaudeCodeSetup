# issue_digest

[Back to index](../README.md)

## Signature

```python
issue_digest(project='', since='week', until='', stale='14d', full=False, format='text', repo='', instance='')
```

What CHANGED since a date, grouped by project — the read a session opens with after a gap, and the one neither time_report (hours, closed issues only) nor project_status (a snapshot with no memory) answers. `project` is a project ref or '*' for every project the token can see. Five buckets per project: OPENED (created in the window), CLOSED (with the time logged), IN-PROGRESS, TOUCHED (moved in the window but none of the above — a comment, a label change, an edit) and STALE (crossed the staleness line while the window was running).

A project with no activity is OMITTED rather than shown as five zeroes. The buckets are VIEWS over the window, not a partition: an issue opened AND closed inside it is counted in both, so they do not sum to the total. Every count states that total as its denominator, and the report says it in a line. Two caveats worth knowing, because both are approximations named for what they measure.

IN-PROGRESS is the issues CARRYING status::in-progress that moved in the window — not a label-change history, which is a per-issue endpoint a digest over hundreds of issues cannot pay for (work_queue is the read that does, and it caps the lookups). TOUCHED does not distinguish a comment from a label change: the list payload carries a LIFETIME note count with no dates on it. `since` (default 'week') and `until` take 'today', 'yesterday', 'week', 'month', '7d', or an ISO date/datetime; boundaries are LOCAL and the window is half-open.

The resolved window is echoed back — including on an empty answer, since a half-open local boundary is the usual reason an empty result is a surprise. `stale` takes '14d' (the default), 'week' or an ISO date and sets the staleness period; stale='' turns that bucket off. ONE issue sweep answers all five, reaching back one staleness period before `since` so the stale bucket costs no second fetch.

Under '*' that sweep is a GraphQL query which also carries the project count — the digest omits the quiet ones, so without it '6 with activity' would have no denominator — plus one follow-up per project whose window overflowed a hundred issues. Measured on this instance over three weeks and 1,183 issues, that is 2 requests where REST was 13 — and about 2.5s SLOWER for it when the host is healthy, which is the trade rather than a speedup.

A named project stays on REST, where it is already one page; GITLAB_GRAPHQL=0 pins the sweep back to REST, and a query this instance's schema refuses falls back to REST with a NOTE on the report rather than silently. Text output is bounded: past 24 issue rows it drops to the ROLL CALL — one line per project with its counts, which is what fits a screen at 25 projects — and says how many rows it withheld.

`full=True` lists them; the structured formats never clip. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The read to open a session with after a GAP, where project_status is the one to open it with after five minutes. Its buckets are VIEWS over the window, not a partition — an issue opened and closed in it is in both — and two of them are approximations named for what they measure: `in-progress` is the label an issue CARRIES, not a label history, and `touched` cannot tell a comment from an edit.

## Example

```python
issue_digest('*', since='week')   # what changed since you last looked
```
