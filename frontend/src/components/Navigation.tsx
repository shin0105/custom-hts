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
    padding: '16px 32px',
    backgroundColor: '#1f2937',
    color: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  };

  const linkStyle = (isActive: boolean): React.CSSProperties => ({
    padding: '8px 16px',
    marginLeft: '16px',
    borderRadius: '4px',
    textDecoration: 'none',
    color: 'white',
    backgroundColor: isActive ? '#3b82f6' : 'transparent',
    transition: 'background-color 0.2s',
  });

  return (
    <nav style={navStyle}>
      <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>
        Custom HTS
      </h1>
      <div style={{ display: 'flex' }}>
        <Link
          to="/"
          style={linkStyle(location.pathname === '/')}
        >
          Home
        </Link>
        <Link
          to="/korean"
          style={linkStyle(location.pathname === '/korean')}
        >
          Korean Market
        </Link>
        <Link
          to="/bonds"
          style={linkStyle(location.pathname === '/bonds')}
        >
          Bonds
        </Link>
        <Link
          to="/futures-options"
          style={linkStyle(location.pathname === '/futures-options')}
        >
          Futures & Options
        </Link>
        <Link
          to="/basis"
          style={linkStyle(location.pathname === '/basis')}
        >
          Basis
        </Link>
        <Link
          to="/us"
          style={linkStyle(location.pathname === '/us')}
        >
          US Market
        </Link>
        <Link
          to="/account-check"
          style={linkStyle(location.pathname === '/account-check')}
        >
          Account Check
        </Link>
      </div>
    </nav>
  );
};
