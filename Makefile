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
	cd backend && python -m venv venv && \
		. venv/bin/activate && pip install -r requirements.txt
	@echo "$(CYAN)→ Copia .env se non esistono$(RESET)"
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	@test -f backend/.env  || cp backend/.env.example  backend/.env

# ── Sviluppo ─────────────────────────────────────────────────────────────────
dev: ## Avvia frontend e backend in parallelo
	@trap 'kill 0' INT; \
		(cd frontend && npm run dev) & \
		(cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000) & \
		wait

dev-fe: ## Avvia solo il frontend
	cd frontend && npm run dev

dev-be: ## Avvia solo il backend
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

# ── Database ──────────────────────────────────────────────────────────────────
migrate: ## Applica le migrazioni Alembic
	cd backend && . venv/bin/activate && alembic upgrade head

migration: ## Crea una nuova migrazione (usa: make migration MSG="descrizione")
	cd backend && . venv/bin/activate && alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback di una migrazione
	cd backend && . venv/bin/activate && alembic downgrade -1

# ── Build ────────────────────────────────────────────────────────────────────
build: ## Build di produzione del frontend
	cd frontend && npm run build

# ── Qualità ──────────────────────────────────────────────────────────────────
lint: ## Lint frontend (ESLint) e backend (ruff se disponibile)
	cd frontend && npm run lint
	cd backend && . venv/bin/activate && \
		(command -v ruff > /dev/null && ruff check app || echo "ruff non installato, skip")

test: ## Esegui tutti i test
	cd frontend && npm run test -- --run
	cd backend && . venv/bin/activate && pytest tests/ -v

test-fe: ## Solo test frontend
	cd frontend && npm run test -- --run

test-be: ## Solo test backend
	cd backend && . venv/bin/activate && pytest tests/ -v

# ── Utility ───────────────────────────────────────────────────────────────────
clean: ## Rimuovi artefatti di build e cache
	rm -rf frontend/dist frontend/node_modules/.vite
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
