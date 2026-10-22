# mr_show

[Back to index](../README.md)

## Signature

```python
mr_show(project='', iid, full=False, format='text', repo='', instance='')
```

Show ONE merge request in full: title, state, source -> target, author, description, its detailed merge status, WHO HAS APPROVED IT, the count of UNRESOLVED discussion threads, its commits, and THE FILES IT CHANGED with +/- on each. That last list is the point. It is what lets a review read what a branch did WITHOUT a checkout — the same argument repo_file and commit_show were built on, and the answer that stays right when the local clone is behind.

The +/- numbers are counted from the diff GitLab returns (its payload carries no numeric stat); a file GitLab would not diff — binary, or too large — shows '-' rather than a zero that would read as 'unchanged'. `detailed_merge_status` is reported, never the deprecated `merge_status`: the old field answers `cannot_be_merged` for a conflict, a failing pipeline and a missing approval alike, while the detailed one names the actual blocker.

Long descriptions and file lists are clipped with a count — full=True for the rest. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The changed-file list is the point: it reads what a branch did with NO checkout. +/- is COUNTED from the diff — GitLab's payload has no numeric stat — and a file it would not diff (binary, too large) shows '-', not a zero. Reports detailed_merge_status, never the deprecated merge_status, which answers cannot_be_merged for a conflict, a failing pipeline and a missing approval alike.

## Example

```python
mr_show('root/gitlab-mcp', iid=4)
```

## Required

`iid`
