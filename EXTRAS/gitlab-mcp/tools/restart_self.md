# restart_self

[Back to index](../README.md)

## Signature

```python
restart_self()
```

Terminate this gitlab-mcp SERVER PROCESS — not the GitLab instance at your GitLab host, which this never touches — so the client respawns it on the next tool call, picking up edits to the server's own source. Call ONLY when the user says they changed gitlab-mcp's code; it is not a remedy for a tool that is failing. A NEWLY ADDED tool still needs a new session — the tool list the client holds was sent at startup and a restart does not resend it.

## Convention

Kills THIS server process, never the GitLab instance. A newly ADDED tool still needs a new session.
