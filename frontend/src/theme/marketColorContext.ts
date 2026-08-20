/**
 * Context plumbing for the price-direction color convention.
 *
 * Split from the provider component so that this module exports only hooks and
 * values — a file exporting both a component and non-components breaks React
 * Fast Refresh.
 */

import { createContext, useContext } from 'react';
import type {
  ColorConvention,
  PriceDirection,
} from '../utils/marketColors';
import {
  changeColor,
  directionColor,
  directionFromChange,
  directionFromSignCode,
  directionGlyph,
  directionLabel,
} from '../utils/marketColors';

export const COLOR_CONVENTION_STORAGE_KEY = 'custom-hts.colorConvention';

export interface MarketColorContextValue {
  convention: ColorConvention;
  setConvention: (next: ColorConvention) => void;
}

export const MarketColorContext = createContext<MarketColorContextValue>({
  convention: 'kr',
  setConvention: () => undefined,
});

export interface MarketColors {
  /** The convention in effect for the caller. */
  convention: ColorConvention;
  /** Change the user's stored preference. Ignored when a page pins a convention. */
  setConvention: (next: ColorConvention) => void;
  /** Color for a raw change amount. */
  colorFor: (change: number | null | undefined) => string;
  /** Color for an already-resolved direction (handles 상한가/하한가). */
  colorForDirection: (direction: PriceDirection) => string;
  /** Direction from a KDevelopers sign code, falling back to the amount. */
  directionOf: (
    signCode: string | null | undefined,
    change?: number | null
  ) => PriceDirection;
  glyphFor: (direction: PriceDirection) => string;
  labelFor: (direction: PriceDirection) => string;
}

/**
 * Resolve the color convention for a component.
 *
 * Pass `pinned` on surfaces that must not follow the user's preference —
 * the US market page is always read with the global convention.
 */
export function useMarketColors(pinned?: ColorConvention): MarketColors {
  const { convention: preferred, setConvention } = useContext(MarketColorContext);
  const convention = pinned ?? preferred;

  return {
    convention,
    setConvention,
    colorFor: (change) => changeColor(change, convention),
    colorForDirection: (direction) => directionColor(direction, convention),
    directionOf: (signCode, change) => directionFromSignCode(signCode, change),
    glyphFor: directionGlyph,
    labelFor: directionLabel,
  };
}

export { directionFromChange };
