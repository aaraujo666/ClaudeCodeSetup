# tag_list

[Back to index](../README.md)

## Signature

```python
tag_list(project='', limit=30, full=False, format='text', repo='', instance='')
```

List a project's TAGS, newest first: name, the commit each points at, its date, whether the tag is annotated, whether it carries RELEASE NOTES, and whether it is protected. What versions this project has actually cut, which is the question release_create's caller asks first and could not ask here. An ANNOTATED tag is one created with a message — a release tag normally is, a tag pushed from a script often is not.

A tag with release notes is one GitLab shows on the Releases page; release_create is what writes them. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.
