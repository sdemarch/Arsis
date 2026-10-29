# ADR 0004 — Autenticazione e sessioni

- Stato: accettato
- Data: 26 ottobre 2026

## Contesto

Arsis è una SPA Angular con API FastAPI e installazione on-premise. Gli endpoint di
dominio devono essere accessibili soltanto a un responsabile attivo, senza esporre
credenziali o token persistenti a JavaScript.

## Decisione

- Le password sono salvate esclusivamente come hash Argon2id tramite `pwdlib`.
- Il login restituisce un access token JWT HS256 con durata breve. Il frontend lo
  conserverà soltanto in memoria e lo invierà come Bearer token.
- Il refresh token è opaco, casuale e salvato nel browser come cookie `HttpOnly`,
  `SameSite=Lax`; in produzione è anche `Secure`. Nel database ne viene conservato
  soltanto l'hash SHA-256.
- Ogni refresh revoca il token precedente e ne emette uno nuovo. Il logout revoca
  la sessione corrente e cancella il cookie.
- Ogni richiesta autenticata rilegge l'utente dal database, così disattivazione e
  archiviazione hanno effetto immediato.
- Il primo responsabile viene creato esclusivamente con comando locale interattivo.
  Il comando rifiuta l'operazione non appena esiste un utente.
- Health check, login, refresh e logout sono pubblici; gli endpoint applicativi
  richiedono un utente attivo.

## Conseguenze

Il server mantiene revocabili le sessioni lunghe senza memorizzare access token.
Gli access token già emessi restano validi al massimo fino alla loro breve scadenza,
ma l'utente viene comunque verificato sul database a ogni richiesta. Prima della
pubblicazione su reti non fidate restano obbligatori HTTPS e rate limiting a livello
di reverse proxy o applicazione.
