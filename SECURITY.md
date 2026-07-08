# Security

CodeRail is a repo-local governance kit. It should never become a place where secrets, credentials, private customer data, or production incident details are stored casually.

## Supported Versions

The latest release on the default branch receives security fixes.

## Reporting a Vulnerability

Please report suspected security issues privately to the maintainer instead of opening a public issue when the report includes exploit details, secrets, or private repository data.

Include:

- affected version or commit
- affected command, script, template, or skill
- reproduction steps
- expected impact
- suggested fix, if known

## Data Handling

Do not store secrets in:

- `docs/TRACELOG.jsonl`
- `docs/HANDOFF.md`
- `docs/RUNLOG.md`
- `docs/CODERAIL_STATUS.md`
- task contracts, contract drafts, or agent notes

If a trace or handoff needs to refer to sensitive data, use a redacted reference such as `secret:redacted`, `customer:redacted`, or an internal ticket ID.
