export interface CourseColor {
  readonly name: string;
  readonly value: string;
  readonly background: string;
}

// Palette di dominio: è un dato del corso e non fa parte del tema dell'interfaccia.
export const COURSE_COLORS: readonly CourseColor[] = [
  { name: 'Blu', value: '#378ADD', background: '#EBF3FC' },
  { name: 'Verde', value: '#1D9E75', background: '#E6F6F0' },
  { name: 'Arancio', value: '#D85A30', background: '#FAEEE9' },
  { name: 'Ambra', value: '#BA7517', background: '#F7EDD9' },
  { name: 'Viola', value: '#7F77DD', background: '#EEEDF9' },
  { name: 'Teal', value: '#2BA8A0', background: '#E4F4F3' },
  { name: 'Rosa', value: '#C2507A', background: '#F7E8EF' },
  { name: 'Grafite', value: '#5A6572', background: '#EAEEF1' },
];

