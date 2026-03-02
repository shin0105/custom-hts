/**
 * Home page component.
 */

import React from 'react';
import { Link } from 'react-router-dom';

export const HomePage: React.FC = () => {
  const containerStyle: React.CSSProperties = {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '48px 24px',
    textAlign: 'center',
  };

  const cardStyle: React.CSSProperties = {
    display: 'inline-block',
    width: '300px',
    margin: '16px',
    padding: '32px',
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    backgroundColor: 'white',
    textDecoration: 'none',
    color: 'inherit',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
  };

  return (
    <div style={containerStyle}>
      <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '16px' }}>
        Welcome to Custom HTS
      </h1>
      <p style={{ fontSize: '20px', color: '#6b7280', marginBottom: '48px' }}>
        Your gateway to Korean and US stock markets
      </p>

      <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap' }}>
        <Link
          to="/korean"
          style={cardStyle}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '12px' }}>
            🇰🇷 Korean Market
          </h2>
          <p style={{ color: '#6b7280' }}>
            Access KOSPI & KOSDAQ stocks with real-time data from Korean
            Investment Securities
          </p>
        </Link>

        <Link
          to="/us"
          style={cardStyle}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '12px' }}>
            🇺🇸 US Market
          </h2>
          <p style={{ color: '#6b7280' }}>
            Track NYSE & NASDAQ stocks with comprehensive data from Yahoo Finance
          </p>
        </Link>

        <Link
          to="/bonds"
          style={cardStyle}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '12px' }}>
            🏦 장내채권
          </h2>
          <p style={{ color: '#6b7280' }}>
            장내채권 마스터 파일 기반 상장 채권 목록과 현재가/핵심 정보를 확인합니다
          </p>
        </Link>

        <Link
          to="/futures-options"
          style={cardStyle}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '12px' }}>
            📈 선물옵션
          </h2>
          <p style={{ color: '#6b7280' }}>
            국내 지수/주식/상품 선물옵션 마스터 파일을 검색하고 필터링합니다
          </p>
        </Link>

        <Link
          to="/account-check"
          style={cardStyle}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '12px' }}>
            🧾 Account Check
          </h2>
          <p style={{ color: '#6b7280' }}>
            View Korean stock account balance API parameters and response fields
          </p>
        </Link>
      </div>

      <div
        style={{
          marginTop: '64px',
          padding: '24px',
          backgroundColor: '#f9fafb',
          borderRadius: '8px',
        }}
      >
        <h3 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>
          Features
        </h3>
        <ul
          style={{
            listStyle: 'none',
            padding: 0,
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '16px',
            textAlign: 'left',
          }}
        >
          <li>📊 Real-time stock quotes</li>
          <li>💰 Financial statements analysis</li>
          <li>📈 Historical price charts</li>
          <li>🔍 Company search</li>
          <li>💱 Multi-currency support</li>
          <li>⚡ Fast and responsive UI</li>
        </ul>
      </div>
    </div>
  );
};
