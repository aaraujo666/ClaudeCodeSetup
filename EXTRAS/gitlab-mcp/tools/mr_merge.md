# mr_merge

[Back to index](../README.md)

## Signature

```python
mr_merge(project='', iid, squash=True, delete_source=True, message='', force=False, wait=30, repo='', instance='')
```

Merge a reviewed branch — the GATE, and the last step of the review half of the workflow. Squash-merges the MR and deletes its source branch, both on by default, matching mr_create. REFUSES, naming the condition AND what clears it, while the MR is a DRAFT, has an UNRESOLVED discussion thread, has CONFLICTS (or any detailed_merge_status other than `mergeable`), has a pipeline on its head SHA that is running, failed or cancelled, or HAS NOT BEEN APPROVED.

Every blocking condition is named in ONE refusal, not one round trip each. Nothing is written when it refuses. `force=True` covers the PIPELINE and APPROVAL refusals and nothing else. Conflicts, a draft and unresolved discussions are states GitLab itself rejects, and pretending otherwise turns a refusal that says what to do into an opaque HTTP 405. The APPROVAL gate is this tool's own, and GitLab will not back it up: on CE an unapproved MR reports `mergeable` and merges without a murmur.

It is here because an agent hands off at status::review and never approves, so a human approval is the one machine-readable 'someone actually looked' signal that is distinct from 'merged' — and forcing past it puts that fact on the report rather than leaving it silent. mr_approve is what clears it. An approval that could not be READ is a note, never a blocker. The CI gate is the one that earns its keep: unless a project turns on 'Pipelines must succeed', GitLab reports an MR with a RED pipeline as `mergeable` and merges it without a murmur.

A pipeline that could not be READ (403, or a project with no CI at all) is a note, never a blocker — the same call release_check makes, for the same reason. IDEMPOTENT: an ALREADY-MERGED MR reports done and writes nothing, so a close protocol that died at a later step can walk past this one — exactly how issue_close resumes an already-closed issue. A CLOSED-unmerged MR is an ERROR: different state, and doing nothing quietly would hide it.

`message` overrides the squash commit message (the merge commit message when squash=False); omitted, GitLab composes it. The merge is submitted WITH the head SHA the gates were checked against, so a push that lands between the check and the merge is rejected rather than merged unreviewed. `squash` OVERRIDES WHAT mr_create PERSISTED (#151). GitLab merges on the MR's own stored squash flag, not on the parameter to the merge call, so this tool PUTs the MR to match first — the argument at merge time is the more recent intent.

The report then states what GitLab ACTUALLY did, read back from `squash_commit_sha` in the merge response, never the requested value; `?` means the response did not say, and is not `no`. A project whose `squash_option` is `always` or `never` CONTRADICTS the argument is REFUSED, naming the setting: GitLab enforces it over both the argument and the MR's flag, and an unasked-for squash is a history rewrite — commit bodies destroyed and authorship rewritten to the merging token's user.

WAITS OUT A TRANSIENT STATUS (#183). Right after a push GitLab reports `checking` (or `approvals_syncing`, `unchecked`, `preparing`) for a few seconds; the MR is re-read until that clears, for up to `wait` seconds (default 30, 0 disables), BEFORE any gate runs, so every gate sees the settled payload and the merge is submitted with the settled head SHA. If the wait runs out the refusal names the last status and the wait, and no merge is attempted.

It does NOT wait for CI: a running pipeline stays a forceable blocker. AFTER THE MERGE the MR is read back to confirm it reached `merged`, and the report gives the merge/squash commit sha. A merge PUT that timed out or answered 422 but whose MR shows `merged` is reported as MERGED, not as a failure. An MR left `locked` is reported as LOCKED, with the recovery (a local `--no-ff` merge and push); nothing is attempted automatically.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The GATE. Refuses on a draft, a conflict, an unresolved discussion, any detailed_merge_status but `mergeable`, a pipeline on the head SHA that is running or red, or NO APPROVAL — ALL the blocking conditions in ONE refusal, each naming what clears it, and nothing written. force=True covers the CI and APPROVAL conditions ALONE; the others are refused by GitLab itself, and forcing them turns a clear refusal into a 405.

Both forceable gates are this tool's own: without 'Pipelines must succeed' GitLab calls a red MR `mergeable`, and on CE it calls an unapproved one `mergeable` too. An ALREADY-MERGED MR reports done and writes nothing; a CLOSED-unmerged one errors. `squash` OVERRIDES what mr_create persisted (#151): GitLab merges on the MR's OWN stored flag, so this PUTs the MR to match before merging, and the report states what GitLab ACTUALLY did, read back from squash_commit_sha — `?` when the response did not say, and never `no`.

A project whose squash_option is `always` or `never` contradicts the argument is REFUSED, naming the setting.

## Example

```python
mr_merge('root/gitlab-mcp', iid=9)
```

## Required

`iid`
