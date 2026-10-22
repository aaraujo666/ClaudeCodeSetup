# gitlab_audit

[Back to index](../README.md)

## Signature

```python
gitlab_audit(since='', tool='', project='', full=False, format='text')
```

Read the AUDIT TRAIL: one record per mutating tool call this server has made — timestamp, tool, instance, project, the iids it touched, the arguments it was given (credentials redacted) and how it ended. Newest first. This is the local record GitLab's activity feed is not: cross-project, cross-instance, greppable, and it names the TOOL and its arguments rather than only the change.

Mutations only — reads are never recorded, or they would drown it. ONE record per call, never per row: issue_bulk over '12,14-16' is a single record carrying all four iids, so a batch reads back as the batch it was. since= takes 'today', 'week', '7d' or an ISO date; tool= and project= are exact matches. Touches no GitLab and takes no `instance` — the trail is a fact about this machine and holds every instance's calls; each row says which one it addressed.

The file is ~/.local/state/gitlab-mcp/audit.jsonl (GITLAB_AUDIT moves it, GITLAB_AUDIT=off turns recording off).
