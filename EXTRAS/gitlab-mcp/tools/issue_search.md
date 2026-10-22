# issue_search

[Back to index](../README.md)

## Signature

```python
issue_search(project='', text, state='all', comments=True, limit=20, format='text', repo='', instance='')
```

Full-text search over issues — the 'has this already been filed?' read. `project` is a project ref, or '*' for EVERY project the token can see. `text` is matched against issue titles and descriptions, and (comments=True, the default) against comment bodies too. state is opened|closed|all (default all — a closed duplicate is exactly what you are looking for). Each hit shows WHERE it matched (title, text, or comment) with an excerpt, plus any attachment filenames the matched text references.

ATTACHMENTS: an upload's FILENAME is searchable, because it sits in the issue text as a /uploads/ link — searching 'diagram.png' finds the issue carrying it. An attachment's CONTENTS are indexed by nothing on this instance (CE basic search; Advanced Search would not cover uploads either), so text inside a PDF or image is NOT findable. COST: comment search is project-scoped only in CE (the global endpoint rejects it), so comments=True with project='*' issues one request per project.

Pass comments=False for a single fast instance-wide pass over titles and descriptions. `format` is text (default), toon or json — the machine formats carry the hits as rows, each with where it matched and the excerpt, plus the same tally. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Attachment FILENAMES are searchable; attachment contents are indexed by nothing. comments=True fans out one request per project when project='*'.

## Example

```python
issue_search('*', 'restic', comments=False)
```

## Required

`text`
