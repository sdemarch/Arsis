export interface NavigationArea {
  readonly label: string;
  readonly path: string;
  readonly children: readonly { label: string; path: string }[];
}

export const NAVIGATION: readonly NavigationArea[] = [
  { label: 'Home', path: '/home', children: [{ label: 'Dashboard', path: '/home' }] },
  {
    label: 'Soci',
    path: '/people',
    children: [
      { label: 'Tutte le persone', path: '/people' },
      { label: 'Soci', path: '/people?role=member' },
      { label: 'Musicanti', path: '/people?role=musician' },
      { label: 'Allievi', path: '/people?role=student' },
      { label: 'Insegnanti', path: '/people?role=teacher' },
    ],
  },
  {
    label: 'Attività',
    path: '/activities',
    children: [
      { label: 'Calendario', path: '/activities/calendar' },
      { label: 'Tutte le attività', path: '/activities' },
      { label: 'Prove', path: '/activities?type=rehearsal' },
      { label: 'Concerti', path: '/activities?type=concert' },
      { label: 'Eventi', path: '/activities?type=event' },
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
    children: [{ label: 'Da definire', path: '/accounting' }],
  },
];

