# ci_variable_list

[Back to index](../README.md)

## Signature

```python
ci_variable_list(project='', limit=40, full=False, format='text', group='', scope='', repo='', instance='')
```

List a project's CI/CD variables: `key type scope masked protected raw`. `group=` (an id or path) lists a group's instead, and `scope='instance'` the instance-level ones (an ADMIN token); naming more than one target is refused. **The VALUES are never returned** — this read answers which variables exist and how they are configured, which is the question that can be answered safely; a value belongs in the job that consumes it.

Tallied by masked and protected, each with its denominator, so an unmasked secret is visible as a count rather than something to spot by eye. `limit` caps the rows (default 40); full=True lifts the cap. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Keys and flags only — values are never returned, in any format, at any level. Tallies the UNMASKED ones with their denominator, so an unmasked secret is a count rather than something to spot by eye. `group=` lists a group's, `scope='instance'` the instance's (ADMIN token).
