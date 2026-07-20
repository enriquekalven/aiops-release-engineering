---
name: zero2hero-release
description: Automates the end-to-end productionization and release of AI Agents using AIOps quality gates.
---

# Skill: Zero2Hero Autonomous Release

## Rationalizations

| Excuse | Rebuttal |
| :--- | :--- |
| Manual releases are fine for small agent updates. | Manual releases are error-prone and miss instruction erosion drift. Automation ensures persona and capability gates are met every time. |
| Running the drift simulation takes too long. | Skipping drift checks leads to prompt leaks and instruction erosion in production. |
| I can just update the version in one place. | Version drift between dependencies and package metadata causes deployment failures. |

## Verification

- Verify that `ai-ops preflight` passes perfectly.
- Verify that the Drift Test Gate score is >= 4.0/5.0.
- Verify that `CHANGELOG.md` is appended with AI-generated notes.
- Verify that the signed `.ai-ops/release_certificate.txt` is generated.

## Instructions for Release Execution

When executing the Zero2Hero release skill, follow these phase-gate instructions:

### Phase 1: Preparation & Preflight
1. **Run Preflight**: `ai-ops preflight`.
2. **Version Alignment**: Run `ai-ops bump` to derive and sync the next patch version.
3. **AI Changelog**: Ensure `GEMINI_API_KEY` is present to generate the AI Release Notes.

### Phase 2: Structural Verification (The Build Gates)
4. **Code Drift Snapshot**: (Optional) Run `ai-ops snapshot` to update the attestation baseline if functional changes are intentional.
5. **Code Drift Check**: Run `ai-ops code-drift`.
6. **Persona Drift Test**: Run `ai-ops drift` to execute the multi-turn dialogue simulation.
7. **Regression Suite**: Run `pytest`.

### Phase 3: Deployment & Publishing
8. **Build Distribution**: Run `uv build`.
9. **Git Tag**: Commit changes, create a git tag `v[VERSION]`, and push.
10. **Publish**: Run `uv publish` (requires `PYPI_TOKEN`).

### Promptfoo Integration

Embed this skill in your repository's `.ai-ops` configuration to gate deployment on semantic correctness using [Promptfoo](https://github.com/promptfoo/promptfoo).
