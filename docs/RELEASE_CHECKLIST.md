# Release Checklist

Use this checklist before publishing a CodeRail release.

## 1. Version

- [ ] Decide the next version using semantic versioning.
- [ ] Update `VERSION`.
- [ ] Update `package.json`.
- [ ] Update `.codex-plugin/plugin.json`.
- [ ] Update `.claude-plugin/plugin.json`.
- [ ] Update README badges and visible version text.

## 2. Changelog

- [ ] Add a `CHANGELOG.md` entry.
- [ ] Include features, fixes, docs, and migration notes.
- [ ] Mention verification commands used for the release.

## 3. Verification

```bash
npm test
python scripts/doctor.py --target project-template
python scripts/contract_check.py --target project-template
python scripts/coordinate_check.py --target project-template
```

## 4. Tag

Create an annotated tag:

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

## 5. GitHub Release

Create a GitHub Release from the tag.

Recommended release title:

```text
vX.Y.Z - Short release name
```

Release notes should include:

- highlights
- compatibility notes
- install command
- verification summary
- links to changed docs

## 6. GitHub Project Surface

- [ ] Check About description.
- [ ] Check topics.
- [ ] Check homepage.
- [ ] Confirm Issues are enabled.
- [ ] Confirm Discussions/Wiki/Projects settings are intentional.
