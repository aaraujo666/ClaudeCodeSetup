# mr_list

[Back to index](../README.md)

## Signature

```python
mr_list(project='', state='opened', author='', target_branch='', source_branch='', since='', limit=20, full=False, format='text', repo='', instance='')
```

List a project's merge requests — the 'what is proposed, against what' read. Returns `!iid state source -> target [draft] pipeline title` per MR, newest-updated first, tallied by state. `state` is opened (default), closed, merged or all — validated locally. `author` is a username or a numeric user id; `target_branch` / `source_branch` filter to one branch each. `since` takes 'today', 'yesterday', 'week', 'month', '7d' or an ISO date, applied to updated_at — the same LOCAL half-open vocabulary as the reporting reads, echoed back resolved.

`limit` caps the rows (default 20). The pipeline column is whatever the LIST payload carries: GitLab dropped head_pipeline from it for performance, so on 17.3 it reads '-' and the report says so. mr_show has the real one, for free. This read never costs a second request per row. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The pipeline column is whatever the LIST payload carries, and GitLab dropped head_pipeline from it — so it reads '-' and the report says why. This read never costs a second request per row; mr_show has the real pipeline for free.

## Example

```python
mr_list('root/gitlab-mcp', state='opened', target_branch='master')
```
