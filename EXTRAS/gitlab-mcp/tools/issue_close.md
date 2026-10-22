# issue_close

[Back to index](../README.md)

## Signature

```python
issue_close(project, iid, spend='', summary='', status='done', commit='', mr='', body='', relation='Closed by', allow_new=False, repo='', summary_overflow='refuse', instance='')
```

Close an issue THE WHOLE WAY: optional commit/MR cross-reference note -> log spent time -> move status:: to a terminal value -> close -> sync the wiki. Use this instead of flipping state by hand; the steps that get forgotten (a closed issue still labelled status::in-progress, work with no time on it, docs correct in the repo and stale on the wiki) are invisible afterwards. `spend` is REQUIRED: a GitLab duration ('45m', '2h30m') estimating the SKILLED-DEV EFFORT the work represents — never the wall-clock length of the session — or '0' to close without logging.

`summary` (<=255 chars) records what was done — a longer one is refused before anything is written, unless `summary_overflow='comment'`, which logs a cut summary and posts the WHOLE text as a comment on the issue rather than making you re-word it. With `spend='0'` there is no timelog, so neither the cap nor `summary_overflow` applies: the summary is posted as a comment WHOLE, at any length — a dropped issue keeps the reason it was dropped.

`status` is the terminal status:: label (default 'done'; pass 'wontfix' when the issue is being dropped, or '' to leave labels alone). commit/mr/body/relation post the cross-reference note first — and `mr` ('42' or '!42'), like `commit`, `spend`, `summary` and `repo`, is taken from the issue's HANDOFF when you do not pass one, so step 1 cites the merge request that carried the work instead of whatever the closing session happened to know.

`repo` (path to the repo checkout) mirrors its declared docs dir to the wiki as the FIFTH step, and it is REQUIRED the way `spend` is: a close is not finished until the wiki is synced, so a close with nowhere to sync from is REFUSED before anything is written (#131). It writes only what actually differs, so a redundant one reports 'nothing to sync' and costs a single read; a wiki failure NEVER un-closes the issue.

Omitted, it is resolved from the issue's HANDOFF and then from the local-checkout registry (GITLAB_REPO_ROOTS), and the refusal only arrives when none of the three answered — so a cold close from a session with no checkout still works, provided the working session wrote a handoff. Steps 1-4 run in order and STOP at the first failure, leaving the issue open and reporting what did happen — so a failed status move can never produce a closed, mislabelled issue.

An ALREADY-CLOSED issue (a commit message saying `closes #N` auto-closes on push, doing nothing else) is RESUMED, not refused: the tool runs only the steps actually still missing — it never logs time onto an issue that already has some, and never re-closes. Call it exactly as you would have; the report says what it finished and what was already done. Nothing missing = nothing written.

## Convention

Steps 1-4 run in order and STOP at the first failure, so a failed status move can never leave a closed, mislabelled issue. Step 5, the wiki sync, runs last and CANNOT abort the close — but having nowhere to sync FROM refuses the whole call up front, the way a missing `spend` does. An ALREADY-CLOSED issue is resumed, not refused: only the missing steps run, and time is never logged twice.

An over-long `summary` is refused before any write — or, with summary_overflow='comment', logged cut with the whole text posted as a comment.

## Example

```python
issue_close('root/gitlab-mcp', 42, spend='1h30m', summary='what was done', commit='9e26896', repo='C:/path/to/checkout')
```

## Required

`project`, `iid`
