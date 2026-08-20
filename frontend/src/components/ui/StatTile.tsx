/**
 * StatTile — one labelled figure. The building block of every metric grid.
 */

import React from 'react';
import { color, fontSize, fontWeight, radius, space, tabularNums } from '../../theme/tokens';

export const StatTile: React.FC<{
  label: React.ReactNode;
  value: React.ReactNode;
  /** Secondary line: the raw account name, a unit, a comparison. */
  sub?: React.ReactNode;
  /** Overrides the value color — pass a direction color for price figures. */
  valueColor?: string;
  /** Sized up for the metric a panel leads with. */
  emphasis?: boolean;
}> = ({ label, value, sub, valueColor, emphasis = false }) => (
  <div
    style={{
      backgroundColor: color.surfaceMuted,
      border: `1px solid ${color.borderSoft}`,
      borderRadius: radius.md,
      padding: space.md,
      minWidth: 0,
    }}
  >
    <div
      style={{
        fontSize: fontSize.sm,
        fontWeight: fontWeight.medium,
        color: color.inkDim,
      }}
    >
      {label}
    </div>
    <div
      style={{
        fontSize: emphasis ? fontSize.xxl : fontSize.lg,
        fontWeight: fontWeight.bold,
        color: valueColor ?? color.ink,
        marginTop: '3px',
        ...tabularNums,
      }}
    >
      {value}
    </div>
    {sub && (
      <div
        style={{
          fontSize: fontSize.xs,
          color: color.inkDim,
          marginTop: '2px',
          wordBreak: 'break-word',
        }}
      >
        {sub}
      </div>
    )}
  </div>
);

/** Responsive grid of tiles. */
export const StatGrid: React.FC<{
  children: React.ReactNode;
  /** Minimum tile width before the grid wraps. */
  minWidth?: number;
}> = ({ children, minWidth = 160 }) => (
  <div
    style={{
      display: 'grid',
      gridTemplateColumns: `repeat(auto-fit, minmax(${minWidth}px, 1fr))`,
      gap: space.md,
    }}
  >
    {children}
  </div>
);
