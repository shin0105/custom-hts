/**
 * Stores the user's price-direction color convention and persists it.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import type { ColorConvention } from '../utils/marketColors';
import {
  COLOR_CONVENTION_STORAGE_KEY,
  MarketColorContext,
} from './marketColorContext';

const isColorConvention = (value: unknown): value is ColorConvention =>
  value === 'kr' || value === 'global';

const readStoredConvention = (): ColorConvention => {
  if (typeof window === 'undefined') return 'kr';
  try {
    const stored = window.localStorage.getItem(COLOR_CONVENTION_STORAGE_KEY);
    return isColorConvention(stored) ? stored : 'kr';
  } catch {
    return 'kr';
  }
};

export const MarketColorProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [convention, setConventionState] =
    useState<ColorConvention>(readStoredConvention);

  const setConvention = useCallback((next: ColorConvention) => {
    setConventionState(next);
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(COLOR_CONVENTION_STORAGE_KEY, convention);
    } catch {
      // A blocked localStorage should not break the app; the preference simply
      // does not survive a reload.
    }
  }, [convention]);

  const value = useMemo(
    () => ({ convention, setConvention }),
    [convention, setConvention]
  );

  return (
    <MarketColorContext.Provider value={value}>
      {children}
    </MarketColorContext.Provider>
  );
};
