/**
 * Design tokens for the application.
 *
 * Every color, spacing step, radius and type size used by a component should
 * come from here rather than being written inline. Keeping them in one place
 * is what makes a later dark theme a token swap instead of a rewrite.
 */

export const color = {
  /** Page background behind all panels. */
  ground: '#f2f4f8',
  /** Default panel/card surface. */
  surface: '#ffffff',
  /** Secondary surface: table headers, panel headers, inset rows. */
  surfaceMuted: '#f8f9fc',
  /** Tertiary surface: zebra striping, disabled controls. */
  surfaceSunken: '#eef1f6',

  /** Primary text. */
  ink: '#10141b',
  /** Secondary text: descriptions, table body on muted rows. */
  inkMid: '#47515f',
  /** Tertiary text: captions, field hints, units. */
  inkDim: '#6d7889',
  /** Text on a dark or accent-filled surface. */
  inkInverted: '#ffffff',

  /** Panel and table borders. */
  border: '#dce0e8',
  /** Lighter rule between rows inside a panel. */
  borderSoft: '#e9ecf2',

  /** Interactive accent: primary buttons, active tabs, focus rings. */
  accent: '#1748c4',
  accentHover: '#123a9f',
  accentSoft: '#eaf0fd',
  accentInk: '#123a9f',

  /** Dark chrome: navigation bar. */
  chrome: '#141a24',
  chromeMuted: '#232c3a',

  /** Status surfaces. */
  dangerInk: '#a3151f',
  dangerSurface: '#fdeced',
  dangerBorder: '#f5c2c6',
  warnInk: '#8a5d0f',
  warnSurface: '#fbf2e2',
  warnBorder: '#ecd7ab',
  infoInk: '#123a9f',
  infoSurface: '#eaf0fd',
  infoBorder: '#c5d6f7',
} as const;

export const space = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  xxl: '32px',
} as const;

export const radius = {
  sm: '4px',
  md: '6px',
  lg: '8px',
  pill: '999px',
} as const;

export const fontSize = {
  /** Field hints, table sub-labels, unit notes. */
  xs: '11px',
  /** Captions, secondary metadata. */
  sm: '12px',
  /** Dense table body, control labels. */
  md: '13px',
  /** Default body and input text. */
  base: '14px',
  /** Emphasized values inside tiles. */
  lg: '16px',
  /** Panel titles. */
  xl: '18px',
  /** Section headings. */
  xxl: '22px',
  /** Page titles. */
  display: '28px',
} as const;

export const fontWeight = {
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const;

/** Monospace stack for codes, tickers and raw API field names. */
export const monoFont =
  "'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

export const shadow = {
  panel: '0 1px 2px rgba(16, 20, 27, 0.04)',
  raised: '0 6px 16px rgba(16, 20, 27, 0.10)',
} as const;

/**
 * Applied to any element rendering figures that line up in a column.
 * Without this, proportional digits make prices in a table impossible to scan.
 */
export const tabularNums = {
  fontVariantNumeric: 'tabular-nums',
  fontFeatureSettings: '"tnum"',
} as const;
