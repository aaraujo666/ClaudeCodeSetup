# mr_create

[Back to index](../README.md)

## Signature

```python
mr_create(project='', source, target='', title='', description='', issue=0, draft=False, squash=True, delete_source=True, repo='', instance='')
```

Open a merge request — the write half of the MR surface, and what `status::review` actually means. `source` is the branch to merge; `title` names it. `target` defaults to the project's DEFAULT BRANCH, read from the API — not a guess between main and master, and the same read release_check scopes CI on. An unreadable default branch is an ERROR naming the project: there is no valid merge request against ''.

`squash` and `delete_source` both default to True — squash-merge is the house default and a per-issue branch has no life after the merge. `draft=True` prefixes the title with 'Draft:'. `issue=N` puts 'Related to #N' in the description, which is what makes GitLab post the cross-reference on #N. `squash` is PERSISTED ON THE MR OBJECT, not a note for later: GitLab honours the MR's own flag at merge time, so the value written here is what the eventual merge does unless something changes it. mr_merge's `squash` argument is that something — it PUTs the MR to match before merging (#151) — but a merge from the UI's button takes what this call wrote.

A multi-commit branch whose commit bodies are worth keeping wants `squash=False` HERE, at the point the branch is still fresh in mind. REFUSES a closing keyword (Closes, Fixes, Resolves, IMPLEMENTING, and every inflection) followed by an issue reference in the title or description. Those fire on merge and auto-close the issue, performing step 4 of the close protocol and none of the other three — no cross-reference, no logged time, no terminal status:: label.

The commit-msg hook already blocks them in commits; an MR description is the second door into the same failure. IDEMPOTENT: a second identical call returns the EXISTING open MR for that source -> target and reports it as existing. GitLab answers a duplicate with a 409, and failing there would mean a retried handoff dies after the branch is already pushed. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

REFUSES a closing keyword — Closes, Fixes, Resolves and every inflection, IMPLEMENTING included — followed by an issue ref in the title or description. They fire on merge and perform step 4 of the close protocol alone: no cross-reference, no logged time, no terminal status::. Write 'Related to #N'. `target` defaults to the project's default branch READ from the API, and an unreadable one is an error, not a fall-back. squash and delete_source default to True — and `squash` PERSISTS ON THE MR OBJECT, governing the eventual merge (#151), so a branch whose commit bodies are worth keeping wants squash=False here.

## Example

```python
mr_create('root/gitlab-mcp', source='issue-116-mr-create', title='mr_create — open the MR a handoff hands off', issue=116)
```

## Required

`source`
