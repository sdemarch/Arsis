export interface NavigationArea {
  readonly label: string;
  readonly path: string;
  /** False for areas with a sidebar but no top bar tab. */
  readonly inTopbar?: boolean;
  readonly children: readonly {
    label: string;
    path: string;
    queryParams?: Readonly<Record<string, string>>;
  }[];
}

export const NAVIGATION: readonly NavigationArea[] = [
  { label: 'Home', path: '/home', children: [{ label: 'Dashboard', path: '/home' }] },
  {
    label: 'Soci',
    path: '/people',
    children: [
      { label: 'Tutte le persone', path: '/people' },
      { label: 'Soci', path: '/people', queryParams: { role: 'member' } },
      { label: 'Musicanti', path: '/people', queryParams: { role: 'musician' } },
      { label: 'Allievi', path: '/people', queryParams: { role: 'student' } },
      { label: 'Insegnanti', path: '/people', queryParams: { role: 'teacher' } },
    ],
  },
  {
    label: 'Attività',
    path: '/activities',
    children: [
      { label: 'Calendario', path: '/activities/calendar' },
      { label: 'Tutte le attività', path: '/activities' },
      { label: 'Prove', path: '/activities', queryParams: { type: 'rehearsal' } },
      { label: 'Concerti', path: '/activities', queryParams: { type: 'concert' } },
      { label: 'Eventi', path: '/activities', queryParams: { type: 'event' } },
      { label: 'Presenze', path: '/activities/attendance' },
    ],
  },
  {
    label: 'Scuola',
    path: '/school/courses',
    children: [
      { label: 'Corsi', path: '/school/courses' },
      { label: 'Iscrizioni', path: '/school/enrollments' },
      { label: 'Lezioni', path: '/school/lessons' },
      { label: 'Registro presenze', path: '/school/attendance' },
    ],
  },
  { label: 'Archivio', path: '/archive', children: [{ label: 'Apri Google Drive', path: '/archive' }] },
  {
    label: 'Contabilità',
    path: '/accounting',
    children: [
      { label: 'Registro contabile', path: '/accounting', queryParams: { tab: 'register' } },
      { label: 'Bilancio', path: '/accounting', queryParams: { tab: 'balance' } },
    ],
  },
  {
    // Reached from the user menu, not the top bar (functional spec §13).
    label: 'Configurazioni',
    path: '/settings',
    inTopbar: false,
    children: [
      { label: 'Generali e responsabili', path: '/settings' },
      { label: 'Strumenti e sezioni', path: '/settings/catalogues' },
      { label: 'Categorie contabili', path: '/settings/accounting-categories' },
      { label: 'Salvataggi', path: '/settings/saves' },
    ],
  },
];
