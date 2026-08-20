/**
 * Loading, error and empty states.
 *
 * Each panel owns its own state so one failed request does not blank the page.
 */

import React from 'react';
import { color, fontSize, radius, space } from '../../theme/tokens';
import { Button } from './Button';

export const Skeleton: React.FC<{
  height?: number | string;
  width?: number | string;
  style?: React.CSSProperties;
}> = ({ height = 16, width = '100%', style }) => (
  <div
    className="hts-skeleton"
    aria-hidden="true"
    style={{ height, width, ...style }}
  />
);

/** Placeholder standing in for a panel while its request is in flight. */
export const SkeletonPanel: React.FC<{ rows?: number; height?: number }> = ({
  rows = 3,
  height = 16,
}) => (
  <div
    role="status"
    aria-live="polite"
    aria-busy="true"
    style={{ display: 'flex', flexDirection: 'column', gap: space.sm }}
  >
    {Array.from({ length: rows }, (_, index) => (
      <Skeleton
        key={index}
        height={height}
        width={index === rows - 1 ? '60%' : '100%'}
      />
    ))}
  </div>
);

type NoticeTone = 'error' | 'warning';

const TONES: Record<NoticeTone, { ink: string; surface: string; border: string }> = {
  error: {
    ink: color.dangerInk,
    surface: color.dangerSurface,
    border: color.dangerBorder,
  },
  warning: {
    ink: color.warnInk,
    surface: color.warnSurface,
    border: color.warnBorder,
  },
};

/** Inline message explaining what failed, with a way to recover. */
export const Notice: React.FC<{
  children: React.ReactNode;
  tone?: NoticeTone;
  onRetry?: () => void;
  retryLabel?: string;
}> = ({ children, tone = 'error', onRetry, retryLabel = '다시 시도' }) => {
  const palette = TONES[tone];
  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      style={{
        display: 'flex',
        gap: space.md,
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        padding: `${space.md} ${space.lg}`,
        backgroundColor: palette.surface,
        border: `1px solid ${palette.border}`,
        borderRadius: radius.md,
        color: palette.ink,
        fontSize: fontSize.base,
      }}
    >
      <div style={{ minWidth: 0 }}>{children}</div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          {retryLabel}
        </Button>
      )}
    </div>
  );
};

export const EmptyState: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div
    style={{
      padding: space.xxl,
      textAlign: 'center',
      color: color.inkDim,
      fontSize: fontSize.base,
      border: `1px dashed ${color.border}`,
      borderRadius: radius.lg,
      backgroundColor: color.surfaceMuted,
    }}
  >
    {children}
  </div>
);
