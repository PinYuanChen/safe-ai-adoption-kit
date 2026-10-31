# Safe AI Adoption Kit

A reference kit showing how a traditional company can adopt AI safely: a multi-agent assistant with least-privilege subagents, an AI gateway, a permission-aware internal assistant, an evaluation and red-team suite, and an adoption checklist. Uses a fictional trading company and synthetic data only.

## Components (build order)
1. Agent loop with tool use on the Anthropic SDK (Python, no framework)
2. Multi-agent orchestrator (Python): hands work to subagents through an explicit handoff format, gives each subagent only the tools it needs, and keeps running when one subagent fails
3. Evaluation and red-team suite: answer quality, agent trajectories (wrong tool, wasted turns, runaway loops), plus prompt injection, exfiltration, and permission-bypass tests; grows with each later component
4. Telemetry: OpenTelemetry traces with tokens, cost, latency, tool calls; single-agent versus multi-agent and model cost-versus-accuracy comparisons
5. AI gateway (Go): secret/PII redaction, per-user budgets, audit log; the only component that holds the API key
6. Internal knowledge assistant (Python): permission-aware retrieval as a read-only subagent, human approval for write actions
7. Adoption checklist and write-up (`docs/`)

## Stack
- Python managed with `uv` (lockfile committed); Go modules with `go.sum` committed
- Models: claude-haiku-5-5 for cheap, high-volume steps; claude-sonnet-5-5 / claude-opus-5-5 where accuracy matters

## Learning mode
I am learning applied AI engineering through this project. Lessons live in `~/learn-applied-ai`; do not write anything there.
- **I write these myself:** the agent loop, the orchestrator's handoff and subagent tool scoping, tool definitions and tool-selection logic, the gateway's redaction and budget logic, retrieval and permission filtering, and eval scoring.
- **Claude may write:** boilerplate, CLI scaffolding, test fixtures and synthetic data, Dockerfiles, CI config, and docs formatting.
- When I ask for a review, explain *why* something is risky or wrong instead of only giving the fix.

## Security rules
- Never put secrets in code, config, commits, or chat. Secrets live in the macOS Keychain and are injected at run time by `scripts/with-secrets.sh`, which only I run (it refuses to start inside Claude Code). Claude Code works with mocked LLM clients; real API runs are mine.
- `.env*` files and key files must never be read or created with real values; `.env.example` holds names only.
- Use synthetic data only. Never add real personal or company data to the repo, prompts, or evals.
- Code that processes untrusted content (documents, red-team payloads) runs in a Docker container with no secrets mounted and no network access unless a test needs it.
- Add dependencies only after checking the exact package name and maintainer; pin versions through the lockfiles. Do not add MCP servers or skills from unknown sources.
- gitleaks runs as a pre-commit hook (`.githooks/pre-commit`) and again on every push in CI (`.github/workflows/secret-scan.yml`). Do not bypass either.
- `.claude/hooks/guard-bash.sh` blocks Bash commands that touch secret files, the Keychain, `with-secrets.sh`, or the pre-commit hook. `.claude/` and `.githooks/` are not editable by Claude Code; I change them by hand.
