# commit_show

[Back to index](../README.md)

## Signature

```python
commit_show(project='', sha, files=False, full=False, format='text', repo='', instance='')
```

Show ONE commit in full: its full SHA, author, date, message, and line stats. files=True adds the paths it touched (one extra request). `sha` may be short or full, or a branch/tag name. This is how a SHA gets VERIFIED before it is quoted: issue_close(commit=…) posts a note GitLab turns into a link, and a SHA copied from a checkout that has not been pushed names a commit the remote has never seen — the note is created either way and the link is simply dead.

The full SHA in this report is one the remote has. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

How a SHA gets VERIFIED before issue_close(commit=…) quotes it: a SHA from an unpushed checkout names a commit the remote hasn't got, and the note is created with a dead link either way.

## Example

```python
commit_show('root/gitlab-mcp', sha='9e26896', files=True)
```

## Required

`sha`
