#!/usr/bin/env bash
# Runs a command with API keys loaded from the macOS Keychain, so keys never
# live in files, shell history, or the repo.
#
# One-time setup (you will be prompted for the key; it is not echoed). -T ""
# trusts no app, so macOS shows a Keychain password dialog every time the key
# is read; a shell or agent cannot answer that dialog for you:
#   security add-generic-password -a "$USER" -s safe-ai-kit/anthropic-api-key -T "" -w
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

# Environment variables can be changed by the caller, so also require a human
# at a real terminal to confirm. Agent shells have no controlling terminal.
if ! { exec 3<>/dev/tty; } 2>/dev/null; then
  echo "Refusing to load API keys without an interactive terminal." >&2
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

printf 'Load the Anthropic API key and run: %s ? [y/N] ' "$*" >&3
read -r answer <&3
exec 3>&-
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
  echo "Cancelled." >&2
  exit 1
fi
export ANTHROPIC_API_KEY

exec "$@"
