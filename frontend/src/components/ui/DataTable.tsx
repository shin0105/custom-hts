/**
 * Table shells.
 *
 * Wide tables scroll inside their own container so the page body never scrolls
 * sideways, and numeric cells get lining tabular digits via `.hts-num`.
 */

import React from 'react';
import { color, radius } from '../../theme/tokens';

export const TableScroll: React.FC<{
  children: React.ReactNode;
  /** Caps the height and lets the sticky header do its job. */
  maxHeight?: number;
  bordered?: boolean;
}> = ({ children, maxHeight, bordered = true }) => (
  <div
    style={{
      overflowX: 'auto',
      overflowY: maxHeight ? 'auto' : undefined,
      maxHeight,
      border: bordered ? `1px solid ${color.border}` : undefined,
      borderRadius: bordered ? radius.lg : undefined,
      backgroundColor: color.surface,
    }}
  >
    {children}
  </div>
);

export const Table: React.FC<{
  children: React.ReactNode;
  /** Forces horizontal scrolling rather than crushing columns. */
  minWidth?: number;
}> = ({ children, minWidth }) => (
  <table className="hts-table" style={{ minWidth }}>
    {children}
  </table>
);

/** Two-column key/value table used for instrument detail. */
export const DefinitionTable: React.FC<{
  rows: Array<{ label: React.ReactNode; value: React.ReactNode; key?: string }>;
}> = ({ rows }) => (
  <table className="hts-table">
    <tbody>
      {rows.map((row, index) => (
        <tr key={row.key ?? index}>
          <th
            scope="row"
            style={{
              position: 'static',
              width: '38%',
              backgroundColor: color.surfaceMuted,
              color: color.inkMid,
              fontWeight: 500,
            }}
          >
            {row.label}
          </th>
          <td>{row.value}</td>
        </tr>
      ))}
    </tbody>
  </table>
);
