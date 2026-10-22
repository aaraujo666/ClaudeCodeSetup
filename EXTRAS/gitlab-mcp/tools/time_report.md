# time_report

[Back to index](../README.md)

## Signature

```python
time_report(project='', since='today', until='', group_by='project', format='text', repo='', by='closed', instance='')
```

Roll up logged time over a date window — the 'what did I close today, and how long did it take' read. `project` is a project ref or '*' for every project the token can see. `since` / `until` take 'today', 'yesterday', 'week', 'month', '7d', or an ISO date/datetime (default: since local midnight today, no upper bound). Boundaries are LOCAL time and the window is half-open, so since='2026-08-14' + until='2026-08-15' is exactly that day.

The window is on the CLOSE date. `group_by` is project|day|none. Output is per-issue rows (ref, spend, close time, title) with a subtotal per group and a grand total, durations as '1h30m' rather than raw seconds. Issues closed with spend='0' — epics, duplicates — are counted and listed separately instead of diluting the total. A `tracking` issue (#157) gets its OWN zero-spend line rather than being folded into that one: its zero is correct — the children carry the time — but unlike a moved stub that time is never logged anywhere else, so hiding it would understate the total.

Caveat worth knowing, and now OPTIONAL rather than absolute: by default a row's spend is the issue's LIFETIME total credited to the day it closed, because GitLab's REST API exposes no per-timelog dates. That is exact under the close protocol (time is logged at close) and approximate for an issue logged against incrementally. `by` is closed|spent (default closed, and today's numbers do not move).

`by='spent'` reads the dated timelog entries over GraphQL — one query for the whole report, no per-issue request — and credits each issue's hours to the days they were LOGGED on. The window still selects issues by `closed_at` either way: this changes which day an issue's hours land on, never which issues appear. Hours logged before the window are shown WHERE THEY FALL rather than clipped to it, so the day rows can extend past the window's start and the report says so; clipping would make the daily rows stop summing to the issue's logged total.

An issue whose entries cannot be read keeps its close-date credit and is NAMED — never rendered as zero hours. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Example

```python
time_report('*', since='week', group_by='day')
```
