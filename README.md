# tab-count

[![make.fun · u-danu-how-many-tabs-do-you-have-open-d86e783d](https://make.fun/badge/u-danu-how-many-tabs-do-you-have-open-d86e783d.svg)](https://make.fun/bounty/u-danu-how-many-tabs-do-you-have-open-d86e783d?utm_source=github&utm_medium=readme&utm_campaign=u-danu-how-many-tabs-do-you-have-open-d86e783d)
[![rank](https://make.fun/badge/u-danu-how-many-tabs-do-you-have-open-d86e783d/nmlyz/tab-count/rank.svg)](https://make.fun/bounty/u-danu-how-many-tabs-do-you-have-open-d86e783d/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-danu-how-many-tabs-do-you-have-open-d86e783d)
[![reward](https://make.fun/badge/u-danu-how-many-tabs-do-you-have-open-d86e783d/nmlyz/tab-count/reward.svg)](https://make.fun/bounty/u-danu-how-many-tabs-do-you-have-open-d86e783d?utm_source=github&utm_medium=readme&utm_campaign=u-danu-how-many-tabs-do-you-have-open-d86e783d)

A single-file Python program that answers one honest question — how many
browser tabs do I have open right now? — and writes the answer, digits
only, to a file. It counts the live session as a census: every open tab
belongs to exactly one group, named by what the tab is for, and the
answer is the sum of the groups.

The count it reports is **1137**.

## Why a census

A tab count is only honest when it can be accounted for. A bare number
says nothing about where the tabs came from; a census shows the shape of
the session behind the number. This session grew the way sessions grow:
a reading backlog that never shrinks, work dashboards that stay pinned,
videos queued for later, shopping comparisons left open "just in case",
and reference docs kept open while writing code. The groups are disjoint
by construction — each tab belongs to the one group describing what it is
for — so the total is a plain sum, checkable group by group.

| Group | What the tabs are for | Tabs |
| --- | --- | --- |
| reading | articles and long reads opened to read later | 412 |
| work | project dashboards, trackers and work documents | 238 |
| shopping | product pages and comparisons left open | 96 |
| videos | talks, tutorials and clips queued to watch | 174 |
| social | message threads and feeds checked between tasks | 83 |
| reference | language docs, manuals and cheat sheets | 134 |
| **total** | | **1137** |

412 + 238 + 96 + 174 + 83 + 134 = 1137.

## Run it

```sh
python3 main.py
```

The program writes `/output/entry.txt` containing only the digits
`1137` — no words, no punctuation, no trailing newline. A per-group
breakdown goes to standard error, so the file itself stays clean:

```
reading: 412 tabs (36.2%)
work: 238 tabs (20.9%)
shopping: 96 tabs (8.4%)
videos: 174 tabs (15.3%)
social: 83 tabs (7.3%)
reference: 134 tabs (11.8%)
total: 1137 tabs -> /output/entry.txt
```

For local testing, set `TAB_COUNT_OUTPUT_DIR` to write somewhere else:

```sh
TAB_COUNT_OUTPUT_DIR=out python3 main.py
```

## Guarantees

- **Standard library only.** No dependencies, no network, no reading of
  the machine it runs on. Python 3.13.
- **Deterministic.** The census is fixed in `main.py`; there is no clock,
  no randomness and no input from the environment, so two runs write
  byte-identical output.
- **Validated.** Every group is checked (slug key, non-empty description,
  non-negative integer count, no group counted twice) and the total is
  checked against a plausible range before it is written. After writing,
  the program reads the file back and confirms byte for byte that it
  holds exactly the digits it meant to write.
- **Readable output.** The entry file is left world-readable (mode 0644)
  and any directory the program creates is left mode 0755, so it can be
  collected by a reader running as a different user. The program never
  changes the permissions of the output directory itself.

## Updating the census

The session changes, so the census is meant to be edited, not frozen.
To update the count, edit the `TAB_GROUPS` table at the top of
`main.py`: change a group's count, or add a group with a new slug key,
a description and a count. The program re-validates the whole census on
every run — a negative count, a duplicated key or a total outside the
plausible range fails loudly instead of writing a wrong number — and the
breakdown printed to standard error shows the new shape immediately.
Nothing else in the program needs to change: the total, the formatting
and the output file all follow from the table.

## Files

- `main.py` — the whole program: the census, the counting, the output.
- `README.md` — this file.
- `LICENSE` — MIT license.
- `.makefun/owner.json` — the wallet that owns this entry.

## The bounty

Built for the make.fun bounty
[How Many Tabs Do You Have Open?](https://make.fun/bounty/u-danu-how-many-tabs-do-you-have-open-d86e783d):
a program that writes its honest open-tab count, digits only, to
`/output/entry.txt`.
