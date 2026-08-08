from test_support import *
from test_support import _lifecycle_env


def _load_owner_modules():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import closeout_facts
    import owner_receipt

    return closeout_facts, owner_receipt


def _zh_delivery() -> dict:
    return {
        "task_status": "finalized",
        "milestone_status": "in_progress",
        "product_status": "not_assessed",
        "customer_outcome": "本地生产命令已可统一编排素材导入、时间线批准和单个渲染任务。",
        "capability_delta": [
            "现在可以导入素材包（Source Bundle）并保存演唱版本",
            "现在可以只读检查本地生产状态",
        ],
        "remaining_gaps": ["尚未验证真实媒体渲染和线上产品界面"],
        "evidence_boundary": ["本地自动化检查全部通过，未运行外部模型"],
        "recommended_next": {
            "id": "REAL-RUN-001",
            "status": "recommended",
            "reason": "用一首真实歌曲完成最小本地实跑",
        },
        "decisions_required": ["是否开始真实歌曲实跑"],
        "technical_receipt": {
            "commits": [],
            "verification": [],
            "safe_files": [],
        },
    }


def _facts(closeout_facts, delivery=None) -> dict:
    return closeout_facts.build(
        task_id="T-037",
        stamp="2026-08-08T10-00-00Z",
        owner_locale="zh-CN",
        delivery=delivery or _zh_delivery(),
        verify_results=[
            {"cmd": "python3 tests/test_cli.py", "exit": 0},
            {"cmd": "git diff --check", "exit": 0},
        ],
        technical_report=".coderail/reports/T-037-closeout.md",
    )


def _worktree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def test_zh_owner_receipt_is_localized_and_within_information_budget():
    closeout_facts, owner_receipt = _load_owner_modules()
    receipt = owner_receipt.render(_facts(closeout_facts), locale="zh-CN")

    check(3 <= owner_receipt.sentence_count(receipt) <= 6, receipt)
    check(owner_receipt.surface_violations(receipt, locale="zh-CN") == [], receipt)
    check("素材包（Source Bundle）" in receipt, receipt)
    for forbidden in (
        "T-037", "REAL-RUN-001", ".coderail/", "test_cli.py", "closeout",
        "commit", "push", "Coordinate", "Drive", "Green", "Red", "marker",
    ):
        check(forbidden not in receipt, receipt)


def test_unlocalized_english_does_not_leak_into_zh_owner_receipt():
    closeout_facts, owner_receipt = _load_owner_modules()
    delivery = _zh_delivery()
    delivery["customer_outcome"] = "Production CLI exact Green is complete."
    delivery["capability_delta"] = ["Import Source Bundle and run one Job"]
    receipt = owner_receipt.render(_facts(closeout_facts, delivery), locale="zh-CN")

    check(owner_receipt.surface_violations(receipt, locale="zh-CN") == [], receipt)
    check("中文产品说明" in receipt, receipt)
    check("Production CLI" not in receipt and "Source Bundle" not in receipt, receipt)


def test_same_closeout_keeps_full_agent_and_technical_facts():
    closeout_facts, owner_receipt = _load_owner_modules()
    facts = _facts(closeout_facts)
    owner = owner_receipt.render(facts, locale="zh-CN")
    technical = closeout_facts.render_technical_report(
        closeout_facts.with_repository_receipt(
            facts,
            commits=["0123456789abcdef"],
            safe_files=["scripts/production-cli.ts", "tests/test_cli.py"],
        )
    )

    check(facts["delivery_id"] in technical, technical)
    for detail in (
        "T-037", ".coderail/reports/T-037-closeout.md", "0123456789abcdef",
        "scripts/production-cli.ts", "python3 tests/test_cli.py", "exit 0",
    ):
        check(detail in technical, technical)
        check(detail not in owner, owner)


def test_delivery_facts_survive_tasks_compaction_and_fresh_clone():
    closeout_facts, _ = _load_owner_modules()
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import coderail

    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as clone_td:
        root = Path(td)
        (root / "docs").mkdir()
        (root / "docs/TASKS.md").write_text(
            "# Tasks\n\n## T-037 Delivered product slice\n\n"
            "Status: [x]\n\n### Delivery Contract\n\n"
            "delivery:\n  customer_outcome: this body will be compacted\n",
            encoding="utf-8",
        )
        (root / "docs/PROGRESS.md").write_text(
            "# Progress\n\n## 2026-08-08 - Delivered product slice (T-037)\n",
            encoding="utf-8",
        )
        (root / "docs/TRACELOG.jsonl").write_text(
            json.dumps({"type": "verify", "task": "T-037", "harness_result": "passed"}) + "\n",
            encoding="utf-8",
        )
        facts = _facts(closeout_facts)
        closeout_facts.append(root, facts)

        _, removed = coderail.compact_persisted_closed_tasks(root)
        check(removed == ["T-037"], removed)
        check("this body will be compacted" not in (root / "docs/TASKS.md").read_text(), "TASKS body survived")
        check(closeout_facts.latest(root)["product"]["customer_outcome"] ==
              _zh_delivery()["customer_outcome"], closeout_facts.latest(root))

        subprocess.check_call(["git", "init", "-q"], cwd=root)
        subprocess.check_call(["git", "config", "user.email", "t@t.io"], cwd=root)
        subprocess.check_call(["git", "config", "user.name", "t"], cwd=root)
        subprocess.check_call(["git", "add", "docs"], cwd=root)
        subprocess.check_call(["git", "commit", "-qm", "fixture"], cwd=root)
        cloned = Path(clone_td) / "fresh"
        subprocess.check_call(["git", "clone", "-q", str(root), str(cloned)])
        rebuilt = closeout_facts.latest(cloned)
        check(rebuilt["delivery_id"] == facts["delivery_id"], rebuilt)
        check(rebuilt["product"] == facts["product"], rebuilt)
        reconstructed = closeout_facts.reconstruct_product_contract(rebuilt)
        for field in (
            "milestone_status", "product_status", "customer_outcome",
            "capability_delta", "remaining_gaps", "evidence_boundary",
            "recommended_next", "decisions_required",
        ):
            check(reconstructed[field] == _zh_delivery()[field], (field, reconstructed))
        check("task_status" not in reconstructed and "technical_receipt" not in reconstructed,
              reconstructed)


def test_inspect_is_agent_blackboard_without_north_star_product_inference():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_inspect_project(target, "", None)
        (target / "docs/NORTH_STAR.md").write_text(
            "# North Star\n\n## Outcome\n\n- aspirational capability that is not verified\n\n"
            "## Current Slice\n\n- planned only\n\n## Drive Contract\n\n- Mode: manual\n",
            encoding="utf-8",
        )
        result = run_inspect(target)
        check(result.returncode == 0, result.stdout + result.stderr)
        check("# CodeRail Agent Blackboard" in result.stdout, result.stdout)
        check("## Owner Product View" not in result.stdout, result.stdout)
        check("Current verified capability" not in result.stdout, result.stdout)
        check("## Current North Star" in result.stdout, result.stdout)


def test_owner_summary_is_a_separate_read_only_surface():
    closeout_facts, _ = _load_owner_modules()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs").mkdir()
        closeout_facts.append(root, _facts(closeout_facts))
        before = _worktree_bytes(root)
        result = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts/coderail.py"), "owner-summary",
                "--locale", "zh-CN", "--target", str(root),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        after = _worktree_bytes(root)

        check(result.returncode == 0, result.stdout)
        check(before == after, "owner-summary changed project files")
        check("# CodeRail Agent Blackboard" not in result.stdout, result.stdout)
        check("T-037" not in result.stdout and ".coderail/" not in result.stdout, result.stdout)


def test_done_zh_projects_owner_receipt_and_persists_agent_receipts():
    closeout_facts, owner_receipt = _load_owner_modules()
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        started = cr("start", "Chinese owner delivery", "--verify", "true")
        check(started.returncode == 0, started.stdout)
        tasks = root / "docs/TASKS.md"
        tasks.write_text(
            tasks.read_text(encoding="utf-8")
            + '''\n### Delivery Contract

delivery:
  task_status: pending
  milestone_status: in_progress
  product_status: not_assessed
  customer_outcome: 本地生产命令已可统一编排素材导入和单个渲染任务
  capability_delta:
    - 现在可以导入素材包（Source Bundle）并保存演唱版本
  remaining_gaps:
    - 尚未验证真实媒体渲染
  evidence_boundary:
    - 本地自动化检查通过，未运行外部模型
  recommended_next:
    id: REAL-RUN-001
    status: recommended
    reason: 用一首真实歌曲完成最小本地实跑
  decisions_required:
    - 是否开始真实歌曲实跑
  technical_receipt:
    commits: []
    verification: []
    safe_files: []
''',
            encoding="utf-8",
        )

        result = cr("done", "--owner-locale", "zh-CN")
        check(result.returncode == 0, result.stdout)
        check(owner_receipt.surface_violations(result.stdout, locale="zh-CN") == [], result.stdout)
        check("本次完成" in result.stdout and "现在可以" in result.stdout, result.stdout)
        check("== Done:" not in result.stdout and "T-001" not in result.stdout, result.stdout)

        facts = closeout_facts.latest(root)
        check(facts["agent_receipt"]["source_task"] == "T-001", facts)
        technical_reports = list((root / ".coderail/reports").glob("delivery-*.md"))
        check(len(technical_reports) == 1, technical_reports)
        technical = technical_reports[0].read_text(encoding="utf-8")
        check("T-001" in technical and "true" in technical and "exit 0" in technical, technical)
        inspect = cr("inspect", "--no-write")
        check("# CodeRail Agent Blackboard" in inspect.stdout, inspect.stdout)
        check(facts["delivery_id"] in inspect.stdout, inspect.stdout)
        check(not subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"], text=True
        ).strip(), "closeout left tracked residue")


def test_done_zh_rejects_owner_unsafe_copy_before_lifecycle_mutation():
    closeout_facts, _ = _load_owner_modules()
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        started = cr("start", "Unsafe owner copy", "--verify", "true")
        check(started.returncode == 0, started.stdout)
        tasks = root / "docs/TASKS.md"
        tasks.write_text(
            tasks.read_text(encoding="utf-8")
            + '''\n### Delivery Contract

delivery:
  task_status: pending
  milestone_status: in_progress
  product_status: not_assessed
  customer_outcome: Production CLI closeout 已完成
  capability_delta:
    - 可以查看完整治理事实
  remaining_gaps:
    - none
  evidence_boundary:
    - 本地检查通过
  recommended_next:
    id: null
    status: none
    reason: 由所有者决定
  decisions_required: []
  technical_receipt:
    commits: []
    verification: []
    safe_files: []
''',
            encoding="utf-8",
        )
        head_before = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()

        result = cr("done", "--owner-locale", "zh-CN")
        check(result.returncode == 1, result.stdout)
        check("面向所有者的中文产品说明不符合要求" in result.stdout, result.stdout)
        check("T-001" not in result.stdout and ".coderail/" not in result.stdout, result.stdout)
        check("Status: [~]" in tasks.read_text(encoding="utf-8"), tasks.read_text())
        check(closeout_facts.latest(root) == {}, closeout_facts.latest(root))
        head_after = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
        check(head_after == head_before, (head_before, head_after))


if __name__ == "__main__":
    run_module(globals())
