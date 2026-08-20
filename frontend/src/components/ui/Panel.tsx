/**
 * Panel — the bordered surface every section of a page sits on.
 */

import React from 'react';
import { color, fontSize, fontWeight, radius, shadow, space } from '../../theme/tokens';

export const Panel: React.FC<{
  children: React.ReactNode;
  /** Panel title, rendered in a muted header strip. */
  title?: React.ReactNode;
  /** Secondary content aligned to the right of the title. */
  actions?: React.ReactNode;
  /** Small note under the title — units, data source, as-of time. */
  note?: React.ReactNode;
  /** Removes the body padding for panels whose body is a table. */
  flush?: boolean;
  style?: React.CSSProperties;
}> = ({ children, title, actions, note, flush = false, style }) => (
  <section
    style={{
      backgroundColor: color.surface,
      border: `1px solid ${color.border}`,
      borderRadius: radius.lg,
      boxShadow: shadow.panel,
      overflow: 'hidden',
      ...style,
    }}
  >
    {(title || actions || note) && (
      <header
        style={{
          padding: `${space.md} ${space.lg}`,
          backgroundColor: color.surfaceMuted,
          borderBottom: `1px solid ${color.border}`,
          display: 'flex',
          flexWrap: 'wrap',
          gap: space.sm,
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ minWidth: 0 }}>
          {title && (
            <h3
              style={{
                fontSize: fontSize.base,
                fontWeight: fontWeight.semibold,
                color: color.ink,
                margin: 0,
              }}
            >
              {title}
            </h3>
          )}
          {note && (
            <p
              style={{
                fontSize: fontSize.sm,
                color: color.inkDim,
                margin: title ? '3px 0 0' : 0,
              }}
            >
              {note}
            </p>
          )}
        </div>
        {actions && (
          <div
            style={{
              display: 'flex',
              gap: space.sm,
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            {actions}
          </div>
        )}
      </header>
    )}
    <div style={flush ? undefined : { padding: space.lg }}>{children}</div>
  </section>
);

/** Page-level section heading with optional controls on the right. */
export const SectionHeader: React.FC<{
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
}> = ({ title, description, actions }) => (
  <div
    style={{
      display: 'flex',
      flexWrap: 'wrap',
      gap: space.md,
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      marginBottom: space.lg,
    }}
  >
    <div>
      <h2
        style={{
          fontSize: fontSize.xxl,
          fontWeight: fontWeight.semibold,
          letterSpacing: '-0.01em',
          margin: 0,
        }}
      >
        {title}
      </h2>
      {description && (
        <p
          style={{
            fontSize: fontSize.base,
            color: color.inkDim,
            margin: '4px 0 0',
          }}
        >
          {description}
        </p>
      )}
    </div>
    {actions && (
      <div
        style={{
          display: 'flex',
          gap: space.sm,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        {actions}
      </div>
    )}
  </div>
);
