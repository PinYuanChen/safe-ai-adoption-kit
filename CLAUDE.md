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

## Learning notes (`notes/`)
When I say "記筆記" or ask to record what I didn't understand, write it here (Claude may write these; it is docs, not project code).
- Layout: `notes/index.html` is the learning timeline (one card per lesson); `notes/lesson-NN-<slug>/` holds that lesson's `index.html` and its notes. Lesson N matches Component N and the lesson of the same number in `~/learn-applied-ai/lessons/` (read it for the title; never write there).
- Notes are numbered globally (`0011-<slug>.html` continues after `0010`) and never renumbered or deleted; mark an outdated note's status pill as 「已取代」 and link the replacement.
- Each note follows the existing ADR-style format: one-line summary, 背景 (what confused me), 觀念 (inline SVG diagrams using the classes in `notes/style.css`), 踩雷紀錄, 相關筆記, prev/next pager. Traditional Chinese, technical terms in English, light and humorous, based only on what actually came up.
- When adding notes: update the lesson's `index.html` (note list and timeline entry with the date), and when starting a new lesson, add its folder and turn its card in `notes/index.html` from `todo` into a linked card.
- Check that every relative link resolves, then show me the result before committing.

## Verifying claims
- Before stating how an external system behaves (Anthropic API, SDKs, libraries, tools, prices, limits), check its official docs in this session. In notes and reviews, link the page and quote the sentence the claim rests on.
- Label every such claim as one of: documented (with link), observed (with the log or command), or inference. If it was not checked, say "unverified" instead of stating it as fact.
- A passing test or a successful call proves only what it exercised. Say what it did not prove.
- Before saying a component or lesson is done, check it against the lesson's checklist in `~/learn-applied-ai/lessons/` and this file, and list anything missing. Do not treat the session's plan as the definition of done.

## Security rules
- Never put secrets in code, config, commits, or chat. Secrets live in the macOS Keychain and are injected at run time by `scripts/with-secrets.sh`, which only I run (it refuses to start inside Claude Code). Claude Code works with mocked LLM clients; real API runs are mine.
- `.env*` files and key files must never be read or created with real values; `.env.example` holds names only.
- Use synthetic data only. Never add real personal or company data to the repo, prompts, or evals.
- Code that processes untrusted content (documents, red-team payloads) runs in a Docker container with no secrets mounted and no network access unless a test needs it.
- Add dependencies only after checking the exact package name and maintainer; pin versions through the lockfiles. Do not add MCP servers or skills from unknown sources.
- gitleaks runs as a pre-commit hook (`.githooks/pre-commit`) and again on every push in CI (`.github/workflows/secret-scan.yml`). Do not bypass either.
- `.claude/hooks/guard-bash.sh` blocks Bash commands that touch secret files, the Keychain, `with-secrets.sh`, or the pre-commit hook. `.claude/` and `.githooks/` are not editable by Claude Code; I change them by hand.
