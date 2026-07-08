# Install CodeRail

## Local template install

```bash
python3 scripts/init_project.py --target /path/to/repo --mode standard
python3 scripts/doctor.py --target /path/to/repo
```

## Claude Code

```bash
claude --plugin-dir ./coderail
```

## Codex

Use `.codex-plugin/plugin.json` as the plugin manifest and point the marketplace entry at this package.

## Verify v0.6 features

```bash
python3 scripts/contract_check.py --target /path/to/repo
python3 scripts/inspect_state.py --target /path/to/repo --write
python3 scripts/done_gate.py --target /path/to/repo --task T-001 --harness-result passed
```
