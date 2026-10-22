# branch_list

[Back to index](../README.md)

## Signature

```python
branch_list(project='', merged=None, stale='', limit=30, full=False, format='text', repo='', instance='')
```

List a project's BRANCHES, without cloning: name, last commit date and author, how far each has diverged from the default branch, and whether it is protected or already merged. The release-prep read — what is still open, what has gone quiet, what is safe to delete. `merged` is tri-state (None lists everything, True only branches already merged into the default branch, False only the unmerged ones).

EITHER filter EXCLUDES THE DEFAULT BRANCH: GitLab reports the trunk's own `merged` as false — it is not merged into itself — so an unqualified merged=False would open every 'what is still open' listing with the one branch nobody is cleaning up. Unfiltered it is still listed, first, because there it is the baseline the ahead/behind column is measured against. `stale` takes '30d', 'week', 'month' or an ISO date and keeps only branches whose last commit is OLDER than that boundary, resolved as a LOCAL boundary and echoed back resolved — the same vocabulary as project_status.

AHEAD/BEHIND IS COUNTED, AND IT COSTS TWO REQUESTS PER BRANCH: GitLab carries no divergence on a branch payload, so it is measured for the first 20 rows shown and every row past that reads '?/?'. `?` is not 0 — a divergence nobody measured and a branch that is level are different answers. The default branch reads 0/0 by definition and is never compared with itself. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.
