/**
 * Colours and date helpers shared by the analytics charts.
 *
 * series1/series2 are a validated colour-blind-safe pair and the only colours
 * defined here; every neutral comes from the design tokens. Text always uses
 * the ink tones, never a series colour.
 */

import { color } from '../theme/tokens';

export const chartTheme = {
  series1: '#2a78d6',
  series2: '#eb6834',
  grid: color.borderSoft,
  axis: color.border,
  zeroLine: color.inkDim,
  surface: color.surface,
  ink: color.ink,
  inkSecondary: color.inkMid,
  inkMuted: color.inkDim,
} as const;

/** YYYYMMDD -> MM/DD */
export const shortDate = (value: string) =>
  value.length === 8 ? `${value.slice(4, 6)}/${value.slice(6, 8)}` : value;
