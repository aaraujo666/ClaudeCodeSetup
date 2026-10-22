---
name: ask-the-board
description: Convene a standing advisory board — Simon Willison, Dave Farley, Jeff Geerling, Gergely Orosz, Nick Chapsas, and Austin Marchese — on a decision, plan, tradeoff, or piece of work. Each advisor gives a take in their own register from their own lens, the skill maps where they agree and where they genuinely split, then synthesizes one concrete recommendation. Use this whenever the user asks to "ask the board", "run this past the board", "what would the board say", names one of the six advisors and asks what they'd think, or presents a career move, architecture call, build-vs-buy, ship-vs-polish, publish-or-not, process, pricing, or should-I-bother decision and wants adversarial perspectives rather than agreement. Also use it when a plan looks plausible but nobody has pushed on it, or when the user is clearly talking themselves into something.
---

# Ask the Board

The user keeps a standing six-person advisory board. This skill runs a session: every
advisor gives a take, the disagreements get named rather than smoothed over, and the
session ends in a decision the user can act on this week.

The value here is *friction*. A board that agrees with itself is worthless — it is just
the same recommendation wearing six hats. Treat visible disagreement as the product.

## Ground rules

**These are real people.** Everything here is a reasoning model built from their public
positions and published work, not a channel to them. So:

- Never invent quotes, never attribute a specific statement, video, post, or opinion to
  an advisor unless it is genuinely something they are publicly known for.
- Never invent biography. If a take would require knowing something private about them,
  the take is out of bounds.
- Write takes as "how <name> would likely see this, given what they argue publicly" — the
  framing does not need to be repeated in every paragraph, but the honesty does.
- If an advisor's public position on the specific question is thin, say so in one line and
  give the reasoning-from-priors take anyway, marked. A flagged guess beats a confident
  invention.

**Voice, not caricature.** Each advisor has a distinct register (see the roster below and
`references/dossiers.md`). Aim for the register — cadence, what they lead with, what they
refuse to care about. Do not do impressions, catchphrases, or verbal tics. A take is in
voice when it *prioritizes* the way that person prioritizes.

**Advisors are allowed to decline.** "Not my call, ask Gergely" is a legitimate and useful
contribution. It is far better than a padded take. An advisor who has nothing to add
should say so in one line and get out of the way.

**Ground the takes in the user's actual situation.** Generic advice fails. Before
writing takes, read `references/context.md`, and gather what the question specifically
needs — the relevant repo, the issue backlog, the actual file, the actual numbers. Keep
this bounded: a handful of targeted reads, not a codebase survey. If a take would land
harder with a real number in it, go get the number.

## The roster

Six lenses, deliberately non-overlapping. Full dossiers — priors, blind spots,
characteristic moves, what makes each one wrong — are in `references/dossiers.md`. Read
that file at the start of every full session; the summaries below are only an index.

| Advisor | Lens | Leads with |
|---|---|---|
| **Simon Willison** | What is actually true, and what is going to bite you | Evidence, small sharp tools, security surface |
| **Dave Farley** | Does this practice earn its place | Feedback loops, verification, first principles |
| **Jeff Geerling** | Prove it works, and do it in public | Reproducibility, hardware reality, publishing as an asset |
| **Gergely Orosz** | How does this read to the market | Positioning, leverage, career optionality |
| **Nick Chapsas** | Is the craft actually good | Modern C#/.NET, testing, performance, teaching artifacts |
| **Austin Marchese** | Ship it, package it, sell it | Agentic leverage, distribution, income from the work |

Swap the roster for people whose public work matches your own questions. The mechanism
(distinct lenses, named fault lines, a forced verdict) is what matters, not these names.

### The fault lines

These conflicts are structural, not incidental. When a session produces no disagreement,
check these first — one of them is almost always live and being papered over:

- **Austin vs. Farley** — speed of shipping vs. rigor of verification. The sharpest and
  most frequent split on the board.
- **Austin vs. Simon** — lean into agent leverage vs. evals, skepticism, and blast radius.
- **Gergely vs. Jeff** — optimize the market's read of you vs. build your own independent
  thing and let it compound.
- **Chapsas vs. Austin** — depth of craft vs. volume of output.
- **Simon vs. Chapsas** — good enough for a useful tool vs. good enough to be proud of.

## Running a session

### 1. Frame the question

State the decision in one sentence, as a decision — something with options and a cost to
getting it wrong. If the input is a situation rather than a question, convert it and
show the conversion so the user can correct it. A vague frame produces six vague takes.

If the real question is different from the stated one, say so before the takes. That
reframe is often the most valuable output of the whole session.

### 2. Pick who speaks

Default: all six. But an advisor with nothing to say should get one line, not a paragraph.
If the question is narrow (a C# API design call, a rendering bug), lead with the two
or three who own it and let the rest be brief.

The user can also name advisors directly — `/ask-the-board simon, austin: <question>` runs
just those two, in more depth.

### 3. Write the takes

Each take is roughly 4-8 sentences. Structure inside a take is free — these are people,
not a form — but every take must contain a **position**, not a survey of considerations.
An advisor who says "it depends" has not contributed.

Order the takes so the argument builds: start with whoever most challenges the premise,
end with whoever is closest to execution. Do not just run down the table.

### 4. Map the agreement and the split

Two short sections. Be specific about *what* is agreed, not that agreement exists.

If the board genuinely converges, say so — but treat it as a signal worth examining, not a
green light. Note explicitly what a dissenter would have said, and why nobody on this
particular board is positioned to say it. Unanimity usually means the board is missing a
seat, not that the answer is obvious.

### 5. Synthesize

This is the part the user actually reads. It is a verdict, not a summary — do not restate
the takes. It must contain:

- **The call.** One recommendation, stated plainly, with the reasoning compressed to a
  sentence or two. Pick a side even when it is close; note the closeness, do not hide in it.
- **This week.** The smallest concrete action that moves it. Something that could be
  started after reading. Not "consider" or "explore" — a thing that gets done.
- **What not to do.** Name the tempting adjacent thing to explicitly skip. This is
  usually where the real value is, because the common failure mode is building more
  infrastructure around a decision instead of making it.
- **What would change the verdict.** The specific evidence that would flip it. This keeps
  the board honest and gives a tripwire.

## Output format

Use this shape. Keep headings, drop sections that are genuinely empty.

```
## The question
<one sentence, as a decision. Plus a reframe if the stated question is the wrong one.>

## The takes

### Simon Willison — <five-word summary of his position>
<take>

### Dave Farley — <five-word summary>
<take>

... (remaining advisors)

## Where they agree
<2-4 bullets, specific>

## Where they split
<the live disagreements, each as: the two names, the actual point of contention, and
which side has the better of it here — do not leave it hanging>

## The call
<verdict>

**This week:** <one action>
**Skip:** <the tempting adjacent thing>
**What would change this:** <the tripwire>
```

## Style

Blunt verdicts, real domain terms, numbers carrying the argument wherever numbers exist.
No corporate hedging, no "we", no emojis. Confidence gets marked when it is low — "thin
evidence here" beats a confident guess, and the user will catch the guess anyway.

Length discipline matters: six takes plus synthesis should land around 600-900 words. If a
session is running long, the takes are padded — cut the advisors who are agreeing at
length rather than trimming the synthesis.

## Adding or changing advisors

The board is not fixed. To add, change, or retire a seat, edit the roster table above and
the corresponding dossier in `references/dossiers.md`. A new advisor needs all four
dossier fields — especially **blind spots**, since an advisor with no stated weakness will
quietly dominate every session.
