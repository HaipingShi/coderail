# Adoption Gate

No new noun without executable behavior. New ideas must map to a command, script, template, check, or hook.

## Unborn Git baseline

Use `coderail start "Adopt project baseline" --adopt-baseline --files "src/**" ...` only before the repository has a first commit. CodeRail records the pre-adoption path set with Git status, SHA-256 fingerprints, and an allowed/outside/forbidden disposition. It never stores contents and never stages the repository wholesale.

At `done`, the closeout preflight re-evaluates the current worktree. Explicitly allowed safe files, including files installed by CodeRail when named in scope, may enter the task commit. Sensitive files block closure with exact paths. Unchanged outside baseline, ignored local dependencies, and generated artifacts remain unstaged.
