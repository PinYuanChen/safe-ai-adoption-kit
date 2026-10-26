# Safe AI Adoption Kit

A reference kit showing how a traditional company can adopt AI safely: an AI gateway, a permission-aware internal assistant, an evaluation and red-team suite, and an adoption checklist. Uses a fictional trading company and synthetic data only.

## Components (build order)
1. Agent loop with tool use on the Anthropic SDK (Python, no framework)
2. AI gateway (Go): secret/PII redaction, per-user budgets, audit log; the only component that holds the API key
3. Internal knowledge assistant (Python): permission-aware RAG, human approval for write actions
4. Evaluation and red-team suite: quality evals plus prompt injection, exfiltration, and permission-bypass tests
5. Telemetry: OpenTelemetry traces with tokens, cost, latency, tool calls; model cost-versus-accuracy comparison
6. Adoption checklist and write-up (`docs/`)

## Stack
- Python managed with `uv` (lockfile committed); Go modules with `go.sum` committed
- Models: claude-haiku-5-5 for cheap, high-volume steps; claude-sonnet-5-5 / claude-opus-5-5 where accuracy matters

## Learning mode
I am learning applied AI engineering through this project. Lessons live in `~/learn-applied-ai`; do not write anything there.
- **I write these myself:** the agent loop, tool definitions and tool-selection logic, the gateway's redaction and budget logic, retrieval and permission filtering, and eval scoring.
- **Claude may write:** boilerplate, CLI scaffolding, test fixtures and synthetic data, Dockerfiles, CI config, and docs formatting.
- When I ask for a review, explain *why* something is risky or wrong instead of only giving the fix.

## Security rules
- Never put secrets in code, config, commits, or chat. Secrets live in the macOS Keychain and are injected at run time by `scripts/with-secrets.sh`.
- `.env*` files and key files must never be read or created with real values; `.env.example` holds names only.
- Use synthetic data only. Never add real personal or company data to the repo, prompts, or evals.
- Code that processes untrusted content (documents, red-team payloads) runs in a Docker container with no secrets mounted and no network access unless a test needs it.
- Add dependencies only after checking the exact package name and maintainer; pin versions through the lockfiles. Do not add MCP servers or skills from unknown sources.
- gitleaks runs as a pre-commit hook (`.githooks/pre-commit`). Do not bypass it with `--no-verify`.
