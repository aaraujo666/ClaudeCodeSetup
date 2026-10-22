# issue_move

[Back to index](../README.md)

## Signature

```python
issue_move(project, iid, to_project, allow_new=False, instance='')
```

Move an issue to another project, preserving its discussion and its logged time — over GitLab's own `POST /issues/:iid/move`. Use this whenever work turns out to have been filed in the wrong project; close-and-refile loses the history and the time. Reports the NEW iid, which changes and cannot be guessed. THE SOURCE IS LEFT AS A CLOSED STUB, and the report says so. GitLab's web UI redirects the old URL to the moved issue; the API does NOT — reading the old ref returns the stub, a closed copy carrying the original title, description and discussion.

The stub keeps its labels, so the move is what moves it: the source is stamped status::moved as part of the move, which is terminal and TRUE of it — the issue left this project, and the work did not happen here. Without that it would be a closed issue carrying a live status::, the exact artifact this tool exists to stop close-and-refile producing. That write comes after the move and can never fail it: a source project seeded before status::moved existed is reported, naming labels_ensure, with the move already done.

LABELS ARE THE PART GITLAB DROPS. Label ids are per-project, so the move maps them by NAME and silently applies only the ones the destination already defines. So the destination is checked FIRST — before the move, the last moment a refusal costs nothing — and a project the scheme was never rolled out to is REFUSED, naming labels_ensure, rather than being handed an unlabelled issue that no board or report will ever show.

The issue's type:: / status:: / priority:: labels are then re-applied against what actually landed. allow_new=True moves anyway and lets GitLab create the labels as the issue arrives. Labels OUTSIDE the scheme are never re-created in a project that has never heard of them; a dropped one is reported by name. Converges: an issue GitLab has already moved into `to_project` is not moved twice — the destination copy is found through the source's moved-to pointer, the labels are re-applied there (a no-op the second time), and the report says so.

An issue already moved SOMEWHERE ELSE is refused, since there is nothing left in this project to move.

## Convention

The alternative to close-and-refile, which loses the discussion and the logged time. GitLab's own move keeps both — but it maps labels across by NAME and silently drops the ones the destination does not define. So a destination without the scheme is REFUSED before the move rather than handed an unlabelled issue, and the scoped labels are re-applied after. The iid CHANGES; the report names the new one.

The SOURCE is left as a closed stub — the web UI redirects the old URL, the API returns the stub — and the move stamps it status::moved, which is terminal and true of it: the issue left this project, and the work did not happen here.

## Example

```python
issue_move('root/gitlab-mcp', 42, to_project='root/acme-api')
```

## Required

`project`, `iid`, `to_project`
