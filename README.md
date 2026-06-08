# Arsis

Gestionale per scuole di musica — React 18 + FastAPI + MySQL.

## Avvio rapido

### Frontend
```bash
cd frontend
cp .env.example .env
npm install
npm run dev        # http://localhost:5173
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # configura DATABASE_URL
alembic upgrade head       # crea schema DB
uvicorn app.main:app --reload   # http://localhost:8000
```

### Docs API
`http://localhost:8000/docs` (solo in `ENVIRONMENT=development`)

## Struttura
```
arsis/
├── frontend/   React 18 + TypeScript + CSS Modules + Vite
└── backend/    FastAPI + SQLAlchemy 2 async + MySQL
```
