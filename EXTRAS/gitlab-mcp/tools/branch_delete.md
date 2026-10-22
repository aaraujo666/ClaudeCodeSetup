# branch_delete

[Back to index](../README.md)

## Signature

```python
branch_delete(project='', branch, force=False, repo='', instance='')
```

Delete a branch on the remote. TWO REFUSALS, and they are deliberately different: a PROTECTED branch is refused outright and no argument here overrides it — protection is a decision made in the project's settings, and a tool that shrugged past it would make the setting a suggestion. An UNMERGED branch (not merged into the default branch) is refused unless force=True, because 'not on the trunk' is routinely true of a branch whose merge request was closed on purpose.

The default branch is refused outright as well. IDEMPOTENT: a branch that is already gone reports 'no change' rather than a 404, so a retried cleanup is safe. The report names the commit that was deleted, which is what makes an accidental delete recoverable — the SHA is still reachable until GitLab's next housekeeping. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Required

`branch`
