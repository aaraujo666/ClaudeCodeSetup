# tracker_sync

[Back to index](../README.md)

## Signature

```python
tracker_sync(tracker_path, project='', issue=0, create=False, title='', labels='', intro='', dry_run=False, repo='', instance='')
```

Mirror a checkbox test tracker (TESTING-*.md) into a GitLab issue: each case becomes a live task-list checkbox (drives the progress bar) plus an expandable <details> plan. `tracker_path` is an ABSOLUTE path to the .md. Provide EITHER `issue` (an existing iid to overwrite in place) OR create=True with a title. dry_run=True returns the generated markdown without touching GitLab. `repo` (path to the repo checkout) supplies `project` from its .gitlab-tools.json when you don't pass one.

NOTE: the .md is the source of truth — syncing OVERWRITES the issue description, so fold any browser-ticked boxes back into the .md first.

## Required

`tracker_path`
