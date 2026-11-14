/**
 * Number helpers shared by the basis and bond yield views.
 *
 * Plain grouped numbers come from `utils/format` (`formatNumber`); this file
 * only holds what that module does not cover: signed figures whose sign is
 * decided after rounding.
 */

export const isNumber = (value?: number | null): value is number =>
  value !== null && value !== undefined && Number.isFinite(value);

/** Index levels carry two decimals; stock prices are whole won. */
export const priceDigits = (kind?: string) => (kind === 'index' ? 2 : 0);

/** Rounds first, so a value that displays as zero carries no sign. */
const roundTo = (value: number, digits: number) => Number(value.toFixed(digits)) || 0;

export const formatSigned = (
  value: number | null | undefined,
  digits: number,
  unit = ''
) => {
  if (!isNumber(value)) return '-';
  const rounded = roundTo(value, digits);
  return `${rounded > 0 ? '+' : ''}${rounded.toLocaleString('ko-KR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })}${unit}`;
};

export const formatSignedPercent = (value: number | null | undefined, digits = 2) => {
  if (!isNumber(value)) return '-';
  const rounded = roundTo(value, digits);
  return `${rounded > 0 ? '+' : ''}${rounded.toFixed(digits)}%`;
};
