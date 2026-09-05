#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
git fetch -q origin

while IFS= read -r LINE; do
  SLUG=$(sed -E 's/^- \[ \] ([a-z0-9-]+):.*/\1/' <<< "$LINE")
  if git branch -a | grep -q "task/$SLUG\$"; then continue; fi
  TASK=$(sed -E 's/^- \[ \] [a-z0-9-]+: *//' <<< "$LINE")
  echo "→ $SLUG"
  exec openclaw agent --agent site \
    --session-key "agent:site:task-$SLUG-$(date +%s)" \
    --timeout 1200 \
    -m "Tarefa '$SLUG': $TASK"
done < <(grep '^- \[ \] ' BACKLOG.md || true)

echo "Nada a fazer."
