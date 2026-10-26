#!/usr/bin/env bash
# Runs a command with API keys loaded from the macOS Keychain, so keys never
# live in files, shell history, or the repo.
#
# One-time setup (you will be prompted for the key; it is not echoed):
#   security add-generic-password -a "$USER" -s safe-ai-kit/anthropic-api-key -w
#
# Usage:
#   scripts/with-secrets.sh uv run python -m kit.agent
set -euo pipefail

# API calls cost money and expose the key to the child process, so only a
# human runs this. Claude Code sets CLAUDECODE=1 in the shells it starts.
if [[ -n "${CLAUDECODE:-}" ]]; then
  echo "Refusing to load API keys inside a Claude Code session. Run this yourself in a terminal." >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "usage: $0 <command> [args...]" >&2
  exit 64
fi

if ! ANTHROPIC_API_KEY="$(security find-generic-password -a "$USER" -s safe-ai-kit/anthropic-api-key -w 2>/dev/null)"; then
  echo "No key in Keychain under service 'safe-ai-kit/anthropic-api-key'. See the setup line at the top of this script." >&2
  exit 1
fi
export ANTHROPIC_API_KEY

exec "$@"
