#!/usr/bin/env bash

# Keep errexit enabled while placing each black-box invocation in an if branch;
# a failed item is recorded and the next independent verification still runs.
set -Eeuo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:9090}"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
export BACKEND_URL ADMIN_USERNAME
# Export only a meaningful override. An explicitly empty value must be removed
# so the existing Python scripts can use their documented admin/123456 fallback.
if [[ -n "${ADMIN_PASSWORD:-}" ]]; then
  export ADMIN_PASSWORD
else
  unset ADMIN_PASSWORD
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_URL="${BACKEND_URL%/}/dashboard"
CHECK_TIMEOUT="${DEMO_BACKEND_TIMEOUT:-10}"

printf 'Backend verification target: %s\n' "$BACKEND_URL"
printf 'Health check: %s\n' "$CHECK_URL"

if ! curl --fail --silent --show-error --max-time "$CHECK_TIMEOUT" "$CHECK_URL" >/dev/null; then
  printf 'ERROR: backend is unavailable at %s\n' "$CHECK_URL" >&2
  printf 'Start Docker/backend first, or set BACKEND_URL to a reachable service.\n' >&2
  exit 2
fi
printf 'Health check: PASS\n\n'

SCRIPT_NAMES=(
  verify_circulation_http.py
  verify_inventory_http.py
  verify_overdue_http.py
  verify_user_management_http.py
)
SCRIPT_LABELS=(
  'circulation (6/6)'
  'inventory (9/9)'
  'overdue (6/6)'
  'user management (7/7)'
)
RESULT_CODES=()

run_check() {
  local index="$1"
  local script="${SCRIPT_NAMES[$index]}"
  local label="${SCRIPT_LABELS[$index]}"
  local code

  printf '===== %s: %s =====\n' "$((index + 1))/${#SCRIPT_NAMES[@]}" "$label"
  if [[ ! -f "$ROOT_DIR/$script" ]]; then
    printf 'FAIL %s - script not found: %s\n' "$label" "$ROOT_DIR/$script" >&2
    code=127
  elif BACKEND_URL="$BACKEND_URL" ADMIN_USERNAME="$ADMIN_USERNAME" \
    python3 "$ROOT_DIR/$script"; then
    code=0
    printf 'PASS %s (exit 0)\n' "$label"
  else
    code=$?
    printf 'FAIL %s (exit %s); continuing with the next check\n' "$label" "$code" >&2
  fi
  RESULT_CODES+=("$code")
  printf '\n'
}

for index in "${!SCRIPT_NAMES[@]}"; do
  run_check "$index"
done

failures=0
printf '===== Backend verification summary =====\n'
for index in "${!SCRIPT_NAMES[@]}"; do
  code="${RESULT_CODES[$index]}"
  if [[ "$code" == 0 ]]; then
    printf 'PASS  %s  (exit %s)\n' "${SCRIPT_LABELS[$index]}" "$code"
  else
    printf 'FAIL  %s  (exit %s)\n' "${SCRIPT_LABELS[$index]}" "$code"
    failures=$((failures + 1))
  fi
done

if [[ "$failures" == 0 ]]; then
  printf 'TOTAL PASS: all %s backend checks passed; temporary test data was cleaned by each script.\n' "${#SCRIPT_NAMES[@]}"
  exit 0
fi

printf 'TOTAL FAIL: %s/%s backend checks failed.\n' "$failures" "${#SCRIPT_NAMES[@]}" >&2
exit 1
