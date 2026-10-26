.PHONY: install dev dev-fe dev-be init-db seed bootstrap-admin setup-db build lint typecheck test test-fe test-be check-schema clean help

PYTHON ?= py -3.14
NPM ?= npm
POWERSHELL ?= powershell

# ── Colori ──────────────────────────────────────────────────────────────────
CYAN  := \033[0;36m
RESET := \033[0m

help: ## Mostra questo messaggio
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────────────────────
install: ## Installa dipendenze frontend e backend
	@echo "$(CYAN)→ Frontend$(RESET)"
	cd frontend && $(NPM) install
	@echo "$(CYAN)→ Backend$(RESET)"
	cd backend && $(PYTHON) -m pip install -e ".[dev]"
	@echo "$(CYAN)→ Configurazione$(RESET)"
	@test -f .env || cp .env.example .env

# ── Sviluppo ─────────────────────────────────────────────────────────────────
dev: ## Avvia frontend e backend in parallelo
	@trap 'kill 0' INT; \
		(cd frontend && $(NPM) start) & \
		(cd backend && $(PYTHON) -m uvicorn arsis.main:app --reload --port 8000) & \
		wait

dev-fe: ## Avvia solo il frontend
	cd frontend && $(NPM) start

dev-be: ## Avvia solo il backend
	cd backend && $(PYTHON) -m uvicorn arsis.main:app --reload --port 8000

# ── Database ──────────────────────────────────────────────────────────────────
init-db: ## Applica i changeset Liquibase e rigenera il codice backend
	$(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File ./scripts/init-db.ps1

seed: ## Inserisce o aggiorna i dati dimostrativi locali
	$(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File ./scripts/seed-dev.ps1

bootstrap-admin: ## Crea in modo interattivo il primo responsabile
	cd backend && $(PYTHON) -m arsis.auth.bootstrap --email "$(EMAIL)" --display-name "$(NAME)"

setup-db: init-db seed ## Inizializza il database e applica il seed locale

check-schema: ## Verifica changelog e codice generato
	$(POWERSHELL) -NoProfile -ExecutionPolicy Bypass -File ./scripts/init-db.ps1 -ValidateOnly
	$(PYTHON) ./scripts/generate_backend_schema.py --check

# ── Build ────────────────────────────────────────────────────────────────────
build: ## Build di produzione del frontend
	cd frontend && $(NPM) run build

# ── Qualità ──────────────────────────────────────────────────────────────────
lint: ## Esegue Ruff sul backend
	cd backend && $(PYTHON) -m ruff check src tests

typecheck: ## Verifica i tipi del backend
	cd backend && $(PYTHON) -m mypy src/arsis

test: ## Esegui tutti i test
	cd frontend && $(NPM) test
	cd backend && $(PYTHON) -m pytest tests/ -v

test-fe: ## Solo test frontend
	cd frontend && $(NPM) test

test-be: ## Solo test backend
	cd backend && $(PYTHON) -m pytest tests/ -v

# ── Utility ───────────────────────────────────────────────────────────────────
clean: ## Rimuovi artefatti di build e cache
	rm -rf frontend/dist frontend/node_modules/.vite
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
