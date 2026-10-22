# release_check

[Back to index](../README.md)

## Signature

```python
release_check(project='', milestone='', since='month', tracker=0, ref='', secrets=True, full=False, format='text', repo='', instance='')
```

Gate a release on the standing rules, as a tool rather than a habit. Checks SIX things and names every issue behind each, because a count is not actionable: 1. OPEN issues on the milestone. 2. TEST CASES not passed, read from the tracker issue's checkboxes (found by its own 'Release gate:' footer, or named with `tracker`) — a failed case and an unrun one are reported apart, since they call for opposite responses. 3.

CLOSED issues with NO logged time: spend='0' is legitimate for an epic or a duplicate, so this is a decision to make once at the gate rather than an error. 4. Issues missing a type:: or status:: label — the same check project_status makes, sharing its implementation so the two cannot disagree about whether a release is clean. 5. CI ON THE RELEASE REF: the latest pipeline there must be `success`, reported as a row with its id, status, time and URL.

A pipeline still RUNNING blocks too, but is worded as a wait rather than a failure. 6. COMMITTED CREDENTIALS on that same ref — secret_scan over the working tree, whose findings block and whose matched values are never echoed. A scan that could NOT RUN blocks as well, which is the tracker's rule and not the CI one: a project with no pipeline has no CI, while files that could not be read have not been checked, and 'not checked' must not authorise a release as 'clean'. secrets=False skips it and says so in a note.

`milestone` is the milestone TITLE ('v1.4') and scopes checks 1 and 3 to it. WITHOUT one, check 3 covers issues closed since `since` ('month' by default, or 'week', '7d', an ISO date), because every issue ever closed is a history lesson and not a gate. `ref` scopes check 5 (default: the project's DEFAULT BRANCH — a red feature branch is not a reason to hold a release cut from master).

A project with NO pipelines, or a CI read that fails, is a `# note:` and NOT a blocker — most projects here have never run CI, and a check every one of them fails forever is a check people skip. That is the opposite of the tracker rule above, on purpose: a missing tracker is missing test evidence, a missing pipeline is not a red one. Ends on PASS or on FAIL with the blocker count.

PASS is stated explicitly — an empty report reads exactly like one that failed to run, and this read is consulted to authorise something. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The gate, as a tool. Names the issues behind every finding — a count is not actionable. spend='0' closes are LISTED, not flagged as errors: zero is a decision, and the gate is where it gets made. Shares project_status's label check, so the two cannot disagree about whether a release is clean. Check 5 is CI on the release `ref` (default: the default branch) — a project with NO pipelines still PASSES, since a check every project fails forever is a check people skip.

## Example

```python
release_check('root/gitlab-mcp', milestone='v1.4')
```
