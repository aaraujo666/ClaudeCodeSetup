# issue_handoff

[Back to index](../README.md)

## Signature

```python
issue_handoff(project, iid, branch='', repo='', commit='', mr='', spend='', summary='', verified='', not_verified='', deferred='', force=False, allow_new=False, instance='')
```

End a round of work: post ONE structured '## Handoff' comment and move the issue to status::review. It carries what issue_close will need — repo, branch, commit, a PROPOSED spend, a summary, and what was verified / not verified / deferred — because the close is a human instruction that lands days later, in a session with no memory of the work. issue_close then sources spend, summary, commit and repo from it, which is what makes `issue_close(project, iid)` legal from a cold session.

SPEND IS PROPOSED, NEVER LOGGED HERE — issue_spend is additive and GitLab exposes no timelog list, so a double log could not be detected afterwards; issue_close stays the only thing that writes time. `repo` is REQUIRED in the comment and resolved from the project's local checkout when you do not pass it, because without it the close cannot sync the wiki; a project with no checkout is refused rather than guessed at.

`mr` is the merge request the work is proposed in — '42' or '!42'. status::review MEANS AN MR IS OPEN, not that a branch exists, so a handoff naming a `branch` and no `mr` is WARNED about (never refused: a rework round hands off onto an MR that is already open, and the field carries forward). issue_close reads it back and cross-references that MR, which is step 1 of the close protocol finally citing the thing that carried the work.

ONE comment per issue: a re-run UPDATES it in place rather than posting a second, and a field you leave out keeps the value already recorded — so a second call adding `commit=` need not repeat the rest. An identical re-run reports 'no change' and writes nothing. verified / not_verified / deferred take one item per line. force=True skips the transition check for an issue that is not in-progress; a CLOSED issue is refused.

## Convention

The bookend to issue_ready: what the CLOSER needs, written down before the working session ends, because the close lands days later with no memory of the work. SPEND IS PROPOSED, NEVER LOGGED — issue_close stays the only thing that writes time, since a double log cannot be detected. ONE comment, updated in place; an omitted field keeps the value already recorded, and an identical re-run writes nothing.

`repo` is required in the comment and resolved from the project's checkout when unpassed. `mr` records the merge request the work is proposed in — status::review MEANS an MR is open, so a branch with no mr is warned about, and issue_close cross-references the one recorded.

## Example

```python
issue_handoff('root/gitlab-mcp', 42, branch='issue/42-thing', commit='9e26896', mr='42', spend='2h30m', summary='what was done', verified='pytest: 1352 passed', not_verified='the live round trip')
```

## Required

`project`, `iid`
