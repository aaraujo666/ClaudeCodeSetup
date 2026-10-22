# repo_file

[Back to index](../README.md)

## Signature

```python
repo_file(project='', path, ref='HEAD', full=False, format='text', repo='', instance='')
```

Read ONE file from a project's repository at a ref, without cloning — the 'what is actually on the remote' read. `path` is repo-relative ('docs/TOOLS.md'); `ref` is a branch, tag or SHA, default HEAD (GitLab resolves it to the default branch, so you need not know whether that is main or master). Returns the path, the ref it resolved to, the blob SHA and size, then the contents.

Long files are clipped with a size hint — full=True for the rest. A BINARY file is named and its size reported rather than decoded into mojibake. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Reads GitLab's copy, not the checkout's — the difference that matters when the checkout is behind. Binary files are named, not decoded.

## Example

```python
repo_file('root/gitlab-mcp', path='docs/TOOLS.md', ref='v1.4')
```

## Required

`path`
