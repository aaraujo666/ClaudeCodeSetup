# milestone_create

[Back to index](../README.md)

## Signature

```python
milestone_create(project='', title, due='', start='', description='', repo='', instance='')
```

Create a milestone — the release a batch of issues gets assigned to. `title` is the release name ('v1.4'). `due` takes 'today', 'week', '7d' or an ISO date, resolved as a LOCAL boundary; `start` the same. `description` is optional. IDEMPOTENT, and that matters here: GitLab will happily create a SECOND milestone with the same title, and two 'v1.4' milestones is a state nothing downstream can read — the issues split across them and a release gate then passes on whichever is empty.

An existing milestone is reported and returned instead, with its id, so the next call can use it. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Idempotent, and it has to be: GitLab will make a SECOND milestone with the same title, and two 'v1.4's split the issues so the gate passes on whichever is empty.

## Example

```python
milestone_create('root/gitlab-mcp', title='v1.4', due='week')
```

## Required

`title`
