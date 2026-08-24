import { Injectable, signal } from '@angular/core';

import settingsData from '../../../assets/mock/settings.json';

export interface PersonRoleOption {
  readonly id: string;
  readonly label: string;
  readonly description: string;
  readonly active: boolean;
}

@Injectable({ providedIn: 'root' })
export class ConfigurationStore {
  readonly roles = signal<PersonRoleOption[]>(settingsData.roles.map((role) => ({ ...role })));

  toggleRole(roleId: string): void {
    this.roles.update((roles) => roles.map((role) => role.id === roleId ? { ...role, active: !role.active } : role));
  }

  addRole(label: string): void {
    const cleanLabel = label.trim();
    if (!cleanLabel) return;
    this.roles.update((roles) => [...roles, {
      id: cleanLabel.toLocaleLowerCase('it').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''),
      label: cleanLabel,
      description: 'Ruolo personalizzato',
      active: true,
    }]);
  }
}
