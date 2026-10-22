# mr_approve

[Back to index](../README.md)

## Signature

```python
mr_approve(project='', iid, withdraw=False, repo='', instance='')
```

Approve a merge request — or withdraw an approval with `withdraw=True`. The reviewer's signal at the review end of the workflow, and what clears mr_merge's APPROVAL gate. IT IS ADVISORY, AND DELIBERATELY SO. This is GitLab 17.3 CE: the approval RULES layer is Premium and absent (approval_state and approval_rules answer 404, approvals_before_merge is not a settable project attribute), so an unapproved MR still reports `detailed_merge_status: mergeable` and GitLab will merge it without a murmur.

The enforcement is gitlab-mcp's own — mr_merge refuses on it — exactly as issue_close enforces its four steps that GitLab knows nothing about. In the dispatch loop an agent hands off at status::review and never approves, so a human approval is the one machine-readable 'someone actually looked' signal distinct from 'merged'. IDEMPOTENT, and that is most of the tool: GitLab answers a SECOND approve with 401 and a second unapprove with 404, neither of which a caller can act on.

Both are reported as 'no change' instead, the way mr_merge reports an already-merged MR. REFUSES a merge request that is not open, naming its state — approving a merged one is a 401 from GitLab, which says nothing. Self-approval by the MR's own author IS allowed here: 'prevent author approval' belongs to the paid rules layer this instance does not have. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

ADVISORY on this CE instance and built that way on purpose: the approval RULES layer is Premium and absent (approval_state and approval_rules 404), so GitLab records the approval and then reports an unapproved MR as `mergeable` anyway. mr_merge is what enforces it. Converges rather than passing GitLab's answers through: a second approve is 401 and a second unapprove 404, and both are reported as 'no change'.

Self-approval IS allowed — 'prevent author approval' is part of the same paid layer.

## Example

```python
mr_approve('root/gitlab-mcp', iid=9)
```

## Required

`iid`
