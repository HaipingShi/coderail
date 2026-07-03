# Security Policy

## Supported versions

CodeRail is a plugin and template kit, not a long-running service. We provide
security fixes for the latest released version only.

| Version | Supported |
|---------|-----------|
| latest `0.x` | ✅ |
| older `0.x` | ❌ upgrade recommended |

## Reporting a vulnerability

If you find a security vulnerability, **please do not open a public issue.**

Instead, report it privately:

1. Open a **private security advisory** on GitHub:
   [github.com/HaipingShi/coderail/security/advisories/new](https://github.com/HaipingShi/coderail/security/advisories/new)
2. Or email the maintainer via the email on the GitHub profile.

Please include:
- A clear description of the issue and its potential impact.
- Steps to reproduce, or a proof of concept.
- Which file(s) or skill(s) are affected.

We will acknowledge receipt within **72 hours** and aim to send an initial
assessment within **7 days**.

## Security model and scope

CodeRail is designed to be safe by default. Understanding the model helps you
report in-scope issues:

**In scope:**
- Any default-on behavior that executes commands the user did not authorize.
- A skill or script that writes, deletes, or overwrites files outside its
  documented contract (e.g. `init_project.py` overwriting a non-empty file
  despite the documented "no overwrite" guarantee).
- Prompts or skill text that instruct the agent to bypass the user's
  permissions, hooks, or review gates.
- Secrets or private keys committed to this repository.

**Out of scope (by design):**
- CodeRail ships **no active hooks by default**. The files under `examples/`
  (e.g. `hooks.example.json`, permission configs) are samples and are not
  executed unless you explicitly enable them. Misuse of sample hooks after you
  enable them is a configuration issue, not a CodeRail vulnerability.
- CodeRail does not run a server, open ports, or accept network input. It is
  local files and stdlib-only Python scripts with no network access.
- CodeRail cannot control what your AI agent chooses to do. It provides prompts,
  templates, and checks — the agent's actual behavior is governed by your host
  tool's permissions and hooks (K4, tool-native enforcement). That is the
  stronger layer and is out of CodeRail's control.

## Guidance for hook contributors

If you contribute a hook or example that executes commands, it must remain
default-off and live under `examples/`. Any contribution that enables
command execution by default will be rejected — see
[`CONTRIBUTING.md`](CONTRIBUTING.md#scope-we-will-not-take).
