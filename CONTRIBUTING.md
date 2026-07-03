# Contributing to CodeRail

Thanks for considering a contribution. CodeRail is a governance kit for AI coding agents — small, intentional, and resistant to bloat. This document explains how to contribute in a way that fits the project.

## What we accept

CodeRail welcomes contributions in these areas:

- **New skills** under `skills/` that strengthen the K0–K6 kernel.
- **Scripts** under `scripts/` that automate or check governance (e.g. new `doctor.py`-style validators).
- **Templates** under `project-template/` and `references/`.
- **Bug fixes and documentation** improvements.
- **Examples** under `examples/` (these remain default-off — see below).

## Before you build: the Adoption Gate

CodeRail resists becoming a feature blob. Every new skill, document, or workflow that enters the **default** set must pass the [Adoption Gate](references/ADOPTION_GATE.md). The short version — all five must hold:

1. It strengthens K0–K6.
2. It can be implemented as a command, skill, hook, template, script, or measurable check.
3. It has a clear metric (fewer reopens, fewer forbidden-file violations, higher first-pass harness rate, better handoff success, lower context cost, fewer drift incidents).
4. It does not require users to maintain a new long-lived document by hand unless the benefit is clear.
5. It is default-off unless it is part of the kernel.

The guiding rule: **no new noun without new executable behavior.** If you propose a new concept, it must come with something runnable that enforces or measures it.

If your idea is promising but not yet ready, it can enter as **Watch** or **Adapt** (optional) rather than **Adopt** (default). Open an issue first to discuss where it should land.

## Project structure

```text
skills/<name>/SKILL.md     # one file per skill, YAML frontmatter + body
scripts/                    # python3, stdlib-only, no network
project-template/docs/      # the docs init_project.py copies into a repo
references/                 # the reasoning behind the kernel
examples/                   # default-OFF samples (hooks, permissions)
tests/test_structure.py     # structure self-tests — must stay green
```

## Adding a new skill

1. Create `skills/<your-skill>/SKILL.md`.
2. Start with YAML frontmatter:

   ```yaml
   ---
   name: your-skill
   description: One sentence on when to use it.
   ---
   ```

3. Follow the body pattern of existing skills — see [`skills/align/SKILL.md`](skills/align/SKILL.md) as a reference. Cover: when to use, inputs read, steps performed, output produced.
4. Do not enable any hook or auto-run behavior by default. Examples go under `examples/`.
5. Run the structure tests (below) — they check that your skill has valid frontmatter.

## Development workflow

CodeRail eats its own dog food — feel free to use the kit on the kit itself. In plain terms:

```bash
# 1. Make your change, keeping inside the relevant files
# 2. Run the structure self-tests
python -m pytest tests/ -q            # or: python tests/test_structure.py
# 3. If you touched doctor.py / drift_check.py, sanity-check on a scratch repo
python scripts/init_project.py --target /tmp/scratch --mode standard
python scripts/doctor.py --target /tmp/scratch
# 4. Commit with a clear message
```

The structure tests enforce a few invariants you should know about:

- Every skill must have `name:` and `description:` in its frontmatter.
- Both plugin manifests must exist and point at `./skills/`.
- Runtime files must not contain research-origin terminology — use plain engineering language. This is intentional and tested.

## Commit and pull request

- Keep one logical change per PR.
- Write a commit message that says *what* and *why*, not just *that*.
- If your PR adds or changes governance behavior, note in the PR description which K0–K6 invariant it serves, and whether it targets Watch / Adapt / Adopt.
- If your PR touches a skill, mention if you validated it against the Adoption Gate.

We do not require conventional-commits formatting; clarity matters more than ceremony.

## Scope we will not take

To keep the project honest about what it is (see the README [Boundary](README.md#boundary-what-this-is-not) section):

- A multi-agent orchestrator or role personas (BMAD-style). Out of scope.
- Auto-enabled hooks or any surprising command execution. Contributions here stay under `examples/` and default-off.
- Heavy new long-lived documents that users must maintain by hand without clear benefit.
- Anything that weakens the "no done without harness" rule (K3).

## Licensing

By contributing you agree your contributions are licensed under the project's [MIT license](LICENSE).

## Questions

Open an issue for anything ambiguous. For design questions (especially "should this be a new skill?"), referencing the Adoption Gate upfront speeds things up.
