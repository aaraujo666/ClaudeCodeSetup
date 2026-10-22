# commit_list

[Back to index](../README.md)

## Signature

```python
commit_list(project='', ref='', since='', limit=20, format='text', repo='', instance='')
```

List recent commits on a ref, without cloning. `ref` is a branch, tag or SHA (default: the project's default branch). `since` takes 'today', 'yesterday', 'week', 'month', '7d' or an ISO date — the same vocabulary as the reporting reads, resolved as a LOCAL boundary and echoed back resolved. `limit` caps the rows (default 20). Returns `short-sha date author title` per commit, newest first, with the count and the window.

Use it to see what actually landed on the remote from a session whose checkout may be behind — and to get the full SHA that issue_close(commit=…) should quote. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Example

```python
commit_list('root/gitlab-mcp', since='week')
```
