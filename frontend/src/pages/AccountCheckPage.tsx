/**
 * Account Check page for Korean stocks balance overview.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { formatCurrency, formatPercent } from '../utils/format';
import { useMarketColors } from '../theme/marketColorContext';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanAccountResponse } from '../types/korean';

const palette = ['#38bdf8', '#f97316', '#14b8a6', '#a855f7', '#f43f5e', '#22c55e'];

const formatKRW = (value: number) => formatCurrency(value, 'KRW');

const formatSignedKRW = (value: number) => {
  const sign = value >= 0 ? '+' : '-';
  return `${sign}${formatCurrency(Math.abs(value), 'KRW')}`;
};

const formatSignedPercent = (value: number) => formatPercent(value, 2);

const maskAccount = (accountNumber: string) => {
  if (!accountNumber) return '—';
  const trimmed = accountNumber.trim();
  if (trimmed.length <= 4) return `••••${trimmed}`;
  return `••••${trimmed.slice(-4)}`;
};

const toKSTString = (iso: string) => {
  try {
    return new Date(iso).toLocaleString('ko-KR');
  } catch {
    return '—';
  }
};

const StatCard: React.FC<{
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}> = ({ label, value, sub, accent }) => (
  <div
    style={{
      backgroundColor: 'white',
      borderRadius: '16px',
      padding: '18px',
      border: '1px solid #e2e8f0',
      boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)',
    }}
  >
    <div style={{ fontSize: '12px', textTransform: 'uppercase', color: '#64748b' }}>{label}</div>
    <div className="hts-num" style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px', color: accent ?? '#0f172a' }}>
      {value}
    </div>
    {sub ? (
      <div style={{ marginTop: '4px', fontSize: '13px', color: '#64748b' }}>{sub}</div>
    ) : null}
  </div>
);

export const AccountCheckPage: React.FC = () => {
  const { colorFor } = useMarketColors();
  const [accountData, setAccountData] = useState<KoreanAccountResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAccount = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await koreanMarketService.getAccountBalance();
        setAccountData(data);
      } catch {
        setError('계좌 데이터를 불러오지 못했습니다. 백엔드 연결과 계좌 설정을 확인해주세요.');
      } finally {
        setLoading(false);
      }
    };

    loadAccount();
  }, []);

  const balance = accountData?.balance;

  const enrichedPositions = useMemo(() => {
    const positions = accountData?.positions ?? [];
    return positions.map((position, index) => {
      const evaluationAmount = Number.isFinite(position.evaluation_amount)
        ? position.evaluation_amount
        : undefined;
      const marketValue = evaluationAmount ?? position.current_price * position.quantity;
      const costValue = position.average_price * position.quantity;
      const profitLoss = Number.isFinite(position.profit_loss) ? position.profit_loss : marketValue - costValue;
      const profitLossPct = Number.isFinite(position.profit_loss_percent)
        ? position.profit_loss_percent
        : costValue
        ? (profitLoss / costValue) * 100
        : 0;
      return {
        ...position,
        marketValue,
        costValue,
        profitLoss,
        profitLossPct,
        color: palette[index % palette.length],
      };
    });
  }, [accountData]);

  const totals = useMemo(() => {
    const marketValue = enrichedPositions.reduce((sum, p) => sum + p.marketValue, 0);
    const cashBalance = balance?.cash_balance ?? 0;
    const totalEvaluation = balance?.total_evaluation ?? marketValue + cashBalance;
    const investmentAmount = balance?.investment_amount ?? enrichedPositions.reduce((sum, p) => sum + p.costValue, 0);
    const profitLoss = balance?.profit_loss ?? marketValue - investmentAmount;
    const profitLossPercent = balance?.profit_loss_percent ?? (investmentAmount ? (profitLoss / investmentAmount) * 100 : 0);

    return {
      marketValue,
      cashBalance,
      totalEvaluation,
      investmentAmount,
      profitLoss,
      profitLossPercent,
    };
  }, [balance, enrichedPositions]);

  const allocationGradient = useMemo(() => {
    if (!totals.marketValue) {
      return 'conic-gradient(#e2e8f0 0% 100%)';
    }
    let current = 0;
    const segments = enrichedPositions.map((position) => {
      const share = (position.marketValue / totals.marketValue) * 100;
      const start = current;
      const end = current + share;
      current = end;
      return `${position.color} ${start.toFixed(2)}% ${end.toFixed(2)}%`;
    });
    return `conic-gradient(${segments.join(', ')})`;
  }, [enrichedPositions, totals.marketValue]);

  const plMax = useMemo(() => {
    const values = enrichedPositions.map((position) => Math.abs(position.profitLoss));
    return Math.max(...values, 1);
  }, [enrichedPositions]);

  const containerStyle: React.CSSProperties = {
    minHeight: 'calc(100vh - 72px)',
    padding: '40px 24px 72px',
    background:
      'radial-gradient(circle at 12% 12%, #fff1f2 0%, #f8fafc 35%, #ecfeff 72%, #e0f2fe 100%)',
    color: '#0f172a',
  };

  const pageWrapStyle: React.CSSProperties = {
    maxWidth: '1240px',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '28px',
  };

  const sectionStyle: React.CSSProperties = {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: '20px',
    padding: '24px',
    border: '1px solid rgba(148, 163, 184, 0.35)',
    boxShadow: '0 18px 32px rgba(15, 23, 42, 0.08)',
  };

  return (
    <div style={containerStyle}>
      <div style={pageWrapStyle}>
        <section
          style={{
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #0f766e 100%)',
            color: 'white',
            borderRadius: '24px',
            padding: '32px',
            boxShadow: '0 28px 52px rgba(15, 23, 42, 0.24)',
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 12px',
              borderRadius: '999px',
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              fontSize: '12px',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
            }}
          >
            국내주식 전용
          </div>
          <h1 style={{ fontSize: '40px', fontWeight: 700, marginTop: '12px' }}>계좌조회</h1>
          <p style={{ marginTop: '10px', fontSize: '16px', lineHeight: 1.7, maxWidth: '720px' }}>
            국내주식 계좌의 잔고 구성, 평가 손익, 현금 흐름을 한 화면에서 확인합니다.
          </p>
          <div
            style={{
              display: 'flex',
              gap: '12px',
              marginTop: '18px',
              flexWrap: 'wrap',
              fontSize: '13px',
              color: 'rgba(226, 232, 240, 0.85)',
            }}
          >
            <span>계좌: {balance ? maskAccount(balance.account_number) : '—'}</span>
            <span>기준 시각: {balance ? toKSTString(balance.timestamp) : '—'}</span>
            <span>데이터: {loading ? '불러오는 중' : '실계좌'}</span>
          </div>
        </section>

        {error ? (
          <section style={sectionStyle}>
            <div style={{ color: '#b91c1c', fontWeight: 600 }}>{error}</div>
          </section>
        ) : null}

        <section style={sectionStyle}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
            <StatCard label="총 평가금액" value={formatKRW(totals.totalEvaluation)} sub="현금 포함" />
            <StatCard label="예수금" value={formatKRW(totals.cashBalance)} sub="주문 가능 현금" />
            <StatCard label="매입금액" value={formatKRW(totals.investmentAmount)} sub="보유 종목 매입 합계" />
            <StatCard
              label="평가손익"
              value={formatSignedKRW(totals.profitLoss)}
              sub={formatSignedPercent(totals.profitLossPercent)}
              accent={colorFor(totals.profitLoss)}
            />
          </div>
        </section>

        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(280px, 1fr) minmax(280px, 1fr)',
            gap: '24px',
          }}
        >
          <div style={sectionStyle}>
            <h2 style={{ fontSize: '20px', fontWeight: 600 }}>계좌 요약</h2>
            <div style={{ display: 'grid', gap: '12px', marginTop: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '15px' }}>
                <span>보유 주식 평가</span>
                <strong>{formatKRW(totals.marketValue)}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '15px' }}>
                <span>예수금</span>
                <strong>{formatKRW(totals.cashBalance)}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '15px' }}>
                <span>매입금액 합계</span>
                <strong>{formatKRW(totals.investmentAmount)}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '15px', color: colorFor(totals.profitLoss) }}>
                <span>평가 손익</span>
                <strong>{formatSignedKRW(totals.profitLoss)}</strong>
              </div>
            </div>
            <div
              style={{
                marginTop: '20px',
                padding: '16px',
                borderRadius: '14px',
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
              }}
            >
              <div style={{ fontSize: '12px', textTransform: 'uppercase', color: '#64748b' }}>총 평가금액</div>
              <div style={{ fontSize: '20px', fontWeight: 700 }}>{formatKRW(totals.totalEvaluation)}</div>
              <div style={{ fontSize: '13px', color: '#64748b' }}>현금 포함</div>
            </div>
          </div>

          <div style={sectionStyle}>
            <h2 style={{ fontSize: '20px', fontWeight: 600 }}>종목 비중</h2>
            <div style={{ display: 'flex', gap: '18px', alignItems: 'center', marginTop: '18px', flexWrap: 'wrap' }}>
              <div
                style={{
                  width: '170px',
                  height: '170px',
                  borderRadius: '50%',
                  background: allocationGradient,
                  position: 'relative',
                  boxShadow: '0 14px 28px rgba(15, 23, 42, 0.12)',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    inset: '22px',
                    borderRadius: '50%',
                    backgroundColor: 'white',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    textAlign: 'center',
                    color: '#334155',
                  }}
                >
                  <div style={{ fontSize: '12px', textTransform: 'uppercase', color: '#94a3b8' }}>보유</div>
                  <div style={{ fontSize: '18px', fontWeight: 700 }}>{enrichedPositions.length} 종목</div>
                </div>
              </div>
              <div style={{ flex: 1, minWidth: '200px', display: 'grid', gap: '10px' }}>
                {enrichedPositions.length === 0 ? (
                  <div style={{ fontSize: '14px', color: '#94a3b8' }}>보유 종목이 없습니다.</div>
                ) : (
                  enrichedPositions.map((position) => {
                    const weight = totals.marketValue ? (position.marketValue / totals.marketValue) * 100 : 0;
                    return (
                      <div key={position.symbol} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span
                          style={{
                            width: '10px',
                            height: '10px',
                            borderRadius: '50%',
                            backgroundColor: position.color,
                          }}
                        />
                        <span style={{ flex: 1, fontSize: '14px' }}>{position.name}</span>
                        <strong style={{ fontSize: '13px', color: '#475569' }}>{weight.toFixed(1)}%</strong>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </section>

        <section style={sectionStyle}>
          <h2 style={{ fontSize: '20px', fontWeight: 600 }}>종목별 손익</h2>
          <div
            style={{
              marginTop: '16px',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
              gap: '12px',
              alignItems: 'end',
            }}
          >
            {enrichedPositions.map((position) => {
              const height = Math.round((Math.abs(position.profitLoss) / plMax) * 72) + 8;
              const barColor = colorFor(position.profitLoss);
              return (
                <div key={position.symbol} style={{ textAlign: 'center' }}>
                  <div
                    style={{
                      height: '88px',
                      display: 'flex',
                      alignItems: 'flex-end',
                      justifyContent: 'center',
                    }}
                  >
                    <div
                      style={{
                        width: '36px',
                        height: `${height}px`,
                        borderRadius: '12px',
                        backgroundColor: barColor,
                        boxShadow: '0 8px 16px rgba(15, 23, 42, 0.1)',
                      }}
                    />
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '12px', color: '#64748b' }}>{position.name}</div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: barColor }}>{formatSignedKRW(position.profitLoss)}</div>
                </div>
              );
            })}
          </div>
        </section>

        <section style={sectionStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 600 }}>보유 종목</h2>
            <div style={{ fontSize: '13px', color: '#64748b' }}>시장가 기준</div>
          </div>
          <div style={{ overflowX: 'auto', marginTop: '16px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '760px' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: '#64748b', fontSize: '12px', textTransform: 'uppercase' }}>
                  <th style={{ padding: '12px 8px' }}>종목</th>
                  <th className="hts-num" style={{ padding: '12px 8px', textAlign: 'right' }}>수량</th>
                  <th className="hts-num" style={{ padding: '12px 8px', textAlign: 'right' }}>평균단가</th>
                  <th className="hts-num" style={{ padding: '12px 8px', textAlign: 'right' }}>현재가</th>
                  <th className="hts-num" style={{ padding: '12px 8px', textAlign: 'right' }}>평가금액</th>
                  <th className="hts-num" style={{ padding: '12px 8px', textAlign: 'right' }}>평가손익</th>
                </tr>
              </thead>
              <tbody>
                {enrichedPositions.map((position) => {
                  const plColor = colorFor(position.profitLoss);
                  return (
                    <tr key={position.symbol} style={{ borderTop: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '14px 8px' }}>
                        <div style={{ fontWeight: 600 }}>{position.name}</div>
                        <div style={{ fontSize: '12px', color: '#94a3b8' }}>{position.symbol}</div>
                      </td>
                      <td className="hts-num" style={{ padding: '14px 8px', textAlign: 'right' }}>{position.quantity.toLocaleString('ko-KR')}주</td>
                      <td className="hts-num" style={{ padding: '14px 8px', textAlign: 'right' }}>{formatKRW(position.average_price)}</td>
                      <td className="hts-num" style={{ padding: '14px 8px', textAlign: 'right' }}>{formatKRW(position.current_price)}</td>
                      <td className="hts-num" style={{ padding: '14px 8px', textAlign: 'right' }}>{formatKRW(position.marketValue)}</td>
                      <td className="hts-num" style={{ padding: '14px 8px', textAlign: 'right', color: plColor }}>
                        {formatSignedKRW(position.profitLoss)}
                        <div style={{ fontSize: '12px', color: plColor }}>{formatSignedPercent(position.profitLossPct)}</div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};
