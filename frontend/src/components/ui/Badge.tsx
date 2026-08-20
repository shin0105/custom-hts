/**
 * Badge — compact status marker. State is carried by the text, not only color.
 */

import React from 'react';
import { color, fontSize, fontWeight, radius } from '../../theme/tokens';

type BadgeTone = 'neutral' | 'accent' | 'warning' | 'danger';

const TONES: Record<BadgeTone, { ink: string; surface: string; border: string }> = {
  neutral: {
    ink: color.inkMid,
    surface: color.surfaceMuted,
    border: color.border,
  },
  accent: {
    ink: color.accentInk,
    surface: color.accentSoft,
    border: color.accent,
  },
  warning: {
    ink: color.warnInk,
    surface: color.warnSurface,
    border: color.warnBorder,
  },
  danger: {
    ink: color.dangerInk,
    surface: color.dangerSurface,
    border: color.dangerBorder,
  },
};

export const Badge: React.FC<{
  children: React.ReactNode;
  tone?: BadgeTone;
  title?: string;
}> = ({ children, tone = 'neutral', title }) => {
  const palette = TONES[tone];
  return (
    <span
      title={title}
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: radius.pill,
        fontSize: fontSize.sm,
        fontWeight: fontWeight.medium,
        color: palette.ink,
        backgroundColor: palette.surface,
        border: `1px solid ${palette.border}`,
        whiteSpace: 'nowrap',
      }}
    >
      {children}
    </span>
  );
};
