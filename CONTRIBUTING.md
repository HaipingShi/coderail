# Contributing

Thanks for helping improve CodeRail.

CodeRail should stay small, repo-local, and easy for an agent to follow. New concepts must map to at least one concrete artifact:

- a command
- a script
- a template
- a skill
- a validator
- a documented check

## Development Loop

1. Keep changes focused.
2. Update docs when behavior changes.
3. Add or update tests for scripts and validators.
4. Run:

```bash
npm test
```

5. For template behavior, also run:

```bash
python scripts/doctor.py --target project-template
```

## Pull Requests

Good pull requests include:

- what changed
- why it changed
- how it was verified
- any compatibility or migration notes

## Design Principles

- Prefer Markdown and standard-library Python.
- Prefer repo-local state over hosted services.
- Prefer explicit checks over prompt-only rules.
- Keep entry files short and push detail into `references/`.
- Do not add a runtime loop, database, queue, or server unless the project scope intentionally changes.
