import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'arsis-login-page',
  imports: [RouterLink],
  template: `
    <main class="login-layout">
      <section class="login-brand" aria-label="Arsis">
        <div class="brand-lockup">
          <img src="assets/brand/arsis-logo-background.svg" alt="" />
          <strong>Arsis</strong>
        </div>
        <div class="brand-message">
          <p class="eyebrow">Banda e Orchestra</p>
          <h1>La musica, organizzata<br />con semplicità.</h1>
          <p>Persone, attività e scuola di musica in un unico spazio condiviso.</p>
        </div>
        <p class="brand-footnote">Arsis | by Stefano Demarchi | 2026</p>
      </section>

      <section class="login-panel">
        <form class="login-card">
          <div>
            <p class="eyebrow">Bentornato</p>
            <h2>Accedi ad Arsis</h2>
            <p class="intro">Inserisci username e password.</p>
          </div>
          <label>
            <span>Email</span>
            <input type="email" value="responsabile@arsis.it" autocomplete="email" />
          </label>
          <label>
            <span>Password</span>
            <input type="password" value="password" autocomplete="current-password" />
          </label>
          <a class="button button--primary button--large" routerLink="/home">Accedi</a>
          <p class="help">Problemi di accesso? Contatta l’amministratore.</p>
        </form>
      </section>
    </main>
  `,
  styles: `
    :host { display: block; min-height: 100vh; }
    .login-layout { display: grid; grid-template-columns: minmax(420px, 46%) 1fr; min-height: 100vh; }
    .login-brand { background: var(--sidebar-bg); color: var(--sidebar-active); display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; padding: var(--sp-10); position: relative; }
    .login-brand::after { border: 60px solid color-mix(in srgb, var(--color-accent) 35%, transparent); border-radius: var(--radius-full); content: ''; height: 360px; position: absolute; right: -150px; top: 24%; width: 360px; }
    .brand-lockup { align-items: center; display: flex; font-family: var(--font-display); font-size: var(--text-login); gap: var(--sp-4); position: relative; z-index: 1; }
    .brand-lockup img { display: block; height: var(--logo-login-size); width: var(--logo-login-size); }
    .brand-message { max-width: 560px; position: relative; z-index: 1; }
    .eyebrow { color: var(--color-accent); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .12em; margin: 0 0 var(--sp-3); text-transform: uppercase; }
    .brand-message h1 { font-size: 48px; margin: 0 0 var(--sp-5); }
    .brand-message > p:last-child { color: var(--sidebar-text); font-size: var(--text-lg); max-width: 440px; }
    .brand-footnote { color: var(--sidebar-text); margin: 0; position: relative; z-index: 1; }
    .login-panel { align-items: center; background: var(--bg-canvas); display: flex; justify-content: center; padding: var(--sp-8); }
    .login-card { display: grid; gap: var(--sp-6); max-width: 420px; width: 100%; }
    .login-card h2 { font-size: var(--text-2xl); margin: 0 0 var(--sp-2); }
    .intro, .help { color: var(--text-secondary); margin: 0; }
    label { display: grid; font-size: var(--text-sm); font-weight: var(--weight-medium); gap: var(--sp-2); }
    input { background: var(--bg-surface); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); color: var(--text-primary); min-height: 46px; padding: 0 var(--sp-4); }
    .button { text-align: center; }
    .help { font-size: var(--text-sm); text-align: center; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginPageComponent {}
