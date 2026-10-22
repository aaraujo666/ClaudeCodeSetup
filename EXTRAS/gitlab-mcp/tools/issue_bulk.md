# issue_bulk

[Back to index](../README.md)

## Signature

```python
issue_bulk(project, iids, add_labels='', remove_labels='', status='', allow_new=False, force=False, instance='')
```

Apply the SAME label change to a list of issues in one call — the release-prep path, where moving a batch one issue_status call at a time is how one of them gets missed. `iids` is comma-separated numbers and ranges: '12,14,16', '12-16', or a mix. Pass any of `status` (bare or qualified — the usual move), `add_labels`, `remove_labels` (comma-separated). Every scoped label applied displaces the labels sharing its prefix, exactly as issue_status does, so no issue can end up carrying two statuses; unscoped labels are purely additive.

The whole label set is validated ONCE before anything is written (allow_new=True bypasses), so a typo cannot leave the first six issues moved and the rest not. Issues are INDEPENDENT: one failing does not abort the others — unlike issue_close, whose steps are coupled. Idempotent per issue: one already carrying the labels reports 'no change' and is not written. An iid that does not exist is named as such rather than returned as a 404, and a batch that moved CLOSED issues to a non-terminal status says so at the end.

A row left carrying no type::/status:: label — a remove_labels that took the last one — is WARNED on its own line and written anyway, exactly as issue_update does, and the warned rows are counted in the summary. The legal status:: transitions are checked PER ROW, exactly as issue_status checks them: a row whose current status cannot legally reach the target is REFUSED and not written, the rest of the batch runs, and `refused=N` appears in the summary. blocked -> backlog is gated per row the same way (#192): a row whose questions are not all answered is refused with the code issue_status would give. force=True moves them anyway.

Returns one line per issue plus a changed/unchanged/refused/failed summary.

## Convention

The batch form of issue_status. Labels are validated ONCE before the first write, and the issues are INDEPENDENT — one failing does not abort the rest (the close protocol's steps are coupled; a batch's rows are not). A removal that takes a row's last type::/status:: warns ON THAT ROW and writes, and the summary counts the warned rows.

## Example

```python
issue_bulk('root/gitlab-mcp', '12,14-16', status='done')
```

## Required

`project`, `iids`
