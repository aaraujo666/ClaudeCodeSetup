#!/usr/bin/env python
"""Keep Claude's memory directories as Open Knowledge Format (OKF v0.2) bundles.

Spec: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md

Each ~/.claude/projects/<key>/memory/ is one bundle. Every concept file carries
OKF frontmatter (`type`, `title`, `description`, `tags`, `status`, `generated`)
next to the harness's own keys (`name`, `metadata.type`), which OKF permits as
extensions. MEMORY.md stays the curated index the harness loads every session;
index.md (OKF's index) and log.md (OKF's update log) are derived from it.

    python okf.py convert <bundle>     one-time migration of a memory dir
    python okf.py check   <bundle>     conformance + house rules; exit 1 on errors
    python okf.py index   <bundle>     regenerate index.md from MEMORY.md
    python okf.py annotate <bundle>    stamp trust markers onto MEMORY.md lines
    python okf.py hook                 PostToolUse hook (stdin JSON): normalize the
                                       written concept, refresh index.md, log.md and
                                       the MEMORY.md markers
    python okf.py session              SessionStart hook: refresh markers in every
                                       bundle, report stale / soon-stale concepts

MEMORY.md is the only file the harness loads up front, so the trust signals ride on
it: `- [Title](file.md) [stale since 2026-10-01] [verified] — hook`. Markers are
derived from frontmatter (`status`, `stale_after`, `verified`) and rewritten on
every run, so never edit them by hand.

Python 3.9 compatible. PyYAML is optional: without it the
checks fall back to line-level parsing of the simple frontmatter used here.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys

OKF_VERSION = "0.2"
RESERVED = {"index.md", "log.md"}
HARNESS_INDEX = "MEMORY.md"
TYPE_MAP = {"user": "User", "feedback": "Feedback", "project": "Project", "reference": "Reference"}
# MEMORY.md section heading (lowercased) -> tags stamped on the concepts listed under it.
# Any heading not listed here is slugified into tags automatically; edit for your own.
SECTION_TAGS = {
    "how to work with me": ["working-rules"],
    "git and tracker": ["git", "tracker"],
    "mcp servers": ["mcp"],
    "toolchain": ["toolchain"],
}
MARKER = r"\[(?:deprecated|draft|verified|stale[^\]]*)\]"
LINK_RE = re.compile(r"^\s*[-*]\s+\[([^\]]+)\]\(([^)#\s]+\.md)\)((?:\s+%s)*)\s*(?:[—–-]+\s*(.*))?$" % MARKER)
SOON = dt.timedelta(days=7)
WIKILINK_RE = re.compile(r"\[\[([A-Za-z0-9_.-]+)\]\]")
BUMP_AFTER = dt.timedelta(minutes=10)


# ---------------------------------------------------------------- helpers

def now_utc():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    s = s.strip().strip("'\"")
    try:
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def split_fm(text):
    """Return (frontmatter_lines, body) or (None, text) when there is no block."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None, text


def top_keys(fm_lines):
    """Top-level scalar keys of a frontmatter block (line-level, no YAML needed)."""
    out = {}
    for ln in fm_lines:
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", ln)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def nested_value(fm_lines, parent, key):
    inside = False
    for ln in fm_lines:
        if re.match(r"^%s:\s*$" % re.escape(parent), ln):
            inside = True
            continue
        if inside:
            if not ln.startswith((" ", "\t")):
                break
            m = re.match(r"^\s+%s:\s*(.*)$" % re.escape(key), ln)
            if m:
                return m.group(1).strip()
    return None


def yq(s):
    """Quote a scalar for YAML unless it is plainly safe."""
    if s and re.match(r"^[A-Za-z0-9][\w ./()+,&'-]*$", s) and not s.endswith(":") and ": " not in s:
        return s
    return json.dumps(s, ensure_ascii=False)


def unq(s):
    s = (s or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        try:
            return json.loads(s) if s[0] == '"' else s[1:-1].replace("''", "'")
        except ValueError:
            return s[1:-1]
    return s


def git_last_commit(path):
    try:
        out = subprocess.run(["git", "-C", os.path.dirname(path), "log", "-1", "--format=%cI", "--",
                              os.path.basename(path)], capture_output=True, text=True, timeout=20).stdout.strip()
        return parse_iso(out) if out else None
    except Exception:
        return None


def concepts(bundle):
    return sorted(f for f in os.listdir(bundle)
                  if f.endswith(".md") and f not in RESERVED and f != HARNESS_INDEX)


# ---------------------------------------------------------------- MEMORY.md

def parse_harness_index(bundle):
    """[(section, [(title, file, hook)])] in MEMORY.md order."""
    path = os.path.join(bundle, HARNESS_INDEX)
    sections = [("General", [])]
    if not os.path.exists(path):
        return sections
    _, body = split_fm(read(path))
    for ln in body.split("\n"):
        h = re.match(r"^#{1,3}\s+(.*\S)\s*$", ln)
        if h:
            if h.group(1).lower() not in ("memory index",):
                sections.append((h.group(1), []))
            continue
        m = LINK_RE.match(ln)
        if m and "/" not in m.group(2):
            sections[-1][1].append((m.group(1).strip(), m.group(2), (m.group(4) or "").strip()))
    return [s for s in sections if s[1]]


def section_tags(section):
    key = section.lower()
    if key in SECTION_TAGS:
        return SECTION_TAGS[key]
    if key == "general":
        return []
    tags = []
    for part in re.split(r"\s+[—–]\s+", re.sub(r"\(.*?\)", "", section)):
        slug = re.sub(r"[^a-z0-9]+", "-", part.lower()).strip("-")
        if slug and slug not in tags:
            tags.append(slug)
    return tags


# ---------------------------------------------------------------- normalize

def okf_header(fm_lines, fname, entry, model, at):
    """OKF keys to add to a concept's frontmatter, as lines. Existing keys win."""
    keys = top_keys(fm_lines)
    add = []
    if "type" not in keys:
        mtype = (nested_value(fm_lines, "metadata", "type") or "").strip()
        add.append("type: " + TYPE_MAP.get(mtype, "Reference"))
    if "title" not in keys:
        title = entry[0] if entry else (unq(keys.get("name")) or fname[:-3]).replace("_", "-")
        add.append("title: " + yq(title))
    if "tags" not in keys and entry is not None:
        tags = list(entry[3])
        if "TRAP" in entry[2] and "trap" not in tags:
            tags.append("trap")
        if tags:
            add.append("tags: [" + ", ".join(tags) + "]")
    if "status" not in keys:
        add.append("status: " + ("deprecated" if entry and "SUPERSEDED" in entry[2] else "stable"))
    if "generated" not in keys:
        add.append("generated: { by: %s, at: %s }" % (model, iso(at)))
    return add


HARNESS_META = {"node_type", "type", "originSessionId", "modified"}


def hoist_from_metadata(fm):
    """When the harness creates a memory file it moves every top-level key it doesn't own
    (title, tags, status, stale_after, sources, ...) under `metadata:`. Move those back to the
    top level, where OKF consumers look; an author's value beats a hook-made default."""
    start = next((i for i, l in enumerate(fm) if re.match(r"^metadata:\s*$", l)), None)
    if start is None:
        return fm
    end = start + 1
    while end < len(fm) and (fm[end].startswith((" ", "\t")) or not fm[end].strip()):
        end += 1
    block = fm[start + 1:end]
    ind = min((len(l) - len(l.lstrip(" ")) for l in block if l.strip()), default=2)
    keep, hoisted, cur = [], {}, None
    for l in block:
        m = re.match(r"^ {%d}([A-Za-z_][\w-]*):" % ind, l)
        if m:
            cur = None if m.group(1) in HARNESS_META else m.group(1)
            if cur:
                hoisted[cur] = []
        (hoisted[cur] if cur else keep).append(l[ind:] if cur else l)
    if not hoisted:
        return fm
    top = fm[:start] + fm[end:]
    out = []
    i = 0
    while i < len(top):  # drop top-level keys the hoisted ones replace (with their nested lines)
        m = re.match(r"^([A-Za-z_][\w-]*):", top[i])
        if m and m.group(1) in hoisted:
            i += 1
            while i < len(top) and top[i].startswith((" ", "\t", "-")):
                i += 1
            continue
        out.append(top[i])
        i += 1
    lifted = [l for k in hoisted for l in hoisted[k]]
    meta_at = next((n for n, l in enumerate(out) if l.startswith("name:")), len(out))
    return out[:meta_at] + lifted + out[meta_at:] + ["metadata:"] + keep


def normalize(path, entry=None, model="claude-code/unknown", at=None, bump=False):
    """Bring one concept file to the house OKF shape. Returns True if it changed."""
    text = read(path)
    fname = os.path.basename(path)
    fm, body = split_fm(text)
    if fm is None:
        first = next((l.lstrip("# ").strip() for l in body.split("\n") if l.strip()), fname[:-3])
        fm = ["name: " + fname[:-3], "description: " + yq(first)]
    fm = hoist_from_metadata(fm)
    at = at or now_utc()
    add = okf_header(fm, fname, entry, model, at)
    fm = add + fm
    if bump:
        fm = bump_generated(fm, model, at)
    body = WIKILINK_RE.sub(lambda m: "[%s](/%s.md)" % (m.group(1), m.group(1)), body)
    new = "---\n" + "\n".join(fm) + "\n---\n" + body
    if new != text:
        write(path, new)
        return True
    return False


def bump_generated(fm, model, at):
    out = []
    for ln in fm:
        m = re.match(r"^generated:\s*\{(.*)\}\s*$", ln)
        if m:
            prev = re.search(r"at:\s*([^,}\s]+)", m.group(1))
            prev_t = parse_iso(prev.group(1)) if prev else None
            if prev_t is None or at - prev_t >= BUMP_AFTER:
                ln = "generated: { by: %s, at: %s }" % (model, iso(at))
        out.append(ln)
    return out


def ensure_harness_index_type(path):
    """MEMORY.md is a concept to OKF, so it needs a top-level `type`. The harness rewrites
    its frontmatter on every edit (moving a lone `type` under `metadata`), so restore it."""
    text = read(path)
    fm, body = split_fm(text)
    if fm is None:
        fm = ["description: Curated index of this bundle, loaded into every Claude Code session; "
              "index.md is generated from it."]
        body = "\n" + body.lstrip("\n")
    if "type" in top_keys(fm):
        return False
    fm = ["type: Memory Index"] + [l for l in fm if not re.match(r'^name:\s*(""|\'\')?\s*$', l)]
    write(path, "---\n" + "\n".join(fm) + "\n---\n" + body)
    return True


def index_entries(bundle):
    """file -> (title, section, hook, tags) from MEMORY.md."""
    out = {}
    for section, items in parse_harness_index(bundle):
        for title, f, hook in items:
            out.setdefault(f, (title, hook, section_tags(section), section))
    return {f: (t, s, h, tags) for f, (t, h, tags, s) in out.items()}


def entry_for(entries, fname):
    e = entries.get(fname)
    return None if e is None else (e[0], e[1], e[2], e[3])  # title, section, hook, tags


# ---------------------------------------------------------------- index / log

def concept_meta(path):
    fm, _ = split_fm(read(path))
    keys = top_keys(fm or [])
    return unq(keys.get("title")) or os.path.basename(path)[:-3], unq(keys.get("description")), keys.get("type", "")


def build_index(bundle):
    lines = ["---", 'okf_version: "%s"' % OKF_VERSION, "---", ""]
    seen = set()
    for section, items in parse_harness_index(bundle):
        rows = []
        for title, f, _ in items:
            p = os.path.join(bundle, f)
            if f in seen or not os.path.exists(p):
                continue
            seen.add(f)
            t, d, _ = concept_meta(p)
            rows.append("* [%s](%s) - %s" % (t, f, d) if d else "* [%s](%s)" % (t, f))
        if rows:
            lines += ["# " + section, ""] + rows + [""]
    rest = [f for f in concepts(bundle) if f not in seen]
    if rest:
        lines += ["# Unindexed", ""]
        for f in rest:
            t, d, _ = concept_meta(os.path.join(bundle, f))
            lines.append("* [%s](%s) - %s" % (t, f, d) if d else "* [%s](%s)" % (t, f))
        lines.append("")
    new = "\n".join(lines)
    p = os.path.join(bundle, "index.md")
    if not os.path.exists(p) or read(p) != new:
        write(p, new)
        return True
    return False


def log_event(bundle, verb, fname, title, day=None):
    """Add `* **verb**: [title](/fname)` under today's heading, once per file per day."""
    day = day or dt.date.today().isoformat()
    p = os.path.join(bundle, "log.md")
    text = read(p) if os.path.exists(p) else "# Knowledge Update Log\n"
    link = "(/%s)" % fname
    head = "## " + day
    lines = text.rstrip("\n").split("\n")
    if head in lines:
        i = lines.index(head)
        j = i + 1
        while j < len(lines) and not lines[j].startswith("## "):
            if link in lines[j]:
                return False
            j += 1
        while j > i + 1 and not lines[j - 1].strip():
            j -= 1
        lines.insert(j, "* **%s**: [%s]%s" % (verb, title, link))
    else:
        k = next((n for n, l in enumerate(lines) if l.startswith("## ")), len(lines))
        block = [head, "* **%s**: [%s]%s" % (verb, title, link), ""]
        if k == len(lines):
            block = [""] + block[:-1]
        lines[k:k] = block
    write(p, "\n".join(lines) + "\n")
    return True


# ---------------------------------------------------------------- trust markers

def trust(path):
    """(status, stale_after datetime|None, human_verified bool) from a concept's frontmatter."""
    fm, _ = split_fm(read(path))
    fm = fm or []
    status = unq(top_keys(fm).get("status")) or "stable"
    stale = parse_iso(unq(top_keys(fm).get("stale_after") or "")) if top_keys(fm).get("stale_after") else None
    human = False
    inside = False
    for ln in fm:
        if re.match(r"^verified:", ln):
            inside = True
            human = "human:" in ln
            continue
        if inside:
            if not ln.startswith((" ", "\t", "-")):
                break
            human = human or "human:" in ln
    return status, stale, human


def markers_for(path, now):
    status, stale, human = trust(path)
    out = []
    if status in ("deprecated", "draft"):
        out.append("[%s]" % status)
    if stale is not None and now >= stale and status != "deprecated":
        out.append("[stale since %s]" % stale.date().isoformat())
    if human:
        out.append("[verified]")
    return out


def annotate(bundle, now=None):
    """Rewrite the trust markers on every MEMORY.md link line. Returns True if changed."""
    now = now or now_utc()
    p = os.path.join(bundle, HARNESS_INDEX)
    if not os.path.exists(p):
        return False
    text = read(p)
    out = []
    for ln in text.split("\n"):
        m = LINK_RE.match(ln)
        target = os.path.join(bundle, m.group(2)) if m and "/" not in m.group(2) else None
        if target and os.path.exists(target):
            marks = "".join(" " + mk for mk in markers_for(target, now))
            ln = ln[:m.end(2) + 1] + marks + ln[m.end(3):]
        out.append(ln)
    new = "\n".join(out)
    if new != text:
        write(p, new)
        return True
    return False


def stale_report(bundle, now):
    """[(state, title, file, stale_after)] for concepts stale now or within SOON."""
    rows = []
    for f in concepts(bundle):
        path = os.path.join(bundle, f)
        status, stale, _ = trust(path)
        if stale is None or status == "deprecated":
            continue
        if now >= stale:
            rows.append(("STALE", concept_meta(path)[0], f, stale))
        elif stale - now <= SOON:
            rows.append(("stale soon", concept_meta(path)[0], f, stale))
    return rows


def all_bundles():
    root = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    if not os.path.isdir(root):
        return []
    return sorted(os.path.join(root, k, "memory") for k in os.listdir(root)
                  if os.path.isfile(os.path.join(root, k, "memory", HARNESS_INDEX)))


def mcp_config_files():
    home = os.path.expanduser("~")
    return [os.path.join(home, ".claude.json"),
            os.path.join(os.environ.get("APPDATA", ""), "Claude", "claude_desktop_config.json"),
            os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")]


def registered_mcp_servers(files=None):
    """Names of MCP servers registered locally: user + project scope in ~/.claude.json and the
    desktop app's config. claude.ai connectors aren't in any local file, so they're not here."""
    names = set()
    for p in files or mcp_config_files():
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        names.update((d.get("mcpServers") or {}).keys())
        for proj in (d.get("projects") or {}).values():
            names.update((proj.get("mcpServers") or {}).keys())
    return names


def inventoried_mcp_servers(bundles):
    """Union of every concept's `mcp_servers: [a, b]` frontmatter list."""
    names = set()
    for b in bundles:
        for f in concepts(b):
            fm, _ = split_fm(read(os.path.join(b, f)))
            names.update(fm_list(fm or [], "mcp_servers"))
    return names


def fm_list(fm, key):
    """A top-level YAML list in either flow (`k: [a, b]`) or block (`k:` + `- a`) form; the
    harness rewrites flow lists to block form when it saves a memory."""
    for i, ln in enumerate(fm):
        m = re.match(r"^%s:\s*(.*)$" % re.escape(key), ln)
        if not m:
            continue
        v = m.group(1).strip()
        if v:
            return [x.strip().strip("'\"") for x in v.strip("[]").split(",") if x.strip()]
        out = []
        for nxt in fm[i + 1:]:
            mm = re.match(r"^\s*-\s+(.*\S)\s*$", nxt)
            if not mm:
                break
            out.append(mm.group(1).strip("'\""))
        return out
    return []


def cmd_session():
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    now = now_utc()
    lines = []
    bundles = all_bundles()
    for b in bundles:
        try:
            annotate(b, now)
            rows = stale_report(b, now)
        except Exception as e:  # a broken bundle must never block a session
            lines.append("okf: could not scan %s (%s)" % (b, e))
            continue
        for state, title, f, at in rows:
            lines.append("- %s: %s (%s), stale_after %s" % (state, title, os.path.join(b, f), iso(at)))
    try:
        listed = inventoried_mcp_servers(bundles)
        new = sorted(registered_mcp_servers() - listed) if listed else []
    except Exception:
        new = []
    for name in new:
        lines.append("- MCP server `%s` is registered but missing from the MCP inventory memory "
                     "(reference-mcp-inventory): add it there and to its `mcp_servers` list." % name)
    if lines:
        msg = ("OKF memory freshness: verify these before relying on them; after re-checking a fact, "
               "move its `stale_after` forward (and add `verified` only if the user confirmed it).\n"
               + "\n".join(lines))
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}}))
    return 0


# ---------------------------------------------------------------- check

def check_file(bundle, fname, listed):
    errs, warns = [], []
    text = read(os.path.join(bundle, fname))
    fm, body = split_fm(text)
    if fm is None:
        return ["%s: no YAML frontmatter block" % fname], warns
    try:
        import yaml
        data = yaml.safe_load("\n".join(fm)) or {}
        if not isinstance(data, dict):
            errs.append("%s: frontmatter is not a mapping" % fname)
            data = {}
    except ImportError:
        data = {k: unq(v) for k, v in top_keys(fm).items()}
    except Exception as e:
        return ["%s: frontmatter is not valid YAML (%s)" % (fname, str(e).split("\n")[0])], warns
    if not str(data.get("type") or "").strip():
        errs.append("%s: missing required `type`" % fname)
    if fname == HARNESS_INDEX:
        return errs, warns
    for k in ("title", "description", "generated"):
        if not data.get(k):
            warns.append("%s: missing `%s`" % (fname, k))
    st = data.get("status")
    if st and st not in ("draft", "stable", "deprecated"):
        errs.append("%s: status %r not draft|stable|deprecated" % (fname, st))
    gen = data.get("generated")
    if isinstance(gen, dict) and not gen.get("by"):
        errs.append("%s: `generated` has no `by`" % fname)
    if WIKILINK_RE.search(body):
        errs.append("%s: [[wikilink]] found; use a markdown link [name](/name.md)" % fname)
    if listed is not None and fname not in listed:
        warns.append("%s: not listed in MEMORY.md" % fname)
    return errs, warns


def check(bundle, only=None):
    listed = set(index_entries(bundle))
    errs, warns = [], []
    files = [only] if only else concepts(bundle) + ([HARNESS_INDEX] if os.path.exists(
        os.path.join(bundle, HARNESS_INDEX)) else [])
    for f in files:
        e, w = check_file(bundle, f, listed)
        errs += e
        warns += w
    for name in RESERVED:
        p = os.path.join(bundle, name)
        if os.path.exists(p) and name == "log.md":
            for ln in read(p).split("\n"):
                if ln.startswith("## ") and not re.match(r"^## \d{4}-\d{2}-\d{2}$", ln):
                    errs.append("log.md: date heading %r not YYYY-MM-DD" % ln)
    return errs, warns


# ---------------------------------------------------------------- commands

def cmd_convert(bundle, model):
    entries = index_entries(bundle)
    changed = 0
    for f in concepts(bundle):
        p = os.path.join(bundle, f)
        fm, _ = split_fm(read(p))
        mod = nested_value(fm or [], "metadata", "modified")
        at = (parse_iso(mod) if mod else None) or git_last_commit(p) or \
            dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc)
        changed += normalize(p, entry_for(entries, f), model, at.replace(microsecond=0))
    hp = os.path.join(bundle, HARNESS_INDEX)
    if os.path.exists(hp):
        ensure_harness_index_type(hp)
    build_index(bundle)
    n = len(concepts(bundle))
    p = os.path.join(bundle, "log.md")
    if not os.path.exists(p):
        write(p, "# Knowledge Update Log\n\n## %s\n* **Initialization**: Converted %d memories to OKF v%s "
                 "(added `type`, `title`, `tags`, `status`, `generated`; `[[wikilinks]]` became markdown "
                 "links); generated [index](/index.md).\n" % (dt.date.today().isoformat(), n, OKF_VERSION))
    print("%s: %d of %d concepts changed" % (bundle, changed, n))


def transcript_model(path):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 400000))
            tail = f.read().decode("utf-8", "replace")
        found = re.findall(r'"model"\s*:\s*"(claude-[\w.-]+)"', tail)
        return "claude-code/" + found[-1] if found else None
    except Exception:
        return None


def cmd_hook():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    ti = data.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    norm = path.replace("\\", "/")
    m = re.search(r"/\.claude/projects/[^/]+/memory/([^/]+\.md)$", norm)
    if not m:
        return 0
    bundle, fname = os.path.dirname(path), m.group(1)
    if fname in RESERVED or not os.path.exists(path):
        return 0
    msgs = []
    if fname != HARNESS_INDEX:
        was_indexed = os.path.exists(os.path.join(bundle, "index.md")) and \
            ("](%s)" % fname) in read(os.path.join(bundle, "index.md"))
        model = transcript_model(data.get("transcript_path") or "") or "claude-code/unknown"
        if normalize(path, entry_for(index_entries(bundle), fname), model, now_utc(), bump=True):
            msgs.append("okf: normalized %s (OKF frontmatter / links); re-read it before the next Edit." % fname)
        title = concept_meta(path)[0]
        log_event(bundle, "Update" if was_indexed else "Creation", fname, title)
        errs, warns = check(bundle, fname)
        msgs += ["okf ERROR: " + e for e in errs] + ["okf warning: " + w for w in warns]
    else:
        ensure_harness_index_type(path)
    annotate(bundle)
    build_index(bundle)
    if msgs:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                 "additionalContext": "\n".join(msgs)}}))
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "hook":
        return cmd_hook()
    if cmd == "session":
        return cmd_session()
    if len(argv) < 3:
        print(__doc__)
        return 2
    bundle = os.path.abspath(argv[2])
    if cmd == "convert":
        cmd_convert(bundle, argv[3] if len(argv) > 3 else "claude-code/unknown")
        return 0
    if cmd == "annotate":
        print("MEMORY.md " + ("updated" if annotate(bundle) else "unchanged"))
        return 0
    if cmd == "index":
        print("index.md " + ("updated" if build_index(bundle) else "unchanged"))
        return 0
    if cmd == "check":
        errs, warns = check(bundle)
        for w in warns:
            print("warning: " + w)
        for e in errs:
            print("ERROR: " + e)
        print("%s: %d concepts, %d errors, %d warnings" % (bundle, len(concepts(bundle)), len(errs), len(warns)))
        return 1 if errs else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
