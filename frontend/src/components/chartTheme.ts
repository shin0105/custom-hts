/**
 * Colours and date helpers shared by the analytics charts.
 *
 * series1/series2 are a colour-blind-safe pair; text always uses the ink
 * tones, never a series colour.
 */

export const chartTheme = {
  series1: '#2a78d6',
  series2: '#eb6834',
  grid: '#e5e7eb',
  zeroLine: '#9ca3af',
  surface: '#ffffff',
  ink: '#111827',
  inkSecondary: '#4b5563',
  inkMuted: '#6b7280',
};

/** YYYYMMDD -> MM/DD */
export const shortDate = (value: string) =>
  value.length === 8 ? `${value.slice(4, 6)}/${value.slice(6, 8)}` : value;

/** YYYYMMDD -> YYYY-MM-DD */
export const isoDate = (value?: string | null) =>
  value && value.length === 8
    ? `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`
    : '-';
