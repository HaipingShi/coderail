#!/usr/bin/env node
const { spawnSync } = require("node:child_process");

const candidates = [
  { cmd: "python", prefix: [] },
  { cmd: "python3", prefix: [] },
  { cmd: "py", prefix: ["-3"] },
];

function isPython(result) {
  const output = `${result.stdout || ""}${result.stderr || ""}`;
  return result.status === 0 && /^Python\s+\d+\.\d+/m.test(output);
}

function findPython() {
  for (const candidate of candidates) {
    const result = spawnSync(candidate.cmd, [...candidate.prefix, "--version"], {
      encoding: "utf8",
      windowsHide: true,
    });
    if (isPython(result)) {
      return candidate;
    }
  }
  return null;
}

const python = findPython();
if (!python) {
  console.error("error: could not find a working Python interpreter");
  process.exit(127);
}

const result = spawnSync(python.cmd, [...python.prefix, ...process.argv.slice(2)], {
  stdio: "inherit",
  windowsHide: true,
});

if (result.error) {
  console.error(`error: ${result.error.message}`);
  process.exit(127);
}
process.exit(result.status ?? 1);
