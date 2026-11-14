/**
 * Small building blocks shared by the basis views.
 */

import React from 'react';

export const Stat: React.FC<{ label: string; value: string; hint?: string }> = ({
  label,
  value,
  hint,
}) => (
  <div
    style={{
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '12px',
      backgroundColor: '#f9fafb',
    }}
  >
    <div style={{ fontSize: '12px', color: '#6b7280' }}>{label}</div>
    <div
      style={{
        fontSize: '20px',
        fontWeight: 600,
        color: '#111827',
        fontVariantNumeric: 'tabular-nums',
      }}
    >
      {value}
    </div>
    {hint && <div style={{ fontSize: '12px', color: '#6b7280' }}>{hint}</div>}
  </div>
);

export const Notes: React.FC<{ notes: string[] }> = ({ notes }) =>
  notes.length ? (
    <ul
      style={{
        margin: '12px 0 0',
        padding: '10px 12px 10px 28px',
        backgroundColor: '#fffbeb',
        border: '1px solid #fde68a',
        borderRadius: '6px',
        fontSize: '13px',
        color: '#78350f',
      }}
    >
      {notes.map((note) => (
        <li key={note}>{note}</li>
      ))}
    </ul>
  ) : null;
