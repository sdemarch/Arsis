.PHONY: install dev build lint test migrate clean help

# ── Colori ──────────────────────────────────────────────────────────────────
CYAN  := \033[0;36m
RESET := \033[0m

help: ## Mostra questo messaggio
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────────────────────
install: ## Installa dipendenze frontend e backend
	@echo "$(CYAN)→ Frontend$(RESET)"
	cd frontend && npm install
	@echo "$(CYAN)→ Backend$(RESET)"
	cd backend && uv sync
	@echo "$(CYAN)→ Copia .env se non esistono$(RESET)"
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	@test -f backend/.env  || cp backend/.env.example  backend/.env

# ── Sviluppo ─────────────────────────────────────────────────────────────────
dev: ## Avvia frontend e backend in parallelo
	@trap 'kill 0' INT; \
		(cd frontend && npm run dev) & \
		(cd backend && uv run uvicorn app.main:app --reload --port 8000) & \
		wait

dev-fe: ## Avvia solo il frontend
	cd frontend && npm run dev

dev-be: ## Avvia solo il backend
	cd backend && uv run uvicorn app.main:app --reload --port 8000

# ── Database ──────────────────────────────────────────────────────────────────
migrate: ## Applica le migrazioni Alembic
	cd backend && uv run alembic upgrade head

migration: ## Crea una nuova migrazione (usa: make migration MSG="descrizione")
	cd backend && uv run alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback di una migrazione
	cd backend && uv run alembic downgrade -1

# ── Build ────────────────────────────────────────────────────────────────────
build: ## Build di produzione del frontend
	cd frontend && npm run build

# ── Qualità ──────────────────────────────────────────────────────────────────
lint: ## Lint frontend (ESLint) e backend (ruff)
	cd frontend && npm run lint
	cd backend && uv run ruff check app

test: ## Esegui tutti i test
	cd frontend && npm run test -- --run
	cd backend && uv run pytest tests/ -v

test-fe: ## Solo test frontend
	cd frontend && npm run test -- --run

test-be: ## Solo test backend
	cd backend && uv run pytest tests/ -v

# ── Utility ───────────────────────────────────────────────────────────────────
clean: ## Rimuovi artefatti di build e cache
	rm -rf frontend/dist frontend/node_modules/.vite
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
