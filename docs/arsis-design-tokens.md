# Arsis — Design Tokens

> Versione 1.1 · Giugno 2026  
> Tutti i token sono CSS custom properties definite su `:root` con override per `[data-theme="dark"]`.  
> In React, il tema viene applicato via `document.documentElement.setAttribute('data-theme', theme)`.  
> **v1.1** — palette brand aggiornata al verde del logo ufficiale (#1D9E75).

---

## 1. Brand

Il brand color di Arsis è verde, derivato dal logo ufficiale. Il colore primario `#1D9E75` è l'ancora di tutta la palette accent.

| Token | Valore (light) | Hex equivalente | Significato |
|---|---|---|---|
| `--arsis-hue` | `160` | — | Hue base del brand. Modificare solo questo per spostare l'intera palette accent. |
| `--color-accent` | `hsl(160, 68%, 36%)` | `#1D9E75` | Colore primario. Pulsanti, link attivi, focus ring, indicatore nav attivo. |
| `--color-accent-soft` | `hsl(160, 55%, 94%)` | `#E6F6F0` | Sfondo soft per badge, selezioni, hover leggeri. |
| `--color-accent-hover` | `hsl(160, 70%, 28%)` | `#0F6E56` | Stato hover per elementi accent. Anche colore profondo sidebar. |

**Dark override**

| Token | Valore (dark) | Note |
|---|---|---|
| `--color-accent` | `hsl(160, 58%, 48%)` | Più luminoso per contrasto su sfondo scuro |
| `--color-accent-soft` | `hsla(160, 58%, 48%, .14)` | Trasparente invece di tinta chiara |
| `--color-accent-hover` | `hsl(160, 60%, 56%)` | |

### Palette logo completa (riferimento, non token)

I colori del logo non diventano token CSS ma sono documentati qui come riferimento per uso in contesti di brand (splash screen, export, stampa).

| Nome | Hex | Uso nel logo |
|---|---|---|
| Verde primario | `#1D9E75` | Fill cerchio `arsis_logo_full`, tratto `arsis_logo_icon` |
| Verde scuro | `#0F6E56` | Stroke cerchio `arsis_logo_icon`, sfondo sidebar light |
| Verde profondo | `#085041` | Fill rettangolo `arsis_logo_white` (uso su sfondo scuro) |
| Verde chiaro anello | `#5DCAA5` | Stroke anello `arsis_logo_background` |
| Verde tenue onda | `#9FE1CB` | Tratto onda `arsis_logo_background` |
| Grafite | `#2C2C2A` | Tutto `arsis_logo_mono` (uso monocromatico) |

### Varianti logo disponibili

| File | Uso consigliato |
|---|---|
| `arsis_logo_full.svg` | Cerchio pieno verde, tratto bianco — favicon, avatar app |
| `arsis_logo_icon.svg` | Cerchio con bordo, tratto verde — brand mark sidebar light |
| `arsis_logo_white.svg` | Sfondo scuro rettangolare, tratto bianco — splash, email header |
| `arsis_logo_mono.svg` | Tutto grafite — stampa, contesti monocromatici |
| `arsis_logo_background.svg` | Variante con doppio anello — illustrazioni, sfondi decorativi |

**Uso in sidebar:** inline SVG di `arsis_logo_icon` con tratto rimappato a `white` su sfondo `--sidebar-bg`.

---

## 2. Semantici — Status

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--color-success` | `hsl(152, 60%, 36%)` | — | Testo/icona stato positivo |
| `--color-success-soft` | `hsl(152, 55%, 94%)` | `hsla(152, 60%, 36%, .18)` | Sfondo badge "pagato", "attivo" |
| `--color-warn` | `hsl(36, 90%, 44%)` | — | Scadenze imminenti, alert medi |
| `--color-warn-soft` | `hsl(36, 90%, 94%)` | `hsla(36, 90%, 44%, .16)` | Sfondo badge "in scadenza" |
| `--color-danger` | `hsl(0, 65%, 50%)` | — | Errori, rate scadute, eliminazione |
| `--color-danger-soft` | `hsl(0, 65%, 95%)` | `hsla(0, 65%, 50%, .16)` | Sfondo badge "scaduto", alert banner |

> **Nota:** i valori `hsl()` per success, warn e danger non cambiano tra light e dark — cambia solo il soft (da tinta piena a trasparenza).

> **Nota:** `--color-success` e `--color-accent` sono intenzionalmente vicini (entrambi verdi). Si distinguono per saturazione e lightness: accent è più saturo e scuro, success è più tenue. Non mescolarli nella stessa riga UI.

---

## 3. Superfici

Le superfici formano una gerarchia di elevazione a 4 livelli. Il canvas ha una leggerissima tinta verde (`hsl(160, 14%, 97%)`) per coerenza con il brand.

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--bg-canvas` | `hsl(160, 14%, 97%)` | `hsl(160, 16%, 8%)` | Sfondo della pagina (body) |
| `--bg-surface` | `hsl(0, 0%, 100%)` | `hsl(160, 14%, 11%)` | Card, topbar, pannello dettaglio |
| `--bg-raised` | `hsl(160, 12%, 96%)` | `hsl(160, 12%, 15%)` | thead, footer card, hover righe tabella, input background |
| `--bg-overlay` | `hsl(160, 10%, 93%)` | `hsl(160, 10%, 19%)` | Hover secondari, progress bar track, separatori visivi |

---

## 4. Bordi

I bordi usano hue 160 (verde) invece di 220 (blu) per coerenza cromatica sottile.

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--border-subtle` | `hsla(160, 14%, 10%, .08)` | `hsla(160, 14%, 100%, .05)` | Divisori interni, bordi card (quasi invisibili) |
| `--border-default` | `hsla(160, 14%, 10%, .14)` | `hsla(160, 14%, 100%, .10)` | Bordi input, select, pulsanti secondary |
| `--border-strong` | `hsla(160, 14%, 10%, .28)` | `hsla(160, 14%, 100%, .22)` | Hover su input, separatori importanti |

---

## 5. Testo

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--text-primary` | `hsl(160, 18%, 8%)` | `hsl(160, 12%, 93%)` | Testo principale, titoli, valori |
| `--text-secondary` | `hsl(160, 10%, 36%)` | `hsl(160, 8%, 60%)` | Label, sottotitoli, descrizioni |
| `--text-tertiary` | `hsl(160, 8%, 52%)` | `hsl(160, 6%, 42%)` | Metadata, hint, date, placeholder leggero |
| `--text-disabled` | `hsl(160, 6%, 72%)` | `hsl(160, 4%, 28%)` | Stato disabilitato, timestamp secondari |
| `--text-inverse` | `hsl(0, 0%, 100%)` | `hsl(160, 18%, 8%)` | Testo su sfondo accent (es. pulsante primary) |

---

## 6. Sidebar

La sidebar usa una palette separata derivata dal logo: verde scuro profondo `#085041` in light mode, ancora più scuro in dark.

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--sidebar-bg` | `hsl(160, 42%, 10%)` | `hsl(160, 42%, 6%)` | Sfondo sidebar (~`#085041` light, più scuro in dark) |
| `--sidebar-text` | `hsl(160, 14%, 60%)` | `hsl(160, 12%, 48%)` | Nav item default, label sezioni |
| `--sidebar-active` | `hsl(0, 0%, 100%)` | `hsl(0, 0%, 100%)` | Nav item attivo/hover, nome utente |
| `--sidebar-hover` | `hsla(160, 20%, 100%, .07)` | `hsla(160, 20%, 100%, .06)` | Hover background nav item |
| `--sidebar-border` | `hsla(160, 20%, 100%, .08)` | `hsla(160, 20%, 100%, .06)` | Divisori interni sidebar |

---

## 7. Ombre

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--shadow-xs` | `0 1px 2px hsla(160,20%,10%,.06)` | `0 1px 2px hsla(0,0%,0%,.25)` | Card a riposo, elementi flat |
| `--shadow-sm` | `0 1px 4px hsla(160,20%,10%,.08), 0 0 0 1px hsla(160,20%,10%,.04)` | `0 1px 4px hsla(0,0%,0%,.30), 0 0 0 1px hsla(160,14%,100%,.04)` | Card hover, pulsanti primary hover |
| `--shadow-md` | `0 4px 16px hsla(160,20%,10%,.10), 0 0 0 1px hsla(160,20%,10%,.05)` | `0 4px 16px hsla(0,0%,0%,.35), 0 0 0 1px hsla(160,14%,100%,.06)` | Dropdown, pannelli |
| `--shadow-lg` | `0 16px 48px hsla(160,20%,10%,.18)` | `0 16px 48px hsla(0,0%,0%,.55)` | Modal, overlay panels |

---

## 8. Tipografia

### Font families

| Token | Valore | Ruolo |
|---|---|---|
| `--font-sans` | `'DM Sans', sans-serif` | Corpo, UI, label, pulsanti |
| `--font-display` | `'Fraunces', serif` | Titoli pagina, metriche numeriche, greeting |
| `--font-mono` | `'DM Mono', monospace` | Valori monetari, date, codici fiscali, percentuali |

### Scale dimensioni

| Token | Valore | Uso tipico |
|---|---|---|
| `--text-xs` | `11px` | Label sezioni sidebar, badge, hint |
| `--text-sm` | `13px` | Corpo UI, nav item, td, input |
| `--text-base` | `15px` | Testo corpo principale |
| `--text-lg` | `17px` | Titolo topbar |
| `--text-xl` | `22px` | Brand name sidebar |
| `--text-2xl` | `28px` | Titoli sezione |
| `--text-3xl` | `38px` | Metriche dashboard (font-display) |

### Pesi

| Token | Valore |
|---|---|
| `--weight-regular` | `400` |
| `--weight-medium` | `500` |
| `--weight-semi` | `600` |

---

## 9. Spaziatura

Base grid: **4px**. Tutti i valori sono multipli interi.

| Token | Valore | Uso tipico |
|---|---|---|
| `--sp-1` | `4px` | Gap micro, margin-top badge dot |
| `--sp-2` | `8px` | Gap tra elementi inline, padding badge |
| `--sp-3` | `12px` | Padding nav item, gap icon+label |
| `--sp-4` | `16px` | Padding pulsanti, padding card compatta |
| `--sp-5` | `20px` | Padding card standard |
| `--sp-6` | `24px` | Padding modal header/body, padding brand |
| `--sp-8` | `32px` | Padding topbar, padding content area |
| `--sp-10` | `40px` | Margin bottom dashboard header |
| `--sp-12` | `48px` | Margin bottom sezioni design system |
| `--sp-16` | `64px` | Spaziature extra-large (raro) |

---

## 10. Border Radius

| Token | Valore | Uso |
|---|---|---|
| `--radius-sm` | `4px` | Input inline add-row, tag rate |
| `--radius-md` | `8px` | Pulsanti, input, nav item, brand mark |
| `--radius-lg` | `12px` | Card standard, table-wrap, kpi |
| `--radius-xl` | `18px` | Modal, course card, detail empty icon |
| `--radius-full` | `999px` | Badge, avatar, chip, progress bar |

---

## 11. Transizioni

| Token | Valore | Uso |
|---|---|---|
| `--ease` | `cubic-bezier(.16, 1, .3, 1)` | Easing default — rapido in uscita, decelerazione naturale |
| `--duration-fast` | `120ms` | Hover, color change, opacity |
| `--duration-base` | `200ms` | Transizioni tema, apertura panel |
| `--duration-slow` | `350ms` | Animazioni più percepibili (progress bar fill) |

---

## 12. Colori corso (costanti JS, non token CSS)

Ogni corso ha un colore identificativo scelto dall'amministratore. I valori vivono nell'array `COURSE_COLORS` nel frontend, non come token CSS, perché sono dati applicativi non di tema.

| Nome | Hex | Light background |
|---|---|---|
| Blu | `#378ADD` | `#EBF3FC` |
| Verde | `#1D9E75` | `#E6F6F0` |
| Arancio | `#D85A30` | `#FAEEE9` |
| Ambra | `#BA7517` | `#F7EDD9` |
| Viola | `#7F77DD` | `#EEEDF9` |
| Teal | `#2BA8A0` | `#E4F4F3` |
| Rosa | `#C2507A` | `#F7E8EF` |
| Grafite | `#5A6572` | `#EAEEF1` |

---

## 13. Colori avatar (classi CSS)

Gli avatar delle persone usano classi predefinite invece di stili inline, per garantire coerenza.

| Classe | Background |
|---|---|
| `.av-blue` | `hsl(220, 70%, 52%)` |
| `.av-green` | `hsl(152, 55%, 38%)` |
| `.av-amber` | `hsl(36, 80%, 46%)` |
| `.av-rose` | `hsl(340, 65%, 50%)` |
| `.av-violet` | `hsl(262, 65%, 54%)` |
| `.av-teal` | `hsl(175, 60%, 38%)` |
| `.av-orange` | `hsl(20, 80%, 48%)` |
| `.av-slate` | `hsl(210, 25%, 45%)` |

---

## 14. CSS completo — `tokens.css`

Blocco pronto da copiare in `src/styles/tokens.css`:

```css
:root {
  /* Font */
  --font-sans:    'DM Sans', sans-serif;
  --font-display: 'Fraunces', serif;
  --font-mono:    'DM Mono', monospace;

  /* Type scale */
  --text-xs:   11px; --text-sm:   13px; --text-base: 15px; --text-lg: 17px;
  --text-xl:   22px; --text-2xl:  28px; --text-3xl:  38px;

  /* Weight */
  --weight-regular: 400; --weight-medium: 500; --weight-semi: 600;

  /* Spacing */
  --sp-1: 4px;  --sp-2: 8px;   --sp-3: 12px; --sp-4: 16px;
  --sp-5: 20px; --sp-6: 24px;  --sp-8: 32px; --sp-10: 40px;
  --sp-12: 48px; --sp-16: 64px;

  /* Radius */
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px;
  --radius-xl: 18px; --radius-full: 999px;

  /* Ease */
  --ease: cubic-bezier(.16, 1, .3, 1);
  --duration-fast: 120ms; --duration-base: 200ms; --duration-slow: 350ms;

  /* Brand */
  --arsis-hue: 160;
  --color-accent:       hsl(160, 68%, 36%);
  --color-accent-soft:  hsl(160, 55%, 94%);
  --color-accent-hover: hsl(160, 70%, 28%);

  /* Status */
  --color-success:      hsl(152, 60%, 36%);
  --color-success-soft: hsl(152, 55%, 94%);
  --color-warn:         hsl(36,  90%, 44%);
  --color-warn-soft:    hsl(36,  90%, 94%);
  --color-danger:       hsl(0,   65%, 50%);
  --color-danger-soft:  hsl(0,   65%, 95%);

  /* Shadows */
  --shadow-xs: 0 1px 2px hsla(160,20%,10%,.06);
  --shadow-sm: 0 1px 4px hsla(160,20%,10%,.08), 0 0 0 1px hsla(160,20%,10%,.04);
  --shadow-md: 0 4px 16px hsla(160,20%,10%,.10), 0 0 0 1px hsla(160,20%,10%,.05);
  --shadow-lg: 0 16px 48px hsla(160,20%,10%,.18);
}

[data-theme="light"] {
  --bg-canvas:  hsl(160, 14%, 97%);
  --bg-surface: hsl(0, 0%, 100%);
  --bg-raised:  hsl(160, 12%, 96%);
  --bg-overlay: hsl(160, 10%, 93%);

  --border-subtle:  hsla(160, 14%, 10%, .08);
  --border-default: hsla(160, 14%, 10%, .14);
  --border-strong:  hsla(160, 14%, 10%, .28);

  --text-primary:   hsl(160, 18%, 8%);
  --text-secondary: hsl(160, 10%, 36%);
  --text-tertiary:  hsl(160,  8%, 52%);
  --text-disabled:  hsl(160,  6%, 72%);
  --text-inverse:   hsl(0, 0%, 100%);

  --sidebar-bg:     hsl(160, 42%, 10%);
  --sidebar-text:   hsl(160, 14%, 60%);
  --sidebar-active: hsl(0, 0%, 100%);
  --sidebar-hover:  hsla(160, 20%, 100%, .07);
  --sidebar-border: hsla(160, 20%, 100%, .08);
}

[data-theme="dark"] {
  --bg-canvas:  hsl(160, 16%, 8%);
  --bg-surface: hsl(160, 14%, 11%);
  --bg-raised:  hsl(160, 12%, 15%);
  --bg-overlay: hsl(160, 10%, 19%);

  --border-subtle:  hsla(160, 14%, 100%, .05);
  --border-default: hsla(160, 14%, 100%, .10);
  --border-strong:  hsla(160, 14%, 100%, .22);

  --text-primary:   hsl(160, 12%, 93%);
  --text-secondary: hsl(160,  8%, 60%);
  --text-tertiary:  hsl(160,  6%, 42%);
  --text-disabled:  hsl(160,  4%, 28%);
  --text-inverse:   hsl(160, 18%, 8%);

  --color-accent:       hsl(160, 58%, 48%);
  --color-accent-soft:  hsla(160, 58%, 48%, .14);
  --color-accent-hover: hsl(160, 60%, 56%);

  --color-success-soft: hsla(152, 60%, 36%, .18);
  --color-warn-soft:    hsla(36,  90%, 44%, .16);
  --color-danger-soft:  hsla(0,   65%, 50%, .16);

  --shadow-xs: 0 1px 2px hsla(0,0%,0%,.25);
  --shadow-sm: 0 1px 4px hsla(0,0%,0%,.30), 0 0 0 1px hsla(160,14%,100%,.04);
  --shadow-md: 0 4px 16px hsla(0,0%,0%,.35), 0 0 0 1px hsla(160,14%,100%,.06);
  --shadow-lg: 0 16px 48px hsla(0,0%,0%,.55);

  --sidebar-bg:     hsl(160, 42%, 6%);
  --sidebar-text:   hsl(160, 12%, 48%);
  --sidebar-active: hsl(0, 0%, 100%);
  --sidebar-hover:  hsla(160, 20%, 100%, .06);
  --sidebar-border: hsla(160, 20%, 100%, .06);
}
```
