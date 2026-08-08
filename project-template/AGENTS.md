# CodeRail

<!-- coderail:gates coordinate,contract,tdd,inspect,closeout,done -->
<!-- Managed marker (kept by init/upgrade): certifies gate coverage to doctor. -->

This project uses CodeRail to keep AI-assisted work on track. The rules below
are written in plain language. You do not need to learn any special terminology.

One principle governs everything here: **spec is the output, not the input**.
The user explores and discovers what they want by building; your job is to help
them converge — each verified task, recorded decision, and learned boundary
becomes a constraint the next round of work must respect. Never demand an
upfront specification from the user, and never violate what has already been
ratified in `docs/`.

## The three commands

There is one entry point with three everyday commands:

```bash
python .coderail/coderail.py start "what you want to do"   # begin a task
python .coderail/coderail.py check                         # am I on track?
python .coderail/coderail.py done --owner-locale en        # finish safely
```

Everything else (verification gates, history tracing, safe commits, handoff
notes) happens automatically behind these three commands.

Make commitments machine-checkable at `start` whenever you can:
`--verify "npm test"` (done RUNS it; non-zero exit blocks closing),
`--tests "tests/x.test.ts"` (done warns if absent from the diff),
`--accept "item"` (done requires done|deferred per item),
`--id T-186` (your task id, kept consistent everywhere).
A task closed without `--verify` is permanently marked UNVERIFIED in the
progress journal. Register real checks.

## Before you write any code

1. Read `docs/NORTH_STAR.md` — the project goal in one page. If it is empty,
   ask the user what they are building and write it down first.
2. Read `docs/TASKS.md` — what is in flight right now.
3. Run `git status` — know what is already changed.
4. With no active task, run `start`. To change owners, run `switch`; `--force`
   never permits multiple active tasks.

## While you work

- Only touch files the current task said it would touch. If you need to go
  outside that list, say so and update the task — do not do it silently.
- If the request is vague, big, or risky (payments, auth, data deletion,
  schema changes), write down what you plan to do in `docs/CONTRACTS.md` and
  get a yes before coding.
- For bug fixes and logic-heavy code, write a failing test first, then make
  it pass. Record that in the task.
- Record important decisions in `docs/DECISIONS.md` (one line is enough:
  what you decided and why).

## Before you say "done"

Never declare a task finished from memory. Run:

```bash
python .coderail/coderail.py done --owner-locale zh-CN  # Chinese conversation
```
Use `--owner-locale en` for English; CodeRail never guesses the owner language or falls back to the retired report.

It runs verification, checks scope and docs, then commits only safe task files.
A successful `done` already authorizes that exact local commit. Do not ask the
user for separate commit approval after every gate passes. Use `--no-commit`
only when the user explicitly asks to review before committing; failed gates,
unsafe scope, or sensitive files block. A local commit never authorizes
push, tag, or release. For task changes use `switch`; use `--checkpoint` only
after a verifiable partial boundary.

## After "done": report in plain language (non-negotiable)

The user may not read code or technical docs. After every finished task,
your closing message to them MUST answer exactly three questions, in the
user's own language, in 3-6 sentences total:

1. **What can you see or do now that you couldn't before?**
2. **How do I know it works?** (what was actually checked, said plainly)
3. **What's next — and do you need to decide anything?**

Rules: no file paths, tool names, governance jargon, or task IDs unless asked;
in Chinese, annotate any necessary English term in Chinese parentheses; decisions
must be clear either/or questions; never paste raw command output at the user.

The localized `done` output is the Owner Receipt. Full lifecycle, verification,
path, and Git facts stay in the Agent Blackboard and Technical Report. The
append-only `docs/DELIVERIES.jsonl` preserves product evidence, not lifecycle.

## When the tool says "Step back"

`check` and `done` watch for circling: the same task failing repeatedly, the
same file changing commit after commit, or multiple blocked tasks. The
`== Step back ==` notice is a hard signal, not a suggestion:

- **"Is the design of this module right?"** — stop patching; propose a
  structural change to the user before attempting another fix.
- **"Is this the right thing to build at all?"** — stop coding; re-read
  `docs/NORTH_STAR.md`, explain the tension plainly, let the user decide.

When repeated fixing does not converge, the bug is almost never at the level
where you are fixing — it lives one level up, in design or in the requirement.

## When the tool says "Blueprints"

`check` and `done` watch the codebase shape; when it grows a new layer they
list the diagrams now needed (4 layers / 11 classes). When you see the notice,
run `python .coderail/coderail.py blueprint --scaffold` — it creates Mermaid
stubs under `docs/blueprints/`, marked `planned` in `docs/BLUEPRINTS.md`.
Replace placeholders with the REAL structure (small enough that a newcomer
understands without guesswork), then set the row to `current`. When a change
invalidates a diagram, mark it `stale` in the same commit. Diagrams are
ratified from what was built — never drawn ahead of the code.

## Honesty rules (non-negotiable)

- Do not claim tests passed if you did not run them.
- Do not mark a task done if the finish command failed.
- Do not quietly expand a task into unrelated files.
- Do not use `git add .` — the finish command stages only safe files.

## When you come back to a project

On resume, read `docs/HANDOFF.md` and the Agent Blackboard in
`docs/CODERAIL_STATUS.md`, then run read-only `coderail inspect`. Preview updates with `coderail sync-projections`;
only `--apply` writes. Stale prose never blocks formulation or activates work.
Advanced commands are listed by `python .coderail/coderail.py --help`.
