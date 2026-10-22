# issue_milestone

[Back to index](../README.md)

## Signature

```python
issue_milestone(project='', iids, milestone, repo='', instance='')
```

Assign a BATCH of issues to a milestone — the release-prep companion to issue_bulk, and the same argument shape: `iids` is comma-separated numbers and ranges ('12,14-16', or a mix). `milestone` is its TITLE ('v1.4') or numeric id; pass milestone='' to take the issues OFF whatever milestone they are on. The milestone is resolved ONCE before anything is written, so a title that does not exist cannot leave the first six issues assigned and the rest not.

Issues are INDEPENDENT: one failing does not abort the others. Idempotent per issue — one already on the milestone reports 'no change' and is not written. An iid that does not exist is named as such rather than returned as a 404. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The batch form, same iids-and-ranges as issue_bulk. The milestone is resolved ONCE before the first write; milestone='' takes issues off one.

## Example

```python
issue_milestone('root/gitlab-mcp', iids='16-18,23', milestone='v1.4')
```

## Required

`iids`, `milestone`
