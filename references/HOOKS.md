# Hooks & Tool-Native Enforcement Guide

CodeRail's rules in `AGENTS.md` are **soft** — they rely on the agent reading
and obeying them. When a rule can be enforced harder by the agent's host tool
(permissions, hooks, CI, pre-commit), that is stronger and preferred. This is
K4 Tool-Native Enforcement.

**CodeRail ships no active hooks by default.** Everything here is opt-in. This
file explains what you *can* wire up and what you *should not*.

## CodeRail's stance (do not change)

- Default-off. The plugin never installs hooks or deny rules automatically.
- Examples only. `examples/` contains templates you review and copy.
- Soft > hard > blocking. Use the lightest enforcement that works; escalate only when drift is recurring.

See [`TOOL_NATIVE_ENFORCEMENT.md`](TOOL_NATIVE_ENFORCEMENT.md) for the principle.

## Three enforcement layers (from soft to hard)

| Layer | Mechanism | Strength | When to use |
|---|---|---|---|
| Prompt | `AGENTS.md` rules | soft (agent may ignore) | Always — the baseline. |
| Permissions deny | Claude Code `settings.json` `permissions.deny` | hard (edit blocked) | Protecting L1 governance files from being rewritten. |
| Hooks / pre-commit | `examples/hooks.example.json` or `.git/hooks/pre-commit` | hard (action blocked / commit blocked) | Periodic drift correction; commit gates. |

## What to protect with `permissions.deny` (L1 layer)

Copy from [`examples/claude/settings.example.json`](../examples/claude/settings.example.json).
This stops the agent from editing CodeRail's own governance files unless the user
explicitly upgrades CodeRail:

- `references/**`, `skills/**`, `scripts/**` — the plugin body
- `.claude-plugin/**`, `.codex-plugin/**` — manifests
- `AGENTS.md` — the runtime entry point's governance sections
- `docs/TRACELOG.jsonl` — append-only; editing past lines corrupts the trace graph
- plus your project's own forbidden paths (`migrations/**`, `.env`, etc.)

See the **Governance Layering** section of `AGENTS.md` for what L1/L2/L3 mean.

## What to wire as hooks / pre-commit

### Soft reminders (Claude Code hooks, `PostToolUse` / `Stop`)

These surface information; they never block. Copy from
[`examples/hooks.example.json`](../examples/hooks.example.json):

- **After Write/Edit**: remind to write a trace event for non-trivial changes.
- **At turn end (`Stop`)**: print a short `doctor.py` summary so drift does not
  accumulate silently across turns.

### Hard gates (git pre-commit, not Claude Code hooks)

These block the commit. Use selectively — only enable the ones matching your
risk tolerance:

- **`coordinate_check.py`** — block commit if any active/doing/done task is
  missing G/V/P fields. Catches "coded without a coordinate."
- **`drift_check.py`** — block commit if drift is detected (orphan tasks, done
  without verify trace, HANDOFF references unrecorded outcomes). Catches
  "the work drifted from the North Star."

## What NOT to wire as a gate

These are intentionally soft. Blocking on them misfires:

- **`blueprint_check.py`** — educational reminder of which technical diagrams
  your project type usually benefits from. Blocking on "missing diagrams"
  would fire on every new project and violates its non-judgmental design. It
  appears only inside `doctor.py`'s Blueprint Awareness section.
- **`doctor.py`** — a read-only health report, not a gate. Its findings are
  warnings (status: "usable with warnings"), not failures. Never exit-1 a
  commit on doctor output.

## How to enable

**Claude Code permissions (L1 protection):**
Copy the `permissions.deny` block from
`examples/claude/settings.example.json` into your Claude Code settings.

**Claude Code hooks (soft reminders):**
Copy the `hooks` block from `examples/hooks.example.json` into your settings,
adjusting paths to your CodeRail install.

**Git pre-commit (hard gates):**
Create `.git/hooks/pre-commit` with the commands from the `pre_commit_examples`
section of `examples/hooks.example.json`. Or use a pre-commit framework
(`pre-commit`, `husky`) referencing the same scripts.

## The point

Without hooks, CodeRail relies on the agent obeying `AGENTS.md` — which works
until it doesn't. Hooks and deny rules are the backstop for when the agent is
distracted, lazy, or "helpfully" rewriting things it shouldn't. Wire the minimum
that catches your actual failure modes; do not enable everything by default.
