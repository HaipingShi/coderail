# Install

## Claude Code

```bash
claude --plugin-dir ./coderail
```

Then run:

```text
/coderail:project-init
```

Claude Code plugin skills are namespaced as `/coderail:<skill>`.

## Codex

For a repo-scoped marketplace:

```bash
mkdir -p ./plugins ./ .agents/plugins
cp -R /path/to/coderail ./plugins/coderail
cp examples/codex/marketplace.example.json .agents/plugins/marketplace.json
```

Restart Codex and open the plugin browser.

## Generic

```bash
python3 coderail/scripts/init_project.py --target /path/to/repo --mode standard
python3 coderail/scripts/doctor.py --target /path/to/repo
```
