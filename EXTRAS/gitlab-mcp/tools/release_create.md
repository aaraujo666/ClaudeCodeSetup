# release_create

[Back to index](../README.md)

## Signature

```python
release_create(project='', tag, ref='', notes_path='', notes='', name='', milestone='', repo='', instance='')
```

Cut a release: create the tag (if it does not exist) and publish release notes against it. `tag` is the tag name ('v1.4'); `ref` the branch or SHA to tag (default HEAD of the default branch). `milestone` optionally links the release to a milestone TITLE. NOTES COME FROM A FILE: `notes_path` points at the repo's changelog for this release (relative paths resolve against `repo`), because notes typed into a call exist only in GitLab and the next release's changelog then disagrees with the last one's release page.

`notes` is accepted for the case with no file, and one of the two is required. IDEMPOTENT: an existing tag pointing where you asked is reported as no change rather than re-created, and an existing RELEASE on that tag is UPDATED with the current notes rather than refused — cutting a release twice after a failed first attempt is ordinary, and must not need cleanup. A tag that exists but points somewhere ELSE is refused: moving a release tag silently is how a published artifact stops matching its source.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Notes come from a FILE (`notes_path`), so the release page cannot drift from the changelog the repo maintains. Re-cutting UPDATES an existing release, but a tag pointing somewhere else is refused rather than moved.

## Example

```python
release_create('root/gitlab-mcp', tag='v1.4', notes_path='changelogs/v1.4.md', repo='C:/path/to/checkout')
```

## Required

`tag`
