"""Shell parsing for the PreToolUse guards, in one place.

The guards used to grep the raw command line, which misjudges it two ways:

  variables  `W=/c/.../source/worktrees/x; rm $W/f` -- the rm never spells out the
             path, so an exemption missed (a needless prompt) or a check missed
             (something slipped through).
  quoting    `git commit -m "the find and -delete guards"` -- words inside a quoted
             argument were read as commands, and a `;` inside quotes split the line.

`parse()` is a small quote-aware tokenizer: it splits on UNQUOTED separators, strips
quotes, substitutes variables assigned earlier in the same line, and returns each
command with its command word resolved. Command substitutions (`$(...)`, backticks)
and `bash -c` / `powershell -Command` strings are parsed too and returned as commands
of their own, so `ls $(find / -name x)` still shows a find.

Only assignments made earlier in the SAME line are known. A variable from an earlier
tool call, the environment, or `$(...)` stays as written (`$W`), and each guard decides
what an unresolved name means for it. This is a drift guard's parser, not a shell:
it errs towards seeing a command, never towards hiding one.

Imported by block-file-delete.sh, block-work-to-third-party.py,
block-unbounded-find.sh, block-cd-git.sh, block-heredoc.sh and block-long-sleep.sh.
Regression suite: tests/test_hooks.py.
"""
import re

NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.S)
WRAPPERS = {"sudo", "command", "exec", "nohup", "time", "&", "builtin"}
SHELLS = {"bash", "sh", "zsh", "dash"}
POWERSHELLS = {"powershell", "pwsh"}


class Word(str):
    """A word with quotes removed. `glob` is True when *, ? or [ appeared unquoted."""
    glob = False


class Command:
    """One simple command. `words` is everything; `name` is the command word after
    env assignments and wrappers (sudo, env, timeout, ...), lowercased, without its
    directory or a .exe/.cmd/.ps1/.bat extension; `args` follows it."""

    def __init__(self, words):
        self.words = words
        self.name, self.args = "", []
        i = 0
        while i < len(words) and ASSIGN.match(words[i]):
            i += 1
        while i < len(words):
            w = words[i].lower()
            if w in WRAPPERS:
                i += 1
            elif w == "env":
                i += 1
                while i < len(words) and (ASSIGN.match(words[i]) or words[i].startswith("-")):
                    i += 1
            elif w in ("timeout", "nice", "xargs", "stdbuf"):
                i += 1
                while i < len(words) and (words[i].startswith("-")
                                          or re.fullmatch(r"[0-9.]+[smhd]?", words[i])):
                    i += 1
            else:
                break
        if i < len(words):
            base = re.split(r"[\\/]", words[i])[-1].lower()
            self.name = re.sub(r"\.(exe|cmd|ps1|bat)$", "", base)
            self.args = words[i + 1:]

    @property
    def text(self):
        return " ".join(self.words)

    def __repr__(self):
        return f"Command({self.words!r})"


class Parsed(list):
    """The commands of a line, in order (nested ones right after their parent).
    `heredoc` is True when an unquoted `<<WORD` (not `<<<`) appeared."""
    heredoc = False


def _balanced(s, i):
    """Index just past the `)` closing the `(` at s[i-1], honouring quotes."""
    depth, q = 1, None
    while i < len(s):
        c = s[i]
        if q:
            if c == q:
                q = None
            elif c == "\\" and q == '"':
                i += 1
        elif c in "'\"":
            q = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i


def parse(cmd, ps=False, known=None, _depth=0):
    """Commands in `cmd`. `ps=True` for PowerShell: backtick is the escape character
    (not command substitution), a backslash is a plain path character, and a lone
    `&` is the call operator rather than a separator."""
    known = dict(known or {})
    out = Parsed()
    nested = []
    words, cur, started, glob = [], [], False, False
    i, n = 0, len(cmd)

    def var_at(j):
        """(value, end) for a $NAME / ${NAME} at cmd[j]; unknown names stay as written."""
        m = re.match(r"\$\{([A-Za-z_]\w*)\}|\$([A-Za-z_]\w*)", cmd[j:])
        if not m:
            return None
        name = m.group(1) or m.group(2)
        return known.get(name, m.group(0)), j + m.end()

    def subst(j):
        """Parse the $( ... ) starting at cmd[j]; return its raw text and end."""
        end = _balanced(cmd, j + 2)
        if _depth < 8:
            nested.extend(parse(cmd[j + 2:end - 1], ps, known, _depth + 1))
        return cmd[j:end], end

    def end_word():
        nonlocal cur, started, glob
        if started:
            w = Word("".join(cur))
            w.glob = glob
            words.append(w)
        cur, started, glob = [], False, False

    def end_command():
        nonlocal words, nested
        end_word()
        if words:
            plain = words[1:] if words[0] == "export" and len(words) > 1 else words
            if all(ASSIGN.match(w) for w in plain):
                for w in plain:
                    k, v = ASSIGN.match(w).groups()
                    known[k] = v
            else:
                c = Command(words)
                out.append(c)
                out.extend(_inner_shell(c, known, _depth))
        out.extend(nested)
        words, nested = [], []

    while i < n:
        c = cmd[i]
        if c == "'":
            j = cmd.find("'", i + 1)
            j = n if j < 0 else j
            cur.append(cmd[i + 1:j])
            started, i = True, j + 1
        elif c == '"':
            i += 1
            started = True
            while i < n and cmd[i] != '"':
                d = cmd[i]
                if d == "\\" and not ps and i + 1 < n and cmd[i + 1] in '"\\$`':
                    cur.append(cmd[i + 1])
                    i += 2
                elif d == "`" and ps and i + 1 < n:
                    cur.append(cmd[i + 1])
                    i += 2
                elif d == "`" and not ps:
                    j = cmd.find("`", i + 1)
                    j = n if j < 0 else j
                    if _depth < 8:
                        nested.extend(parse(cmd[i + 1:j], ps, known, _depth + 1))
                    cur.append(cmd[i:j + 1])
                    i = j + 1
                elif d == "$" and cmd[i + 1:i + 2] == "(":
                    raw, i = subst(i)
                    cur.append(raw)
                elif d == "$" and var_at(i):
                    val, i = var_at(i)
                    cur.append(val)
                else:
                    cur.append(d)
                    i += 1
            i += 1
        elif c == "\\" and not ps:
            if i + 1 < n and cmd[i + 1] == "\n":
                i += 2
                continue
            cur.append(cmd[i + 1:i + 2])
            started, i = True, i + 2
        elif c == "`" and ps:
            cur.append(cmd[i + 1:i + 2])
            started, i = True, i + 2
        elif c == "`":
            j = cmd.find("`", i + 1)
            j = n if j < 0 else j
            if _depth < 8:
                nested.extend(parse(cmd[i + 1:j], ps, known, _depth + 1))
            cur.append(cmd[i:j + 1])
            started, i = True, j + 1
        elif c == "$" and cmd[i + 1:i + 2] == "(":
            raw, i = subst(i)
            cur.append(raw)
            started = True
        elif c == "$" and var_at(i):
            val, i = var_at(i)
            cur.append(val)
            started = True
        elif c in " \t":
            end_word()
            i += 1
        elif c == "#" and not started and not ps:
            j = cmd.find("\n", i)
            i = n if j < 0 else j
        elif c == "&" and (cmd[i - 1:i] in "<>" and i > 0 or cmd[i + 1:i + 2] == ">"):
            cur.append(c)  # 2>&1, &>file: a redirection, not a separator
            started, i = True, i + 1
        elif c == "&" and ps and cmd[i + 1:i + 2] != "&":
            end_word()
            words.append(Word("&"))  # PowerShell call operator
            i += 1
        elif c in ";|&\n\r()":
            end_command()
            i += 1
        elif c == "<" and cmd[i:i + 3] == "<<<" and not ps:
            cur.append("<<<")  # here-string: one line, not a heredoc
            started, i = True, i + 3
        elif c == "<" and cmd[i:i + 2] == "<<" and not ps:
            if re.match(r"<<-?\s*['\"]?[A-Za-z_]", cmd[i:]):
                out.heredoc = True
            cur.append("<<")
            started, i = True, i + 2
        else:
            if c in "*?[":
                glob = True
            cur.append(c)
            started, i = True, i + 1
    end_command()
    return out


def _inner_shell(c, known, depth):
    """Commands inside `bash -c '...'` / `powershell -Command ...` / `cmd /c ...`."""
    if depth >= 8:
        return []
    a = [w.lower() for w in c.args]
    if c.name in SHELLS and "-c" in a:
        k = a.index("-c")
        return parse(c.args[k + 1], False, known, depth + 1) if k + 1 < len(a) else []
    if c.name in POWERSHELLS:
        for k, w in enumerate(a):
            if w in ("-c", "-command"):
                return parse(" ".join(c.args[k + 1:]), True, known, depth + 1)
    if c.name == "cmd" and "/c" in a:
        return parse(" ".join(c.args[a.index("/c") + 1:]), False, known, depth + 1)
    return []


def segments(cmd):
    """The line split on UNQUOTED ; & | and newlines, with variables assigned earlier
    in the line substituted. Assignment-only segments are recorded, not returned.
    Kept for guards that regex a segment's text (block-long-sleep.sh); new guards
    should use parse() and judge Command.name / Command.args instead."""
    return [c.text for c in parse(cmd)]


def expand(cmd):
    """The whole line, parsed and rejoined: `; ` between commands, quotes removed."""
    return "; ".join(segments(cmd))
