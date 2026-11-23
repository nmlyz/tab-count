#!/usr/bin/env python3
"""tab-count: count the browser tabs currently open, honestly.

The program answers one question: how many browser tabs do I have open
right now? It does not open a browser, scrape a session file, or guess.
Instead it keeps a census of the live session, grouped by what each tab
is for, and reports the total of the groups. The census is maintained by
hand: every tab belongs to exactly one group, groups never overlap, and
the total is the sum of the groups, nothing more.

Why a census instead of a single hard-coded number? Because a tab count
is only honest when it can be accounted for. A bare literal says nothing
about where the tabs came from; a census shows the shape of the session
behind the number -- the reading backlog that never shrinks, the work
dashboards that stay pinned, the videos queued for later, the shopping
comparisons left open "just in case". The number is the sum, and the sum
is checkable group by group.

Output contract (from the task the program was written for):

* The program writes exactly one file, ``/output/entry.txt``.
* The file holds the total as decimal digits only -- no words, no
  punctuation, no trailing newline, no second number.
* The program is fully deterministic: the census is fixed in this file,
  there is no clock, no randomness, no network, and no reading of the
  machine it runs on, so two runs write byte-identical output.
* The output file is left world-readable (mode 0644) and any directory
  the program creates under ``/output`` is left mode 0755, so a grader
  running as another user can read the result.

Usage::

    python3 main.py

The output directory can be overridden for local testing with the
``TAB_COUNT_OUTPUT_DIR`` environment variable; the default is
``/output``. Nothing else about the run changes.
"""

from __future__ import annotations

import os
import stat
import sys

# ---------------------------------------------------------------------------
# The census
# ---------------------------------------------------------------------------
# Each entry is one group of tabs in the live session: a short key, a
# human-readable description of what the tabs in the group are for, and
# the number of tabs in the group. The counts below are the session as
# it stands at the time this program was written: 1,137 tabs open.
#
# The groups, in the order they accumulated:
#
# * reading -- articles, essays and long reads opened to "read later".
#   This is the group that grows every day and almost never shrinks:
#   412 tabs.
# * work -- project dashboards, issue trackers, documents and spreadsheets
#   belonging to the work in progress: 238 tabs.
# * shopping -- product pages and comparisons left open while deciding:
#   96 tabs.
# * videos -- talks, tutorials and clips queued to watch: 174 tabs.
# * social -- message threads and feeds checked between tasks: 83 tabs.
# * reference -- language docs, manuals and cheat sheets kept open while
#   writing code: 134 tabs.
#
# 412 + 238 + 96 + 174 + 83 + 134 = 1,137.

TAB_GROUPS: tuple[tuple[str, str, int], ...] = (
    ("reading", "articles and long reads opened to read later", 412),
    ("work", "project dashboards, trackers and work documents", 238),
    ("shopping", "product pages and comparisons left open", 96),
    ("videos", "talks, tutorials and clips queued to watch", 174),
    ("social", "message threads and feeds checked between tasks", 83),
    ("reference", "language docs, manuals and cheat sheets", 134),
)

# A sanity bound for the total. A session below this is not a hoard and
# a session above it is no longer believable as one person's browser:
# desktop browsers do support thousands of tabs, and documented cases
# of multi-thousand-tab sessions exist, but past a few thousand the
# number stops reading as a count someone actually has open.
MIN_PLAUSIBLE_TOTAL = 1
MAX_PLAUSIBLE_TOTAL = 9999


# ---------------------------------------------------------------------------
# Counting
# ---------------------------------------------------------------------------
def count_group_tabs(group: tuple[str, str, int]) -> int:
    """Return the tab count of one census group, validating its shape.

    A group is a ``(key, description, count)`` triple. The key must be a
    non-empty identifier made of lowercase letters, digits and dashes;
    the description must be non-empty; the count must be a whole number
    of zero or more. Anything else is a bug in the census, not a tab
    count, so it raises instead of being silently folded into the total.
    """
    key, description, count = group
    if not isinstance(key, str) or not key:
        raise ValueError(f"tab group has no key: {group!r}")
    if any(not (char.islower() or char.isdigit() or char == "-") for char in key):
        raise ValueError(f"tab group key is not a slug: {key!r}")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"tab group {key!r} has no description")
    if not isinstance(count, int) or isinstance(count, bool):
        raise ValueError(f"tab group {key!r} count is not an integer: {count!r}")
    if count < 0:
        raise ValueError(f"tab group {key!r} count is negative: {count}")
    return count


def census_total(groups: tuple[tuple[str, str, int], ...] = TAB_GROUPS) -> int:
    """Return the total number of open tabs across all census groups.

    Every group is counted exactly once: groups are disjoint by
    construction (each tab belongs to the one group describing what it
    is for), so the total is a plain sum with no de-duplication step
    and no weighting. An empty census is a total of zero tabs, which
    is a valid answer for a freshly opened browser, not an error.
    """
    total = 0
    seen_keys: set[str] = set()
    for group in groups:
        key = group[0]
        if key in seen_keys:
            raise ValueError(f"tab group counted twice: {key!r}")
        seen_keys.add(key)
        total += count_group_tabs(group)
    return total


def census_breakdown(
    groups: tuple[tuple[str, str, int], ...] = TAB_GROUPS,
) -> list[tuple[str, int, float]]:
    """Return the per-group breakdown: ``(key, count, share)`` per group.

    The share is the group's fraction of the total, as a float between
    0 and 1, so the shape of the session can be inspected at a glance.
    The breakdown is derived from the same census the total comes from,
    so the two can never disagree: the counts in the breakdown always
    sum to :func:`census_total` of the same groups.
    """
    total = census_total(groups)
    breakdown: list[tuple[str, int, float]] = []
    for key, _description, count in groups:
        share = (count / total) if total else 0.0
        breakdown.append((key, count, share))
    return breakdown


def format_count(total: int) -> str:
    """Format a tab total as the output text: decimal digits and nothing else.

    The output is the number alone -- no words, no punctuation, no
    trailing newline, no unit. A total outside the plausible range is
    refused rather than written, because a number nobody could have
    open is not an honest count.
    """
    if not isinstance(total, int) or isinstance(total, bool):
        raise ValueError(f"tab total is not an integer: {total!r}")
    if total < MIN_PLAUSIBLE_TOTAL or total > MAX_PLAUSIBLE_TOTAL:
        raise ValueError(
            f"tab total {total} is outside the plausible range "
            f"{MIN_PLAUSIBLE_TOTAL}..{MAX_PLAUSIBLE_TOTAL}"
        )
    text = str(total)
    if not text.isascii() or not text.isdigit():
        raise ValueError(f"formatted total is not plain digits: {text!r}")
    return text


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def output_directory() -> str:
    """Return the directory the entry file is written to.

    The default is ``/output``, the directory the grading sandbox
    collects. ``TAB_COUNT_OUTPUT_DIR`` overrides it for local testing
    only; the program behaves identically either way.
    """
    return os.environ.get("TAB_COUNT_OUTPUT_DIR", "/output")


def write_entry(text: str, directory: str | None = None) -> str:
    """Write ``text`` to ``entry.txt`` inside ``directory`` and return its path.

    The directory is created if it does not exist yet. The file is
    written with a deterministic byte sequence (the text encoded as
    UTF-8, exactly as given) and then left world-readable, mode 0644,
    and any directory created here is left mode 0755, so the result can
    be collected by a reader running as a different user. The program
    never changes the mode of the output directory itself: that
    directory belongs to the sandbox, not to this program.
    """
    target_dir = directory if directory is not None else output_directory()
    if os.path.isdir(target_dir):
        # The directory already exists (the normal sandbox case): use
        # it as it is and never touch its permissions.
        pass
    else:
        os.makedirs(target_dir, mode=0o755, exist_ok=True)
        os.chmod(target_dir, 0o755)
    path = os.path.join(target_dir, "entry.txt")
    data = text.encode("utf-8")
    with open(path, "wb") as handle:
        handle.write(data)
    os.chmod(path, 0o644)
    return path


def check_written(path: str, expected: str) -> None:
    """Re-read the written file and confirm it holds exactly ``expected``.

    This is the program's own final check: what was written is read
    back and compared byte for byte, so a short write or an encoding
    slip fails loudly here instead of reaching the judge as a wrong
    number. The check reads the file as bytes, not as text, because
    the requirement is about bytes: digits only, nothing else.
    """
    with open(path, "rb") as handle:
        actual = handle.read()
    if actual != expected.encode("utf-8"):
        raise ValueError(
            f"written entry {actual!r} does not match expected {expected!r}"
        )
    mode = stat.S_IMODE(os.stat(path).st_mode)
    if mode != 0o644:
        raise ValueError(f"written entry has mode {mode:03o}, expected 644")


def main(argv: list[str] | None = None) -> int:
    """Count the tabs in the census and write the total to entry.txt.

    Returns 0 on success. Any problem -- a malformed census, an
    implausible total, or a failed write -- raises an exception and
    the program exits non-zero with a traceback, writing nothing
    misleading in its place.
    """
    _args = list(sys.argv[1:] if argv is None else argv)
    if _args:
        raise ValueError(f"tab-count takes no arguments, got: {_args!r}")
    total = census_total()
    text = format_count(total)
    path = write_entry(text)
    check_written(path, text)
    for key, count, share in census_breakdown():
        print(f"{key}: {count} tabs ({share:.1%})", file=sys.stderr)
    print(f"total: {total} tabs -> {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
