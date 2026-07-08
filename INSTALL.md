# Install CodeRail

## Local template install

```bash
python3 scripts/init_project.py --target /path/to/repo --mode standard
python3 scripts/doctor.py --target /path/to/repo
python3 scripts/tdd_check.py --target /path/to/repo
python3 scripts/blueprint_check.py --target /path/to/repo
python3 scripts/ci_gate.py --target /path/to/repo
python3 scripts/closeout_check.py --target /path/to/repo --auto-commit
```

## Optional hooks

Copy `examples/hooks.example.json` or `examples/claude/settings.example.json` into your agent configuration and replace `<path-to-coderail>` with the local CodeRail path.

Hooks can:

- remind agents to treat CodeRail as long-lived project rails
- block casual edits to `AGENTS.md`, `CLAUDE.md`, skills, scripts, and references
- periodically run Doctor and Blueprint Gate

## Claude Code

```bash
claude --plugin-dir ./coderail
```

## Codex

Use `.codex-plugin/plugin.json` as the plugin manifest and point the marketplace entry at this package.

## Verify v0.7+ features

```bash
python3 scripts/blueprint_check.py --target /path/to/repo
python3 scripts/hook_guard.py --stage stop --target /path/to/repo --soft
python3 scripts/contract_check.py --target /path/to/repo
python3 scripts/tdd_check.py --target /path/to/repo
python3 scripts/inspect_state.py --target /path/to/repo --write
python3 scripts/done_gate.py --target /path/to/repo --task T-001 --harness-result passed
python3 scripts/ci_gate.py --target /path/to/repo
python3 scripts/closeout_check.py --target /path/to/repo --task T-001 --task-result stage-complete --auto-commit
```
