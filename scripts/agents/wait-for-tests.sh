#!/usr/bin/env bash
# Poll gh pr checks until tests* are green, failed, or timeout.
# Outputs: GITHUB_OUTPUT ci_ok=true|false; on failure writes /tmp/ci-fail-name.txt
set -euo pipefail
PR="${1:?PR number}"

echo "Waiting for checks on PR #$PR…"
for i in $(seq 1 60); do
  json=$(gh pr checks "$PR" --json name,state,bucket)
  verdict=$(printf '%s' "$json" | python3 -c '
import json, sys
checks = json.loads(sys.stdin.read() or "[]")
tests = [c for c in checks if str(c.get("name", "")).startswith("tests")]
if not tests:
    print("pending")
    raise SystemExit
failed, unfinished = [], []
for c in tests:
    bucket = (c.get("bucket") or "").lower()
    name = c.get("name") or "tests"
    if bucket in ("pass", "skipping"):
        continue
    if bucket in ("fail", "cancel"):
        failed.append(name)
        continue
    unfinished.append(name)
if failed:
    print("failed:" + ",".join(failed))
elif unfinished:
    print("pending")
else:
    print("green")
')
  echo "poll $i: $verdict"
  case "$verdict" in
    green)
      echo "ci_ok=true" >> "${GITHUB_OUTPUT:-/dev/null}"
      echo "ci_ok=true"
      exit 0
      ;;
    failed:*)
      echo "ci_ok=false" >> "${GITHUB_OUTPUT:-/dev/null}"
      echo "${verdict#failed:}" | cut -d, -f1 > /tmp/ci-fail-name.txt
      echo "ci_ok=false"
      exit 0
      ;;
  esac
  sleep 20
done
echo "ci_ok=false" >> "${GITHUB_OUTPUT:-/dev/null}"
echo "tests-timeout" > /tmp/ci-fail-name.txt
echo "ci_ok=false"
