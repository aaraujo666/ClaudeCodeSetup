# project_events

[Back to index](../README.md)

## Signature

```python
project_events(project='', action='', target_type='', since='', until='', sort='desc', limit=20, format='text', repo='', instance='')
```

List a project's activity feed (its events): who did what, to which issue, merge request or ref, and when. Answers 'when was the first issue closed' (action='closed', target_type='issue', sort='asc', limit=1) and 'what happened on day X' (since/until) without raw REST. `action` is one of approved, closed, commented, created, destroyed, expired, joined, left, merged, pushed, reopened, updated; `target_type` one of issue, milestone, merge_request, note, project, snippet, user; `sort` asc or desc (default newest first).

`since`/`until` take the same vocabulary as the reporting reads ('today', 'week', '7d', an ISO date), resolved LOCAL, half-open [since, until), and echoed back resolved. `limit` caps the rows (default 20). Returns `date time author action target title` per event, the target being #iid for an issue, !iid for a merge request, the ref for a push. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Example

```python
project_events('root/gitlab-mcp', action='closed', target_type='issue', sort='asc', limit=1)
```
