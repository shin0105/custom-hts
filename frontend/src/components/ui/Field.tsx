/**
 * Labelled form controls.
 */

import React from 'react';
import { color, fontSize, fontWeight, space } from '../../theme/tokens';

/** Wraps a control with a visible label, keeping the two associated. */
export const Field: React.FC<{
  label: React.ReactNode;
  children: React.ReactNode;
  hint?: React.ReactNode;
  /** Lays the label beside the control instead of above it. */
  inline?: boolean;
  style?: React.CSSProperties;
}> = ({ label, children, hint, inline = false, style }) => (
  <label
    style={{
      display: 'flex',
      flexDirection: inline ? 'row' : 'column',
      alignItems: inline ? 'center' : 'stretch',
      gap: inline ? space.sm : space.xs,
      fontSize: fontSize.md,
      minWidth: 0,
      ...style,
    }}
  >
    <span
      style={{
        color: color.inkMid,
        fontWeight: fontWeight.medium,
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </span>
    {children}
    {hint && (
      <span style={{ color: color.inkDim, fontSize: fontSize.sm }}>{hint}</span>
    )}
  </label>
);

export const TextInput: React.FC<
  React.InputHTMLAttributes<HTMLInputElement>
> = ({ className, ...rest }) => (
  <input
    className={['hts-input', className ?? ''].filter(Boolean).join(' ')}
    {...rest}
  />
);

export const Select: React.FC<
  React.SelectHTMLAttributes<HTMLSelectElement>
> = ({ className, children, ...rest }) => (
  <select
    className={['hts-select', className ?? ''].filter(Boolean).join(' ')}
    {...rest}
  >
    {children}
  </select>
);
