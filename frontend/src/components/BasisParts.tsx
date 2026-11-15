/**
 * Small building blocks shared by the basis and bond yield views, composed
 * from the UI kit so the analytics panels read like the rest of the app.
 */

import React from 'react';
import { Notice, Table, TableScroll } from './ui';
import { color, fontSize, fontWeight, space } from '../theme/tokens';

/** Even vertical spacing between the blocks of a panel body. */
export const Stack: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      gap: space.lg,
      minWidth: 0,
    }}
  >
    {children}
  </div>
);

/** Heading for one block inside a panel: a chart or a table. */
export const SubHeading: React.FC<{
  children: React.ReactNode;
  /** Secondary figures or units shown beside the heading. */
  note?: React.ReactNode;
}> = ({ children, note }) => (
  <h4
    style={{
      display: 'flex',
      flexWrap: 'wrap',
      alignItems: 'baseline',
      gap: space.sm,
      margin: `0 0 ${space.sm}`,
      fontSize: fontSize.md,
      fontWeight: fontWeight.semibold,
      color: color.ink,
    }}
  >
    {children}
    {note && (
      <span
        style={{
          fontSize: fontSize.sm,
          fontWeight: fontWeight.regular,
          color: color.inkDim,
        }}
      >
        {note}
      </span>
    )}
  </h4>
);

/** Explanatory line under a table or chart. */
export const Caption: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <p
    style={{
      margin: `${space.sm} 0 0`,
      fontSize: fontSize.sm,
      lineHeight: 1.5,
      color: color.inkDim,
    }}
  >
    {children}
  </p>
);

/** Caveats attached to a result. Renders nothing when there are none. */
export const Notes: React.FC<{ notes: string[] }> = ({ notes }) => {
  if (notes.length === 0) return null;
  return (
    <Notice tone="warning">
      {notes.length === 1 ? (
        notes[0]
      ) : (
        <ul style={{ margin: 0, paddingLeft: space.lg }}>
          {notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      )}
    </Notice>
  );
};

/**
 * Table of figures that scrolls sideways inside its own box. Cells never
 * wrap, so a bid/ask pair or a signed value stays on one line.
 */
export const FigureTable: React.FC<{
  children: React.ReactNode;
  /** Caps the height; the header stays pinned while the body scrolls. */
  maxHeight?: number;
}> = ({ children, maxHeight }) => (
  <TableScroll maxHeight={maxHeight}>
    <div style={{ whiteSpace: 'nowrap' }}>
      <Table>{children}</Table>
    </div>
  </TableScroll>
);

/** A table kept collapsed under the chart that already shows the same data. */
export const Disclosure: React.FC<{
  summary: React.ReactNode;
  children: React.ReactNode;
}> = ({ summary, children }) => (
  <details>
    <summary
      style={{
        cursor: 'pointer',
        width: 'fit-content',
        fontSize: fontSize.md,
        fontWeight: fontWeight.medium,
        color: color.inkMid,
      }}
    >
      {summary}
    </summary>
    <div style={{ marginTop: space.sm }}>{children}</div>
  </details>
);
