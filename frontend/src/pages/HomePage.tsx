/**
 * Home page component.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { color, fontSize, fontWeight, radius, space } from '../theme/tokens';
import { ko } from '../i18n/ko';

const MARKETS: Array<{
  to: string;
  icon: string;
  title: string;
  description: string;
}> = [
  {
    to: '/korean',
    icon: '🇰🇷',
    title: ko.nav.korean,
    description:
      'KOSPI·KOSDAQ 종목의 시세, 투자지표, 재무제표, 추정실적을 조회합니다.',
  },
  {
    to: '/bonds',
    icon: '🏦',
    title: ko.nav.bonds,
    description:
      '장내채권 마스터 기반 종목 검색과 현재가, 이론가, 발행 정보를 확인합니다.',
  },
  {
    to: '/futures-options',
    icon: '📈',
    title: ko.nav.futuresOptions,
    description: '국내 지수·주식·상품 선물옵션 마스터를 검색하고 차트를 조회합니다.',
  },
  {
    to: '/us',
    icon: '🇺🇸',
    title: ko.nav.us,
    description: 'NYSE·NASDAQ 종목을 Yahoo Finance 데이터로 조회합니다.',
  },
  {
    to: '/account-check',
    icon: '🧾',
    title: ko.nav.account,
    description: '국내주식 계좌의 잔고 구성과 평가 손익을 확인합니다.',
  },
];

const FEATURES = [
  '📊 실시간 시세 조회',
  '💰 재무제표 분석',
  '📈 기간별 차트',
  '🔍 종목 검색',
  '💱 원화·달러 표기',
  '⚡ 국내 등락 색상 관행 적용',
];

export const HomePage: React.FC = () => (
  <div className="hts-page" style={{ maxWidth: '1100px', paddingTop: '48px' }}>
    <header style={{ textAlign: 'center', marginBottom: space.xxl }}>
      <h1
        style={{
          fontSize: '40px',
          fontWeight: fontWeight.bold,
          letterSpacing: '-0.02em',
          marginBottom: space.md,
        }}
      >
        Custom HTS
      </h1>
      <p style={{ fontSize: fontSize.xl, color: color.inkDim }}>
        국내 주식·채권·파생과 해외 주식을 한 곳에서
      </p>
    </header>

    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: space.lg,
      }}
    >
      {MARKETS.map((market) => (
        <Link key={market.to} to={market.to} className="hts-home-card">
          <h2
            style={{
              fontSize: fontSize.xl,
              fontWeight: fontWeight.semibold,
              marginBottom: space.sm,
            }}
          >
            <span aria-hidden="true">{market.icon}</span> {market.title}
          </h2>
          <p
            style={{
              color: color.inkDim,
              fontSize: fontSize.base,
              lineHeight: 1.6,
            }}
          >
            {market.description}
          </p>
        </Link>
      ))}
    </div>

    <section
      style={{
        marginTop: space.xxl,
        padding: space.xl,
        backgroundColor: color.surfaceMuted,
        border: `1px solid ${color.border}`,
        borderRadius: radius.lg,
      }}
    >
      <h3
        style={{
          fontSize: fontSize.xl,
          fontWeight: fontWeight.semibold,
          marginBottom: space.lg,
        }}
      >
        주요 기능
      </h3>
      <ul
        style={{
          listStyle: 'none',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: space.md,
          color: color.inkMid,
          fontSize: fontSize.base,
        }}
      >
        {FEATURES.map((feature) => (
          <li key={feature}>{feature}</li>
        ))}
      </ul>
    </section>
  </div>
);
