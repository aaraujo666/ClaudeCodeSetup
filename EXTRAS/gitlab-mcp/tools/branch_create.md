# branch_create

[Back to index](../README.md)

## Signature

```python
branch_create(project='', branch, ref='', repo='', instance='')
```

Create a branch on the remote from a ref, without a checkout. `branch` is the new name; `ref` is what it is cut from — a branch, tag or SHA, defaulting to the project's DEFAULT BRANCH read from the API rather than guessed between main and master. IDEMPOTENT, and it never MOVES a branch: a name that already exists is reported with the commit it points at rather than created, and if that commit is not the one `ref` names, the report says the branch was left alone.

Moving an existing branch to a new ref is a force-push, not an idempotent create, so no argument here does it. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Required

`branch`
