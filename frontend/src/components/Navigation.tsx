/**
 * Navigation component for switching between markets.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { color, fontSize, fontWeight, radius, space } from '../theme/tokens';
import { useMarketColors } from '../theme/marketColorContext';
import { CONVENTION_LABELS } from '../utils/marketColors';
import type { ColorConvention } from '../utils/marketColors';
import { ko } from '../i18n/ko';

const NAV_GROUPS: Array<{ label: string; items: Array<{ to: string; label: string }> }> = [
  {
    label: '국내',
    items: [
      { to: '/korean', label: ko.nav.korean },
      { to: '/bonds', label: ko.nav.bonds },
      { to: '/futures-options', label: ko.nav.futuresOptions },
    ],
  },
  {
    label: '해외',
    items: [{ to: '/us', label: ko.nav.us }],
  },
  {
    label: '계좌',
    items: [{ to: '/account-check', label: ko.nav.account }],
  },
];

const CONVENTIONS: ColorConvention[] = ['kr', 'global'];

export const Navigation: React.FC = () => {
  const location = useLocation();
  const { convention, setConvention } = useMarketColors();

  const linkStyle = (isActive: boolean): React.CSSProperties => ({
    padding: '7px 12px',
    borderRadius: radius.md,
    fontSize: fontSize.base,
    fontWeight: isActive ? fontWeight.semibold : fontWeight.regular,
    color: isActive ? color.inkInverted : 'rgba(255,255,255,0.72)',
    backgroundColor: isActive ? color.accent : 'transparent',
    transition: 'background-color 0.15s ease, color 0.15s ease',
    whiteSpace: 'nowrap',
  });

  const groupLabelStyle: React.CSSProperties = {
    fontSize: fontSize.xs,
    color: 'rgba(255,255,255,0.42)',
    letterSpacing: '0.08em',
    alignSelf: 'center',
    whiteSpace: 'nowrap',
  };

  return (
    <nav
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: space.lg,
        flexWrap: 'wrap',
        padding: `${space.md} ${space.xl}`,
        backgroundColor: color.chrome,
        color: color.inkInverted,
      }}
    >
      <Link
        to="/"
        style={{
          fontSize: fontSize.xl,
          fontWeight: fontWeight.bold,
          letterSpacing: '-0.01em',
          marginRight: space.sm,
        }}
      >
        {ko.nav.brand}
      </Link>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: space.md,
          flexWrap: 'wrap',
          flex: 1,
          minWidth: 0,
        }}
      >
        {NAV_GROUPS.map((group, index) => (
          <React.Fragment key={group.label}>
            {index > 0 && (
              <span
                aria-hidden="true"
                style={{
                  width: '1px',
                  height: '18px',
                  backgroundColor: color.chromeMuted,
                }}
              />
            )}
            <span style={groupLabelStyle}>{group.label}</span>
            {group.items.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                aria-current={location.pathname === item.to ? 'page' : undefined}
                style={linkStyle(location.pathname === item.to)}
              >
                {item.label}
              </Link>
            ))}
          </React.Fragment>
        ))}
      </div>

      {/* Korean markets read red as up; the toggle exists for anyone who
          prefers the global convention. */}
      <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
        <span style={groupLabelStyle}>{ko.nav.colorConvention}</span>
        <div
          role="group"
          aria-label={ko.nav.colorConvention}
          style={{
            display: 'flex',
            border: `1px solid ${color.chromeMuted}`,
            borderRadius: radius.md,
            overflow: 'hidden',
          }}
        >
          {CONVENTIONS.map((option) => {
            const isActive = convention === option;
            return (
              <button
                key={option}
                type="button"
                aria-pressed={isActive}
                title={CONVENTION_LABELS[option]}
                onClick={() => setConvention(option)}
                style={{
                  border: 'none',
                  cursor: 'pointer',
                  padding: '5px 10px',
                  fontFamily: 'inherit',
                  fontSize: fontSize.sm,
                  fontWeight: isActive ? fontWeight.semibold : fontWeight.regular,
                  backgroundColor: isActive ? color.chromeMuted : 'transparent',
                  color: isActive
                    ? color.inkInverted
                    : 'rgba(255,255,255,0.55)',
                }}
              >
                <span
                  aria-hidden="true"
                  style={{
                    color: isActive
                      ? option === 'kr'
                        ? '#d92b3a'
                        : '#16a34a'
                      : 'inherit',
                  }}
                >
                  ▲
                </span>{' '}
                {option === 'kr' ? '국내식' : '글로벌식'}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
