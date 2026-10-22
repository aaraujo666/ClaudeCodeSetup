# pipeline_wait

[Back to index](../README.md)

## Signature

```python
pipeline_wait(project='', pipeline_id=0, ref='', sha='', mr=0, timeout=120, interval=5, full=False, format='text', repo='', instance='')
```

BLOCK until a pipeline finishes, then report it — replaces a hand-written sleep/curl poll loop. Name the pipeline with exactly ONE of `pipeline_id`, `sha`, `ref` or `mr` (the merge request iid; its newest pipeline). For `sha`, `ref` and `mr` it also waits for the pipeline to APPEAR, so it can be called straight after a push. Finished means success, failed, canceled, skipped or manual (a pipeline blocked on a person cannot be waited out, so it stops there).

The result is the final status and the job table `pipeline_show` renders; on failure it names the failed job ids, so `job_log(job_id=...)` follows directly (a job allowed to fail is listed apart). `timeout` is in seconds: DEFAULT 120, capped at 600, kept under the MCP client's own call timeout. Running out is not an error: the result starts `# TIMED OUT`, carries the pipeline id and its current state, and says to call again to keep waiting.

`interval` (default 5s) is the poll gap. A push for a merge request runs CI on `refs/merge-requests/<iid>/head`, not on the branch name, so `ref=<branch>` can find nothing for an MR push — use `mr=` or `sha=` for that. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Blocks until the pipeline finishes (default 120s, cap 600): a timeout is a `# TIMED OUT` result to call again from, not an error. sha/ref/mr wait for the pipeline to APPEAR. An MR push runs on refs/merge-requests/<iid>/head, so use mr= or sha=, not ref=<branch>.

## Example

```python
pipeline_wait('root/gitlab-mcp', mr=12, timeout=120)
```
