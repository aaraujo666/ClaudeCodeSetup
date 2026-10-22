# 08. Memory: a structured knowledge base, not a junk drawer

Claude Code can keep notes between sessions. Left alone, that becomes one large file
that grows until it is noise, with half of it out of date and no way to tell which half.

My memory is a folder of small files, one fact each, validated by a hook, indexed
automatically, and version-controlled. It follows the Open Knowledge Format (OKF) v0.2,
a small spec for knowledge bundles: markdown concept files with typed frontmatter, an
index, and a change log. The details I added on top are what make it useful.

A sample bundle is in [examples/memory/](../examples/memory/).

## One fact per file

A file that holds one fact can be superseded, marked stale, verified, linked and
deduplicated individually. A file that holds twelve cannot. Each file has a type:

| `type` | What it holds |
|---|---|
| `User` | Who I am, my background, how I like to be spoken to |
| `Feedback` | How I want the work done; corrections that should stick |
| `Project` | State, decisions and constraints for one project |
| `Reference` | A fact about a system, tool or place: where it is, how it behaves |

## A full example (fictional)

```markdown
---
type: Reference
title: Container image build cache
tags: [infrastructure, trap]
status: stable
stale_after: 2027-01-15T00:00:00Z
sources:
  - "[^1]: https://docs.example.com/build/cache#pruning"
generated: { by: claude-code/unknown, at: 2026-10-14T09:12:40Z }
verified: { by: human:owner, at: 2026-10-14T09:30:00Z }
name: reference-container-build-cache
description: "TRAP: `build prune --all` exits 0 but keeps cache for pinned base images; verify with `build du`"
metadata:
  node_type: memory
  type: reference
---

`build prune --all` prints the freed-space line, exits 0, and **leaves the cache for
any pinned base image in place**. It looks like a full clean and is not one.

Hit on the acme-widgets CI runner: the disk filled again within a day because the
"clean" step never reclaimed the 14 GB layer cache. The job log said `pruned`.

**How to apply:**
- To reclaim everything: `build prune --all --force` followed by removing the pinned
  images by hand.
- ALWAYS verify with `build du`, never with the prune command's own output.[^1]

Related: [CI runner layout](/reference-ci-runner-layout.md)
```

Notes on that file:

- **Both `type` keys are intentional.** The harness reads `name`, `description` and
  `metadata.type`; OKF reads the capitalised `type`, `title`, `tags`, `status` and
  `generated`.
- **`description` is the retrieval hook.** It is what shows up in the index, so write it
  as the answer, not the topic. "TRAP: ... exits 0 but ..." beats "Notes about pruning".
- **`stale_after`** goes on anything that ages: versions, prices, addresses, who-owns-what,
  anything with the word "currently" in it.
- **`verified`** is added by hand, only when I actually confirmed it.
- **`sources`** with footnote ids for facts that came from a URL or a document, so the
  claim can name its source when repeated.
- **Links are `[name](/name.md)`**, never wiki-style `[[name]]`. A hook rewrites the latter.

## Supersede, do not delete

When a fact is replaced, set `status: deprecated` on the old one and link to what
replaced it. History stays. A deprecated entry is a record of what used to be true and
why it stopped, which is sometimes exactly what explains a surprising behaviour.

## `verified: by human` beats inferred

A fact I confirmed outranks one the model inferred from a transcript. In a conflict:
verified beats unverified, and a newer timestamp beats an older one within the same tier.
This gives the model a rule for resolving contradictions that does not involve guessing
which note it liked more.

## TRAP entries

Many entries are explicitly marked as traps: things that cost real time once. They have a
fixed shape, and the shape is the point:

1. **What the thing appears to do** (the plausible reading).
2. **What it actually does** (the surprise).
3. **How it was discovered**, briefly, with the cost.
4. **How to apply**: the safe alternative and the verification.

Examples of the pattern (all generic): a command that exits 0 but changes nothing; a
"running" status that does not mean healthy; a download URL that returns a sign-in page
with HTTP 200; a number that was triple-counted because a log was not deduplicated by
request id. These are the most valuable entries in the whole store, because they are
exactly the knowledge a fresh session cannot derive.

## The index and the markers

`MEMORY.md` is the only file loaded up front, so it is an index with one line per
concept, and the trust signals ride on it:

```markdown
## Homelab
- [Container image build cache](reference-container-build-cache.md) [verified] — TRAP: prune --all keeps pinned-image cache
- [Registry mirror address](reference-registry-mirror.md) [stale since 2026-10-01] — pull-through mirror for CI
- [Old runner layout](reference-ci-runner-layout-v1.md) [deprecated] — replaced by v2 layout
```

Format: `- [Title](file.md) [marker] [marker] — one-line hook`. The markers are derived from
frontmatter and rewritten on every run, so they are never hand-edited:

| Marker | Meaning for the reader |
|---|---|
| `[deprecated]` | History. Follow whatever superseded it |
| `[stale since DATE]` | Re-check against the live system before acting or repeating it |
| `[verified]` | A human confirmed it |
| `[draft]` | A lead, not a fact |

The instruction to the model, in `CLAUDE.md`, is to treat those markers as instructions.

## The hooks that keep it honest

- **PostToolUse on writes.** When a memory file is written or edited, a hook normalises
  the frontmatter, fills the missing OKF keys, rewrites wiki-style links, bumps the
  `generated` timestamp, appends to `log.md`, regenerates `index.md`, and refreshes the
  markers on `MEMORY.md`. If something cannot be repaired it prints an error that gets
  fixed before moving on.
- **SessionStart.** Reports every concept whose `stale_after` has passed or is within a
  week, with the instruction to re-verify and move the date forward. See
  [Hooks](03-hooks.md#sessionstart-report-staleness).
- **An audit command** checks a bundle for conformance and house rules and exits non-zero
  on errors, so it can run in CI.

## Version control

The whole memory store is a git repository. That gives history for free, makes a bad
write recoverable, lets the store sync between machines, and makes the periodic
"what did I learn this month" review a diff.

## What does not belong

- Anything derivable from the code or the tracker. Memory is for what a fresh session
  cannot recover.
- Secrets. Memory files get read, sometimes sent places, and committed. A credential
  screen runs before any memory content is sent to a third-party model for deduplication,
  after a bulk run once nearly shipped a LAN login. See [Jev](06-jev-decision-model.md).
- Work state. That belongs in the tracker.

Next: [09 MCP servers](09-mcp-servers.md)
