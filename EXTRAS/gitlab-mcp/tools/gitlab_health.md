# gitlab_health

[Back to index](../README.md)

## Signature

```python
gitlab_health(instance='')
```

Is the GitLab instance up, and if not, how is it down? Answers the question that an opaque tool failure mid-workflow does not: 'restarting, retry in ~60s' vs 'the host is down' vs 'your token is rejected'. Takes no arguments and touches no project. One unretried request, so it reports the state NOW rather than after the retry budget. Reports the version, the round-trip time, and the retry policy the other tools are running under.

The report leads with the HTTP status in brackets, so [200] means healthy. Pass `instance` to probe a GitLab other than the one this server is registered against.

## Convention

One unretried probe. Distinguishes restarting / host down / token rejected.

## Example

```python
gitlab_health(instance='ee')
```
