#!/usr/bin/env bash
# PreToolUse guard for Bash. Permission rules match command prefixes, so this
# hook inspects the whole command line and blocks anything that could read
# secrets, load API keys, or skip the secret scan, wherever it appears.
set -euo pipefail

cmd="$(jq -r '.tool_input.command // empty')"

block() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

shopt -s nocasematch
case "$cmd" in
  *.env*|*.pem*|*.p12*|*id_rsa*|*id_ed25519*|*/.ssh*|*/.aws*|*Keychains*)
    block "Blocked: command references a secret file (.env, key, ~/.ssh, ~/.aws or Keychain). Ask the user to run it." ;;
  *security\ *find-*|*security\ *dump-keychain*|*security\ *export*)
    block "Blocked: reading the macOS Keychain is not allowed from Claude Code." ;;
  *with-secrets*)
    block "Blocked: commands that load API keys are run by the user, not by Claude Code." ;;
  *--no-verify*|*--no-ver*|*core.hookspath*|*.githooks*|*git_config*|*.gitleaks*)
    block "Blocked: skipping or changing the secret scan is not allowed." ;;
  *.claude/settings*|*.claude/hooks*|*.github/workflows*)
    block "Blocked: Claude Code settings, hooks and CI workflows are changed by the user, not through Bash." ;;
esac
shopt -u nocasematch

# git commit -n is the short form of --no-verify (also catches combined flags like -an).
if [[ "$cmd" =~ (^|[[:space:];&|])git([[:space:]]+-[^[:space:]]+)*[[:space:]]+commit([[:space:]]+[^[:space:]]+)*[[:space:]]+-[a-zA-Z]*n ]]; then
  block "Blocked: git commit -n skips the pre-commit secret scan."
fi

exit 0
