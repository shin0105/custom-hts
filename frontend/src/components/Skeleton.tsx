/**
 * Loading placeholders used while a section's data is in flight.
 */

import React from 'react';

interface SkeletonProps {
  width?: string;
  height?: string;
  radius?: string;
  style?: React.CSSProperties;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '16px',
  radius = '6px',
  style,
}) => (
  <div
    aria-hidden="true"
    style={{
      width,
      height,
      borderRadius: radius,
      backgroundColor: '#e5e7eb',
      animation: 'pulse 1.4s ease-in-out infinite',
      ...style,
    }}
  />
);

interface SkeletonBlockProps {
  /** Number of placeholder rows. */
  rows?: number;
  label?: string;
}

/** Card-shaped placeholder for a table or panel. */
export const SkeletonPanel: React.FC<SkeletonBlockProps> = ({
  rows = 5,
  label = 'Loading',
}) => (
  <div
    role="status"
    aria-live="polite"
    aria-label={label}
    style={{
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      backgroundColor: 'white',
      padding: '16px',
      display: 'grid',
      gap: '12px',
    }}
  >
    {Array.from({ length: rows }).map((_, index) => (
      <Skeleton
        key={index}
        width={index === 0 ? '40%' : '100%'}
        height={index === 0 ? '20px' : '14px'}
      />
    ))}
  </div>
);

/** Grid of metric-tile placeholders. */
export const SkeletonTiles: React.FC<{ count?: number; label?: string }> = ({
  count = 6,
  label = 'Loading metrics',
}) => (
  <div
    role="status"
    aria-live="polite"
    aria-label={label}
    style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
      gap: '12px',
      padding: '16px',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      backgroundColor: 'white',
    }}
  >
    {Array.from({ length: count }).map((_, index) => (
      <div key={index} style={{ display: 'grid', gap: '8px' }}>
        <Skeleton width="60%" height="12px" />
        <Skeleton width="80%" height="20px" />
      </div>
    ))}
  </div>
);

/**
 * Dims a section while a background refetch replaces its contents, so stale
 * numbers are never presented as current.
 */
export const StaleOverlay: React.FC<{
  stale: boolean;
  children: React.ReactNode;
}> = ({ stale, children }) => (
  <div
    style={{
      position: 'relative',
      opacity: stale ? 0.55 : 1,
      transition: 'opacity 0.2s ease',
    }}
    aria-busy={stale}
  >
    {children}
  </div>
);
