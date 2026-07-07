---
name: blueprint
description: Surface the technical diagrams this kind of project usually benefits from. Educational reminder of the 11 standard blueprint types, not a compliance gate. Use when a developer is unsure what structural diagrams their project needs, or when a mid-stage project feels unmaintainable.
---

# Blueprint Awareness

This skill surfaces **"what you might not know you don't know"** — the 11
standard technical diagrams (4 layers: interaction / architecture / data /
deployment) that projects of different types benefit from. It scans the
project, infers which diagrams are relevant, and reminds the developer they
exist, what pain each solves, and what it looks like.

This is **not** a compliance gate. It does not check whether diagrams were
drawn, does not report severe findings, does not block work. It only pushes
concepts: "your kind of project usually benefits from these diagrams — have
you heard of them?"

## Why it exists

Many projects rot in the middle/late stage not because the code is bad, but
because the developer never learned the names of the structural diagrams that
would have caught the problem early. vibe coding is like building a house by
hand: a small shack needs no blueprint, but a complex building without one
accumulates structural debt that becomes unfixable and un-auditable — like
maintaining pipes in a building with no BIM.

This skill turns "unknown unknowns" into "at least heard of".

## Procedure

1. Scan the project for signals (UI? DB? multiple modules? HTTP API? stateful
   entities? Dockerfile? CI?).
2. From the 11 standard diagrams, infer which ones this project type benefits
   from.
3. For each relevant diagram, output: why it's relevant, what pain it solves,
   a minimal mermaid example, what symptom says you're missing it.
4. Do **not** evaluate whether the diagram was drawn. Do **not** judge
   compliance. Only push concepts.

## Optional script

```bash
python3 scripts/blueprint_check.py --target .
```

Output is a readable report. Add `--json` to get raw signals + relevant list.

## Output

```markdown
## Blueprint Awareness

> 不是合规检查。这些是你这类项目常受益的技术图——你可能没听过名字。

检测信号：<N 个子模块, 有/无 UI, 有/无 DB, ...>

### System Architecture
**为何相关**：<reason>
**解决什么痛**：<one line>
**最小示例**：<mermaid>
**症状**：<how you'd notice it's missing>

### Component Diagram
...

未推荐（信号未命中，未必需要）：<omitted diagrams>
```

## Rules

- Never claim a diagram is "missing" or "required" — only "relevant" or "you
  might benefit from this".
- Never block work. This skill produces zero severe findings and never changes
  an exit code.
- Do not draw the diagrams for the user. Drawing is design work. This skill
  only teaches that the diagrams exist.
- Point to [`references/BLUEPRINT_STANDARD.md`](../../references/BLUEPRINT_STANDARD.md)
  for the full encyclopedia of all 11 diagrams.
- Adapt to the project. A TTS model with no DB should not be told it needs an
  ER diagram. A single-page gradio app should not be told it needs User Flow.

## The 11 diagrams (quick index)

- **Interaction**: User Journey, User Flow, Page Flow
- **Architecture**: System Architecture, Component, Sequence, State Machine
- **Data**: ER Diagram, Data Flow
- **Deployment**: Deployment, CI/CD Pipeline

Details, examples, and "when you don't need it" for each are in
[`references/BLUEPRINT_STANDARD.md`](../../references/BLUEPRINT_STANDARD.md).
