# github_sync

[Back to index](../README.md)

## Signature

```python
github_sync(project='', source='', since='', comments=True, dry_run=False, limit=0, default_type='', repo='', instance='')
```

Mirror a GitHub repo's issues into a GitLab project — one-way, idempotent, safe to re-run. `source` is 'owner/repo'; `project` is the GitLab target. Each mirrored issue carries a `<!-- gh:owner/repo#N updated=... -->` marker in its description, which IS the mapping: a second run creates nothing, and an issue edited upstream is updated in place. Closed upstream closes here (state_reason 'not_planned' -> status::wontfix, otherwise status::done).

Labels are set ONCE at creation and never rewritten, so local triage survives a sync. Pull requests are never imported. `since` (ISO date) narrows the GitHub fetch for a scheduled run; leaving it empty is always correct and just slower. comments=True also mirrors each upstream comment as a note, once. dry_run=True reports the plan and writes nothing. Needs GITHUB_TOKEN (a CLASSIC PAT with `repo` scope).

`repo` (path to a checkout) supplies `project` and the `github` block from its .gitlab-tools.json.

## Convention

One-way and idempotent: the mapping is a marker in each mirrored description, NOT a state file, so it survives a lost checkout and a re-run costs nothing. Labels are written ONCE at creation and never rewritten — local triage on a mirrored issue outlives every later sync. Upstream STATE is authoritative, so an issue reopened here is re-closed. Pull requests are never imported. Needs GITHUB_TOKEN: a CLASSIC PAT with `repo` scope, since a fine-grained one cannot read another user's private repo.
