# close_audit

[Back to index](../README.md)

## Signature

```python
close_audit(project='', since='', full=False, format='text', repo='', instance='')
```

Find CLOSES THAT BYPASSED THE PROTOCOL, across every project at once (#156). `issue_close` enforces the protocol on callers that go through it, and a required argument cannot be required of a BROWSER — ten issues were closed from GitLab's bulk-edit panel still carrying status::backlog, with no logged time and no close note. The UI door will not close, so detection is the only available control and this is it.

Two checks, and they are NOT equally strong — the report says which is which. (1) CLOSED issues still carrying a NON-TERMINAL status:: label: the clean signal, and exactly what a UI close or a bare state flip leaves behind. (2) CLOSED issues with NO LOGGED TIME, minus the legitimate cases (status::wontfix, status::moved, tracking, github_sync mirror rows) — a weaker signal, because most of that population is correct, so it is REPORTED and never counted as a failure on its own.

`project` defaults to '*', every project the token can see; name one to scope it. `since=` ('month', '7d', an ISO date) windows on the CLOSE date. Repairs are PROPOSED, never performed: the fix for a batch is issue_bulk(project, iids, status='wontfix'|'done'), and which of the two is right is a judgement per issue. Reads GitLab — unlike gitlab_audit, which reads this machine's own trail and would not have seen any of this.

## Convention

Finds closes that BYPASSED the protocol, instance-wide (#156) — a required argument cannot be required of a browser, and ten issues were closed from GitLab's bulk-edit panel still carrying status::backlog. Two checks of unequal strength, and it says which: a closed issue on a NON-TERMINAL status:: is the clean signal; zero logged time is REPORTED, not blocked on, because most of that population is correct (wontfix, moved and mirror rows are excluded outright).

Repairs are PROPOSED, never applied — done vs wontfix is a judgement per issue. Reads GitLab, unlike gitlab_audit, which reads this machine's trail and never saw any of it.

## Example

```python
close_audit()   # every project; add since='month' to window it
```
