/**
 * Yield view of a listed bond: yields at last/bid/ask, the pricing
 * agencies' benchmark, rate sensitivity and daily yield history.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { SignedBarChart, TwoLineChart } from './AnalyticsCharts';
import { chartTheme, isoDate } from './chartTheme';
import {
  apiErrorMessage,
  koreanAnalyticsService,
} from '../services/koreanAnalytics';
import type {
  BondReferenceSource,
  KoreanBondAnalytics,
  KoreanBondYieldHistory,
} from '../types/koreanAnalytics';

const HISTORY_RANGES = [
  { value: 60, label: '2개월' },
  { value: 120, label: '4개월' },
  { value: 250, label: '8개월' },
] as const;

const REFERENCE_LABEL: Record<BondReferenceSource, string> = {
  last_trade: '오늘 체결가 기준',
  quote_mid: '매수·매도 호가 중간',
  last_price: '직전 체결가 기준',
  agency: '민평 수익률',
};

const sectionTitle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  color: '#374151',
  margin: '16px 0 8px',
};
/** A grid cell holding a table: scrolls sideways rather than spilling
 * into its neighbour when the table is wider than the cell. */
const tableCell: React.CSSProperties = { minWidth: 0, overflowX: 'auto' };
const th: React.CSSProperties = {
  padding: '6px 10px',
  textAlign: 'right',
  borderBottom: '1px solid #e5e7eb',
  fontWeight: 600,
  color: '#374151',
  whiteSpace: 'nowrap',
};
const td: React.CSSProperties = {
  padding: '6px 10px',
  textAlign: 'right',
  borderBottom: '1px solid #f3f4f6',
  whiteSpace: 'nowrap',
  fontVariantNumeric: 'tabular-nums',
};

const isNumber = (value?: number | null): value is number =>
  value !== null && value !== undefined && Number.isFinite(value);

const formatYield = (value?: number | null) =>
  isNumber(value) ? `${value.toFixed(3)}%` : '-';

const formatPrice = (value?: number | null, digits = 1) =>
  isNumber(value)
    ? value.toLocaleString('ko-KR', {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      })
    : '-';

const formatSigned = (value: number | null | undefined, digits: number, unit = '') =>
  isNumber(value) ? `${value > 0 ? '+' : ''}${value.toFixed(digits)}${unit}` : '-';

const formatCount = (value?: number | null) =>
  isNumber(value) ? value.toLocaleString('ko-KR') : '-';

/** Market yield above the benchmark means the bond is cheaper than it. */
const relativeValueLabel = (spreadBp?: number | null) => {
  if (!isNumber(spreadBp) || Math.abs(spreadBp) < 0.5) return '민평 수준';
  return spreadBp > 0 ? '민평보다 싸게 거래 (수익률 높음)' : '민평보다 비싸게 거래 (수익률 낮음)';
};

const Stat: React.FC<{ label: string; value: string; hint?: string }> = ({
  label,
  value,
  hint,
}) => (
  <div
    style={{
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '10px 12px',
      backgroundColor: '#f9fafb',
    }}
  >
    <div style={{ fontSize: '12px', color: '#6b7280' }}>{label}</div>
    <div
      style={{
        fontSize: '18px',
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

export const BondYieldPanel: React.FC<{ pdno: string }> = ({ pdno }) => {
  const [analytics, setAnalytics] = useState<KoreanBondAnalytics | null>(null);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [history, setHistory] = useState<KoreanBondYieldHistory | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [historyDays, setHistoryDays] = useState<number>(120);

  useEffect(() => {
    let cancelled = false;
    setAnalytics(null);
    setAnalyticsError(null);
    koreanAnalyticsService
      .getBondAnalytics(pdno)
      .then((result) => {
        if (!cancelled) setAnalytics(result);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setAnalyticsError(apiErrorMessage(err, '수익률 분석을 불러오지 못했습니다.'));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [pdno]);

  useEffect(() => {
    let cancelled = false;
    setHistory(null);
    setHistoryError(null);
    koreanAnalyticsService
      .getBondYieldHistory(pdno, historyDays)
      .then((result) => {
        if (!cancelled) setHistory(result);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setHistoryError(apiErrorMessage(err, '수익률 추이를 불러오지 못했습니다.'));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [pdno, historyDays]);

  const yieldLines = useMemo(
    () =>
      (history?.points ?? []).map((point) => ({
        date: point.date,
        first: point.market_yield,
        second: point.agency_yield,
      })),
    [history]
  );
  const spreadBars = useMemo(
    () =>
      (history?.points ?? [])
        .filter((point) => isNumber(point.spread_bp))
        .map((point) => ({ date: point.date, value: point.spread_bp })),
    [history]
  );
  const hasYieldHistory = yieldLines.some(
    (point) => isNumber(point.first) || isNumber(point.second)
  );

  return (
    <div
      style={{
        padding: '12px 16px 16px',
        backgroundColor: '#ffffff',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          flexWrap: 'wrap',
          gap: '8px',
        }}
      >
        <div style={{ fontSize: '15px', fontWeight: 600, color: '#111827' }}>
          수익률 분석
          {analytics?.kind_label && (
            <span style={{ color: '#6b7280', fontWeight: 400, fontSize: '13px' }}>
              {' '}
              · {analytics.kind_label}
              {isNumber(analytics.remaining_years)
                ? ` · 잔존 ${analytics.remaining_years.toFixed(2)}년`
                : ''}
            </span>
          )}
        </div>
        {analytics && (
          <span style={{ color: '#6b7280', fontSize: '12px' }}>
            결제일 {isoDate(analytics.settlement_date)} 기준 · 가격은 액면 10,000원당
            (경과이자 포함)
          </span>
        )}
      </div>

      {analyticsError && (
        <p style={{ color: '#dc2626', fontSize: '13px' }}>{analyticsError}</p>
      )}
      {!analytics && !analyticsError && (
        <p style={{ color: '#6b7280', fontSize: '13px' }}>수익률을 계산하는 중입니다…</p>
      )}

      {analytics && (
        <>
          {analytics.notes.length > 0 && (
            <ul
              style={{
                margin: '10px 0 0',
                padding: '8px 12px 8px 28px',
                backgroundColor: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: '6px',
                fontSize: '13px',
                color: '#78350f',
              }}
            >
              {analytics.notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          )}

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
              gap: '10px',
              marginTop: '12px',
            }}
          >
            <Stat
              label="만기수익률 (YTM)"
              value={formatYield(analytics.reference_yield ?? analytics.last_yield)}
              hint={
                analytics.reference_source
                  ? REFERENCE_LABEL[analytics.reference_source]
                  : analytics.last_yield
                    ? '증권사 제공값'
                    : undefined
              }
            />
            <Stat
              label="세후 수익률"
              value={formatYield(analytics.after_tax_yield)}
              hint={
                isNumber(analytics.tax_rate)
                  ? `이자소득세 ${analytics.tax_rate.toFixed(1)}% 가정`
                  : undefined
              }
            />
            <Stat
              label="민평 수익률"
              value={formatYield(analytics.agency_yield)}
              hint={analytics.agency_date ? `${isoDate(analytics.agency_date)} 평가` : undefined}
            />
            <Stat
              label="민평 대비"
              value={formatSigned(analytics.agency_spread_bp, 1, 'bp')}
              hint={
                isNumber(analytics.agency_spread_bp)
                  ? relativeValueLabel(analytics.agency_spread_bp)
                  : undefined
              }
            />
            <Stat
              label="매수·매도 호가 수익률"
              value={`${formatYield(analytics.best_bid_yield)} / ${formatYield(
                analytics.best_ask_yield
              )}`}
              hint={
                isNumber(analytics.bid_ask_spread_bp)
                  ? `스프레드 ${analytics.bid_ask_spread_bp.toFixed(1)}bp`
                  : undefined
              }
            />
            <Stat
              label="수정 듀레이션"
              value={
                isNumber(analytics.modified_duration)
                  ? `${analytics.modified_duration.toFixed(2)}년`
                  : '-'
              }
              hint={
                isNumber(analytics.macaulay_duration)
                  ? `맥컬리 ${analytics.macaulay_duration.toFixed(2)}년`
                  : undefined
              }
            />
            <Stat
              label="DV01 (1bp당 가격)"
              value={formatPrice(analytics.dv01, 2)}
              hint={
                isNumber(analytics.convexity)
                  ? `볼록성 ${analytics.convexity.toFixed(1)}`
                  : undefined
              }
            />
            <Stat
              label="경과이자"
              value={formatPrice(analytics.accrued_interest, 2)}
              hint={
                isNumber(analytics.clean_price)
                  ? `제외 가격 ${formatPrice(analytics.clean_price, 2)}`
                  : analytics.next_coupon_date
                    ? `다음 이자 ${isoDate(analytics.next_coupon_date)}`
                    : undefined
              }
            />
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))',
              gap: '16px',
            }}
          >
            {analytics.levels.length > 0 && (
              <div style={tableCell}>
                <div style={sectionTitle}>호가별 수익률</div>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f9fafb' }}>
                      <th style={th}>매도잔량</th>
                      <th style={th}>매도 수익률</th>
                      <th style={th}>매도가</th>
                      <th style={th}>매수가</th>
                      <th style={th}>매수 수익률</th>
                      <th style={th}>매수잔량</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.levels.map((level) => (
                      <tr key={level.level}>
                        <td style={td}>{formatCount(level.ask_quantity)}</td>
                        <td style={td}>{formatYield(level.ask_yield)}</td>
                        <td style={td}>{formatPrice(level.ask_price)}</td>
                        <td style={td}>{formatPrice(level.bid_price)}</td>
                        <td style={td}>{formatYield(level.bid_yield)}</td>
                        <td style={td}>{formatCount(level.bid_quantity)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p style={{ color: '#6b7280', fontSize: '12px', margin: '6px 0 0' }}>
                  매도가에 사면 매도 수익률을, 매수가에 팔면 매수 수익률을 확정합니다.
                </p>
              </div>
            )}

            {analytics.scenarios.length > 0 && (
              <div style={tableCell}>
                <div style={sectionTitle}>금리 변동 시 가격</div>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f9fafb' }}>
                      <th style={th}>금리 변동</th>
                      <th style={th}>수익률</th>
                      <th style={th}>가격</th>
                      <th style={th}>가격 변화</th>
                      <th style={th}>변화율</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.scenarios.map((row) => (
                      <tr key={row.shift_bp}>
                        <td style={td}>{formatSigned(row.shift_bp, 0, 'bp')}</td>
                        <td style={td}>{formatYield(row.yield_rate)}</td>
                        <td style={td}>{formatPrice(row.price)}</td>
                        <td style={td}>{formatSigned(row.price_change, 1)}</td>
                        <td style={td}>{formatSigned(row.price_change_percent, 2, '%')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {analytics.agencies.length > 0 && (
              <div style={tableCell}>
                <div style={sectionTitle}>채권평가사별 평가</div>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f9fafb' }}>
                      <th style={{ ...th, textAlign: 'left' }}>평가사</th>
                      <th style={th}>평가수익률</th>
                      <th style={th}>평가단가</th>
                      <th style={th}>신용등급</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.agencies.map((agency) => (
                      <tr key={agency.agency}>
                        <td style={{ ...td, textAlign: 'left' }}>{agency.agency}</td>
                        <td style={td}>{formatYield(agency.yield_rate)}</td>
                        <td style={td}>{formatPrice(agency.price, 2)}</td>
                        <td style={td}>{agency.credit_rating || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {isNumber(analytics.price_vs_agency) && (
                  <p style={{ color: '#6b7280', fontSize: '12px', margin: '6px 0 0' }}>
                    시장 가격이 민평 수익률로 계산한 가격{' '}
                    {formatPrice(analytics.agency_implied_price, 2)}보다{' '}
                    {formatPrice(Math.abs(analytics.price_vs_agency), 2)}원{' '}
                    {analytics.price_vs_agency >= 0 ? '높습니다' : '낮습니다'}.
                  </p>
                )}
              </div>
            )}
          </div>
        </>
      )}

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: '8px',
        }}
      >
        <div style={sectionTitle}>수익률 추이: 시장 vs 민평</div>
        <div style={{ display: 'flex', gap: '6px' }}>
          {HISTORY_RANGES.map((range) => (
            <button
              key={range.value}
              onClick={() => setHistoryDays(range.value)}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '3px 10px',
                fontSize: '12px',
                cursor: 'pointer',
                backgroundColor: historyDays === range.value ? '#0f766e' : 'white',
                color: historyDays === range.value ? 'white' : '#111827',
              }}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {historyError && <p style={{ color: '#dc2626', fontSize: '13px' }}>{historyError}</p>}
      {!history && !historyError && (
        <p style={{ color: '#6b7280', fontSize: '13px' }}>추이를 불러오는 중입니다…</p>
      )}
      {history && !hasYieldHistory && (
        <p style={{ color: '#6b7280', fontSize: '13px' }}>
          조회 기간에 표시할 수익률 데이터가 없습니다.
        </p>
      )}
      {history && hasYieldHistory && (
        <>
          <TwoLineChart
            data={yieldLines}
            firstName="시장 수익률 (거래일 종가)"
            secondName="민평 수익률"
            format={(value) => `${value.toFixed(3)}%`}
            axisFormat={(value) => `${value.toFixed(2)}%`}
            height={240}
            firstDots
          />
          {spreadBars.length > 0 && (
            <>
              <div style={{ ...sectionTitle, marginTop: '8px' }}>
                시장 − 민평 (bp)
                {isNumber(history.average_spread_bp) && (
                  <span style={{ color: '#6b7280', fontWeight: 400 }}>
                    {' '}
                    · 평균 {formatSigned(history.average_spread_bp, 1, 'bp')}, 최근{' '}
                    {formatSigned(history.latest_spread_bp, 1, 'bp')}
                  </span>
                )}
              </div>
              <SignedBarChart
                data={spreadBars}
                name="시장 − 민평"
                positiveLabel="시장 수익률이 더 높음 (싸게 거래)"
                negativeLabel="민평 수익률이 더 높음 (비싸게 거래)"
                positiveColor={chartTheme.series1}
                negativeColor={chartTheme.series2}
                format={(value) => `${value.toFixed(1)}bp`}
                height={150}
              />
            </>
          )}
          <details style={{ marginTop: '8px' }}>
            <summary style={{ cursor: 'pointer', color: '#374151', fontSize: '13px' }}>
              표로 보기 ({history.points.length}일)
            </summary>
            <div style={{ maxHeight: '280px', overflowY: 'auto', marginTop: '8px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f9fafb' }}>
                    <th style={{ ...th, textAlign: 'left' }}>일자</th>
                    <th style={th}>종가</th>
                    <th style={th}>거래량</th>
                    <th style={th}>시장 수익률</th>
                    <th style={th}>민평 수익률</th>
                    <th style={th}>차이</th>
                  </tr>
                </thead>
                <tbody>
                  {[...history.points].reverse().map((point) => (
                    <tr key={point.date}>
                      <td style={{ ...td, textAlign: 'left' }}>{isoDate(point.date)}</td>
                      <td style={td}>{formatPrice(point.close)}</td>
                      <td style={td}>{formatCount(point.volume)}</td>
                      <td style={td}>{formatYield(point.market_yield)}</td>
                      <td style={td}>{formatYield(point.agency_yield)}</td>
                      <td style={td}>{formatSigned(point.spread_bp, 1, 'bp')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
          {history.notes.length > 0 && (
            <p style={{ color: '#6b7280', fontSize: '12px', margin: '8px 0 0' }}>
              {history.notes.join(' ')}
            </p>
          )}
        </>
      )}
    </div>
  );
};
