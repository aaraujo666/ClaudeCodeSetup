# repo_list

[Back to index](../README.md)

## Signature

```python
repo_list(refresh=False, full=False, format='text')
```

List the CHECKOUT REGISTRY: every project ref that a local checkout declares, the path it maps to, and the roots that were scanned to find them. This is the read behind `no local checkout declares root/X` — that message names where it looked, and this names what it found. One row per project ref. A ref that TWO checkouts declare is reported as AMBIGUOUS with every path named, never deduped to the first: that is the state the registry refuses to resolve, so it must be visible rather than look healthy.

Configured roots that do not exist on this machine are listed too — a checkout outside the roots and a checkout with no .gitlab-tools.json are different faults with the same symptom. Touches no GitLab: the map is a fact about this machine, so there is no `instance` and no project scope. refresh=True rescans instead of reading the held map — the answer after a fresh clone. Set GITLAB_REPO_ROOTS (os.pathsep-separated) when the checkouts live somewhere else.

## Convention

The registry's own rule, which this read exists to make visible: NOTHING IS GUESSED. `<root>/<name>` fits most projects and `acme/*` does not, so an unmapped ref is reported rather than inferred — a wrong path there is `issue_close` publishing one repo's docs to another repo's wiki. Same rule on the ambiguous case, which is why it is a row here and not a dedup.
