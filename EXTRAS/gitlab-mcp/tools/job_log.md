# job_log

[Back to index](../README.md)

## Signature

```python
job_log(project='', job_id=0, pipeline_id=0, lines=200, full=False, errors_only=False, clean=True, format='text', repo='', instance='')
```

Read a CI job's TRACE — the log that says WHY it failed. `pipeline_show` gets as far as the job, its status and its runner and stops there; this is the line that actually names the cause. Name the job with `job_id`, OR pass `pipeline_id` and let it pick: given a pipeline it reads the FAILED job and says which one it read (a job merely `allow_failure` is chosen only when nothing else failed).

A pipeline with no failed job is refused with its jobs and their ids listed, rather than a successful job's log nobody asked for. Output is CLEANED by default: ANSI colour codes, `section_start:`/`section_end:` markers and progress-bar redraws are stripped — a fifth of the bytes on a measured real trace, and far more of one carrying a progress bar. `clean=False` returns it byte for byte.

Clipped to the LAST `lines` (default 200) — the tail is the useful part, since the head of every job is an image pull and a dependency install — and to 20 000 characters; `full=True` lifts both. `errors_only=True` returns just the lines around each failure marker plus the tail, with the gaps between them named. A job that has not run yet reports that, with its status — never an empty log.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The trace itself — WHY a job failed, which pipeline_show stops one line short of. Given a pipeline_id it picks the FAILED job and says which. ANSI and section markers are stripped, and the clipping keeps the TAIL: the head of every job is an image pull and an install.

## Example

```python
job_log('root/gitlab-mcp', pipeline_id=28, errors_only=True)
```
