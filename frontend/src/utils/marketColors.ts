/**
 * Price-direction color conventions.
 *
 * Korean markets read red as up and blue as down — the opposite of the
 * convention used in US markets. Every domestic HTS (영웅문, eFriend, M-STOCK)
 * follows the Korean convention, so a Korean user reading a green-up screen
 * misreads direction at a glance.
 *
 * Nothing outside this module should hard-code a change color.
 */

export type ColorConvention = 'kr' | 'global';

export type PriceDirection =
  | 'upperLimit'
  | 'up'
  | 'flat'
  | 'down'
  | 'lowerLimit';

type DirectionPalette = Record<PriceDirection, string>;

/** 빨강 상승 / 파랑 하락. 상한가·하한가는 같은 계열의 더 짙은 톤. */
const KR_PALETTE: DirectionPalette = {
  upperLimit: '#b3121f',
  up: '#d92b3a',
  flat: '#5b6674',
  down: '#1e56c8',
  lowerLimit: '#0b3ba8',
};

/** Green up / red down, as used on US venues. */
const GLOBAL_PALETTE: DirectionPalette = {
  upperLimit: '#15803d',
  up: '#16a34a',
  flat: '#6b7280',
  down: '#dc2626',
  lowerLimit: '#b91c1c',
};

const PALETTES: Record<ColorConvention, DirectionPalette> = {
  kr: KR_PALETTE,
  global: GLOBAL_PALETTE,
};

/** Arrow glyphs are convention-independent: direction, not color. */
const DIRECTION_GLYPHS: Record<PriceDirection, string> = {
  upperLimit: '↑',
  up: '▲',
  flat: '―',
  down: '▼',
  lowerLimit: '↓',
};

const DIRECTION_LABELS: Record<PriceDirection, string> = {
  upperLimit: '상한',
  up: '상승',
  flat: '보합',
  down: '하락',
  lowerLimit: '하한',
};

/**
 * KDevelopers 전일대비부호 (prdy_vrss_sign):
 * 1 상한 / 2 상승 / 3 보합 / 4 하한 / 5 하락.
 */
const SIGN_CODE_DIRECTIONS: Record<string, PriceDirection> = {
  '1': 'upperLimit',
  '2': 'up',
  '3': 'flat',
  '4': 'down',
  '5': 'lowerLimit',
};

/** Direction from a raw change amount. */
export function directionFromChange(
  change: number | null | undefined
): PriceDirection {
  if (change === null || change === undefined || Number.isNaN(change)) {
    return 'flat';
  }
  if (change > 0) return 'up';
  if (change < 0) return 'down';
  return 'flat';
}

/**
 * Direction from a KDevelopers sign code, falling back to the change amount
 * when the code is missing or unrecognized.
 */
export function directionFromSignCode(
  signCode: string | null | undefined,
  change?: number | null
): PriceDirection {
  const normalized = String(signCode ?? '').trim();
  return SIGN_CODE_DIRECTIONS[normalized] ?? directionFromChange(change);
}

export function directionColor(
  direction: PriceDirection,
  convention: ColorConvention
): string {
  return PALETTES[convention][direction];
}

/** Color for a raw change amount under the given convention. */
export function changeColor(
  change: number | null | undefined,
  convention: ColorConvention
): string {
  return directionColor(directionFromChange(change), convention);
}

export function directionGlyph(direction: PriceDirection): string {
  return DIRECTION_GLYPHS[direction];
}

export function directionLabel(direction: PriceDirection): string {
  return DIRECTION_LABELS[direction];
}

export const CONVENTION_LABELS: Record<ColorConvention, string> = {
  kr: '국내식 (상승 빨강)',
  global: '글로벌식 (상승 초록)',
};
