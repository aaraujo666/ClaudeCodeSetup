# changelog_generate

[Back to index](../README.md)

## Signature

```python
changelog_generate(project='', milestone='', closed_after='', closed_before='', version='', title='', date='', full=False, format='text', repo='', instance='')
```

Generate a changelog from the tracker: the closed issues in a milestone and/or a close-date window, grouped by `type::` into Added / Changed / Fixed, one bullet each from the issue title with its `(#N)` reference. IT RETURNS THE TEXT AND WRITES NO FILE. The loop closes through the caller: generate -> edit the prose -> write changelogs/Changelog.vX.Y.md -> release_create(notes_path=...).

A generated changelog is a FIRST DRAFT — the value is that nothing gets forgotten, not that nobody writes prose — and a tool that wrote the file itself would invite an unread draft being tagged and published. SCOPE: `milestone` (its TITLE) and/or `closed_after`/`closed_before`; at least one is required, and both together intersect. The window takes 'today', 'week', '7d' or an ISO date, resolved as half-open LOCAL boundaries — issue_list's vocabulary exactly.

A milestone-only tool could not be run against most projects here: root/gitlab-mcp has no milestones at all. EXCLUDED: issues closed status::wontfix or status::moved (the work did not happen) and any issue carrying the `tracking` label (its children carry the work). `## Removed` and `## Notes` are NEVER generated — no type:: maps to them, and both are hand-added afterwards. An issue with no type:: label lands in Changed rather than being dropped.

`version` defaults to the milestone title, or to a placeholder on a window-only call; `title` defaults to the GitLab project NAME (the files read 'Acme Widgets' where the project is 'acme-widgets', so override it); `date` defaults to today. format=text returns the changelog itself and nothing else, so it can be written straight to a file; toon/json carry the rows, the counts and what was excluded.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Returns the TEXT and writes NO file — the loop closes through the caller (generate -> edit the prose -> write changelogs/Changelog.vX.Y.md -> release_create). A first DRAFT: the value is that nothing gets forgotten, not that nobody writes prose. Scope is a milestone and/or a close window; neither is refused. `## Removed` and `## Notes` are never generated, and wontfix/moved/tracking issues are excluded.

## Example

```python
changelog_generate('root/acme-widgets', milestone='v2.1', title='Acme Widgets')
```
