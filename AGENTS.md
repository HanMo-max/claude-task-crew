# Repository instructions

This repository publishes portable Claude Code templates. Files under `templates/project/` are distribution assets, not active configuration for this repository.

Keep routing guidance in the distributed `opus-orchestrator/SKILL.md`. Keep `CLAUDE.md` as an import of canonical `AGENTS.md`; do not duplicate policy text. Preserve the distinction between role defaults and per-invocation model/effort overrides.

Run `python3 scripts/check_bundle.py` after changes. State runtime checks separately from static validation. Do not add credentials, account settings, local installation paths, customer data, runtime transcripts or unverified cost/quality claims.
