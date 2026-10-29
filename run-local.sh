#!/usr/bin/env bash
# Start Arsis either in development mode or through the packaged-style local runtime.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-4200}"
ARSIS_MODE="${ARSIS_MODE:-development}"
LOCAL_RUNTIME_PORT="${LOCAL_RUNTIME_PORT:-8765}"

if command -v py >/dev/null 2>&1; then
  PYTHON=(py -3.14)
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=(python3)
else
  echo "Python 3.14 non trovato. Installarlo oppure rendere disponibile il comando 'py'." >&2
  exit 1
fi

for command in npm "${PYTHON[0]}"; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Comando richiesto non trovato: $command" >&2
    exit 1
  fi
done

if [[ ! -d "$ROOT_DIR/frontend/node_modules" ]]; then
  echo "Dipendenze frontend assenti. Eseguire: cd frontend && npm install" >&2
  exit 1
fi

if ! (
  cd "$ROOT_DIR/backend"
  "${PYTHON[@]}" -c "import uvicorn"
); then
  echo "Dipendenze backend assenti. Eseguire: cd backend && ${PYTHON[*]} -m pip install -e '.[dev]'" >&2
  exit 1
fi

if [[ ! -f "$ROOT_DIR/data/arsis.db" ]]; then
  echo "Database assente. Inizializzarlo prima con: ./scripts/init-db.ps1" >&2
  exit 1
fi

if [[ "$ARSIS_MODE" == "runtime" ]]; then
  echo "Compilazione frontend per il runtime locale"
  (
    cd "$ROOT_DIR/frontend"
    npm run build
  )
  echo "Avvio runtime locale: http://127.0.0.1:${LOCAL_RUNTIME_PORT}"
  cd "$ROOT_DIR/backend"
  exec "${PYTHON[@]}" -c "from arsis.local_runtime import main; main()" --port "$LOCAL_RUNTIME_PORT"
fi

if [[ "$ARSIS_MODE" != "development" ]]; then
  echo "Modalita non supportata: $ARSIS_MODE (usare development o runtime)" >&2
  exit 1
fi

cleanup() {
  trap - EXIT INT TERM
  kill "${BACKEND_PID:-}" "${FRONTEND_PID:-}" 2>/dev/null || true
  wait "${BACKEND_PID:-}" "${FRONTEND_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Avvio backend:  http://localhost:${BACKEND_PORT}"
(
  cd "$ROOT_DIR/backend"
  exec "${PYTHON[@]}" -m uvicorn arsis.main:app --reload --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

echo "Avvio frontend: http://localhost:${FRONTEND_PORT}"
(
  cd "$ROOT_DIR/frontend"
  exec npm start -- --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

wait -n "$BACKEND_PID" "$FRONTEND_PID"
exit $?
