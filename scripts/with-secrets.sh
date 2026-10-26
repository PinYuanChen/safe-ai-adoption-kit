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
