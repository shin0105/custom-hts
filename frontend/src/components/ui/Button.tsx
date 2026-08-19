/**
 * Buttons and toggle chips.
 */

import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: 'md' | 'sm';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className,
  type = 'button',
  ...rest
}) => (
  <button
    type={type}
    className={[
      'hts-btn',
      `hts-btn--${variant}`,
      size === 'sm' ? 'hts-btn--sm' : '',
      className ?? '',
    ]
      .filter(Boolean)
      .join(' ')}
    {...rest}
  />
);

interface ChipProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Rendered as `aria-pressed` so the active state is not conveyed by color alone. */
  active?: boolean;
}

export const Chip: React.FC<ChipProps> = ({
  active = false,
  className,
  type = 'button',
  ...rest
}) => (
  <button
    type={type}
    aria-pressed={active}
    className={['hts-chip', className ?? ''].filter(Boolean).join(' ')}
    {...rest}
  />
);

/** A row of chips behaving as one segmented control. */
export const ChipGroup: React.FC<{
  children: React.ReactNode;
  label?: string;
}> = ({ children, label }) => (
  <div
    role="group"
    aria-label={label}
    style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}
  >
    {children}
  </div>
);
