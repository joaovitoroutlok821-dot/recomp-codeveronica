#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/common.sh"

IGNORE_STAMP=false
LOG_LEVEL=info
for arg in "$@"; do
  case "$arg" in
    --ignore-stamp|force) IGNORE_STAMP=true ;;
    --trace) LOG_LEVEL=trace ;;
    normal|linux-*) ;;
    *) recvx_die "usage: RECVX_XEX_PATH=/path/to/Default.xex ./scripts/codegen.sh [--ignore-stamp] [--trace]" ;;
  esac
done

# The manifest expects game/Default.xex. Allow the user's own copy to remain
# outside the repository and stage a temporary, ignored copy for codegen.
STAGED_XEX="$RECVX_ROOT/game/Default.xex"
CREATED_XEX_COPY=false
if [[ -n "${RECVX_XEX_PATH:-}" ]]; then
  [[ -f "$RECVX_XEX_PATH" ]] || recvx_die "RECVX_XEX_PATH is not a file: $RECVX_XEX_PATH"
  mkdir -p -- "$RECVX_ROOT/game"
  if [[ -e "$STAGED_XEX" ]]; then
    recvx_die "game/Default.xex already exists; refusing to overwrite it"
  fi
  cp -- "$RECVX_XEX_PATH" "$STAGED_XEX"
  CREATED_XEX_COPY=true
fi
cleanup_staged_xex() {
  if [[ "$CREATED_XEX_COPY" == true ]]; then
    rm -f -- "$STAGED_XEX"
  fi
}
trap cleanup_staged_xex EXIT

recvx_verify_xex
recvx_verify_sdk
recvx_prepare_logs
CODEGEN_LOG="$RECVX_ROOT/logs/codegen-$(recvx_timestamp).log"
printf 'Codegen log: %s\n' "$CODEGEN_LOG"

ARGS=(--log-level "$LOG_LEVEL" --log-file "$CODEGEN_LOG" codegen)
if [[ "$IGNORE_STAMP" == true ]]; then
  ARGS+=(--ignore-stamp)
fi
ARGS+=("$RECVX_MANIFEST")

cd "$RECVX_ROOT"
"$RECVX_REXGLUE_CLI" "${ARGS[@]}"
