/**
 * Navigation component for switching between markets.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Navigation: React.FC = () => {
  const location = useLocation();

  const navStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: '12px',
    padding: 'clamp(12px, 3vw, 16px) clamp(16px, 4vw, 32px)',
    backgroundColor: '#1f2937',
    color: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  };

  const linkStyle = (isActive: boolean): React.CSSProperties => ({
    padding: '8px 14px',
    borderRadius: '4px',
    textDecoration: 'none',
    whiteSpace: 'nowrap',
    color: 'white',
    backgroundColor: isActive ? '#3b82f6' : 'transparent',
    transition: 'background-color 0.2s',
  });

  return (
    <nav style={navStyle}>
      <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
        Custom HTS
      </h1>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
        <Link
          to="/"
          aria-current={location.pathname === '/' ? 'page' : undefined}
          style={linkStyle(location.pathname === '/')}
        >
          Home
        </Link>
        <Link
          to="/korean"
          aria-current={location.pathname === '/korean' ? 'page' : undefined}
          style={linkStyle(location.pathname === '/korean')}
        >
          Korean Market
        </Link>
        <Link
          to="/bonds"
          aria-current={location.pathname === '/bonds' ? 'page' : undefined}
          style={linkStyle(location.pathname === '/bonds')}
        >
          Bonds
        </Link>
        <Link
          to="/futures-options"
          aria-current={location.pathname === '/futures-options' ? 'page' : undefined}
          style={linkStyle(location.pathname === '/futures-options')}
        >
          Futures & Options
        </Link>
        <Link
          to="/us"
          aria-current={location.pathname === '/us' ? 'page' : undefined}
          style={linkStyle(location.pathname === '/us')}
        >
          US Market
        </Link>
        <Link
          to="/account-check"
          aria-current={location.pathname === '/account-check' ? 'page' : undefined}
          style={linkStyle(location.pathname === '/account-check')}
        >
          Account Check
        </Link>
      </div>
    </nav>
  );
};
