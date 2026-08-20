# ADR 0001 — Stack iniziale

- Stato: superata da ADR 0002
- Data: 20 agosto 2026

## Contesto

La specifica richiede versioni esplicite e compatibili per lo starter dell'MVP.

## Decisione

- Python 3.14 e FastAPI 0.140.x.
- SQLAlchemy sincrono 2.x con psycopg 3.
- Angular 22.1, componenti standalone, TypeScript 6.0 e Node.js 24.
- PostgreSQL 18.4.
- Liquibase Community 5.0.3 standalone.
- JSON `camelCase` verso il frontend e `snake_case` nel backend.
- Autenticazione da formalizzare in un ADR dedicato prima dell'implementazione del login.

## Conseguenze

Lo stack privilegia versioni supportate e semplicità operativa. FastAPI non esegue migrazioni al bootstrap; Liquibase rimane un processo separato.
