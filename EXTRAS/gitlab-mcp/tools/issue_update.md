# issue_update

[Back to index](../README.md)

## Signature

```python
issue_update(project, iid, title=None, description=None, labels=None, add_labels='', remove_labels='', allow_new=False, instance='')
```

Update an issue's fields/labels. Pass any of title/description/labels (labels REPLACES the whole set) or add_labels/remove_labels (comma-separated, additive/subtractive). OMITTING a field leaves it alone; passing an EMPTY STRING clears it — description='' blanks the description, labels='' strips every label. (title='' is refused: GitLab requires a title.) For scoped labels prefer issue_status / issue_scoped_set — they handle the CE add-and-remove pairing.

Labels being ADDED are validated against the scheme and the project (allow_new=True bypasses); removals are not, so this is also how you strip a bad label. The one-type-one-status rule holds here as it does on create, and allow_new does not bypass it: a `labels` replacement naming no type:: is REFUSED (one naming no status:: carries the issue's current status forward rather than resetting it to backlog), an add_labels that would put a second value in a scope is REFUSED, and a remove_labels that takes the last type::/status:: WARNS and proceeds — removal is how a bad label gets cleaned up. labels='' stays the deliberate full strip and is exempt.

A `description` stating an UNMADE DECISION as prose — a decision-shaped heading ('## What has to be settled' included), or an acceptance criterion that is an ALTERNATIVE to another ('- [ ] Or, …', '… either X, or Y'), with no '## Open questions' block — is REFUSED here exactly as it is on issue_create, because a body can acquire one long after it was filed. Ask it with issue_ask, or head the section DECISION / AMENDMENT / DECIDED / RESOLVED (uppercase) if it is already settled.

A HAND-WRITTEN questions block — '## Open questions' with no readable '### Qn' heading under it — is refused the same way; write it with issue_ask instead. An update that CHANGES the title or description of an issue on a project that opted in (custom attribute typesafe_decision_check=on) is also read by TypeSafe's Jev for an unmade decision (`semantic_decision`, #190) — ADVISORY, reported after the write with its probability and cost; a label or unchanged-text edit sends nothing.

## Required

`project`, `iid`
