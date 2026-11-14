/**
 * Put-call parity view: the futures price a call and a put at the same
 * strike imply together, against the listed futures and spot.
 */

import React, { useEffect, useState } from 'react';
import { Notes, Stat } from './BasisParts';
import {
  card,
  formatCount,
  formatPrice,
  formatSigned,
  formatSignedPercent,
  isNumber,
  priceDigits,
  td,
  th,
} from './basisFormat';
import {
  apiErrorMessage,
  koreanAnalyticsService,
} from '../services/koreanAnalytics';
import type {
  BasisUnderlyingKind,
  KoreanOptionParity,
  OptionParitySource,
} from '../types/koreanAnalytics';

const STRIKE_CHOICES = [5, 9, 13] as const;

const SOURCE_LABEL: Record<OptionParitySource, string> = {
  quote: '호가 중간',
  last: '체결가',
  wide_quote: '넓은 호가',
};

/** Where the rate that carries the net premium to expiry came from. */
const RATE_LABEL: Record<KoreanOptionParity['rate_source'], string> = {
  user: ' (입력한 금리)',
  futures_carry: ' (선물 이론가에 내재된 보유비용률)',
  none: '',
};

const groupTh: React.CSSProperties = {
  ...th,
  textAlign: 'center',
  borderLeft: '1px solid #e5e7eb',
};
const groupStart: React.CSSProperties = { borderLeft: '1px solid #e5e7eb' };
const muted: React.CSSProperties = { color: '#6b7280' };

const formatExpiry = (expiry?: string | null) =>
  expiry && expiry.length === 6 ? `${expiry.slice(0, 4)}-${expiry.slice(4)}` : '-';

/** Strikes are listed in halves for the index and whole won for stocks. */
const formatStrike = (value?: number | null) =>
  isNumber(value) ? value.toLocaleString('ko-KR', { maximumFractionDigits: 2 }) : '-';

/** A positive edge is money on the table; anything else is just the spread. */
const edgeStyle = (value?: number | null): React.CSSProperties =>
  isNumber(value) && value > 0 ? { color: '#047857', fontWeight: 600 } : muted;

const edgeHint = (
  edge: number | null | undefined,
  strike: number | null | undefined,
  hasFutures: boolean
) => {
  if (!hasFutures) return '같은 만기 선물 없음';
  if (!isNumber(edge)) return '콜·풋 모두 양쪽 호가인 행사가 없음';
  return `행사가 ${formatStrike(strike)} · ${edge > 0 ? '차익 여지 (비용 전)' : '차익 없음'}`;
};

type OptionParityPanelProps = {
  underlying: string;
  kind: BasisUnderlyingKind;
  /** Financing rate typed on the page; the broker's carry rate when unset. */
  rate?: number;
  /** Changes whenever the page reloads its quotes, to reload these too. */
  refreshToken: string;
};

export const OptionParityPanel: React.FC<OptionParityPanelProps> = ({
  underlying,
  kind,
  rate,
  refreshToken,
}) => {
  const [parity, setParity] = useState<KoreanOptionParity | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expiry, setExpiry] = useState<string | undefined>(undefined);
  const [strikes, setStrikes] = useState<number>(9);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    koreanAnalyticsService
      .getOptionParity(underlying, { expiry, rate, strikes })
      .then((result) => {
        if (!cancelled) setParity(result);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setParity(null);
          setError(apiErrorMessage(err, '옵션 시세를 불러오지 못했습니다.'));
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [underlying, expiry, rate, strikes, refreshToken]);

  const title = <h2 style={{ margin: 0, fontSize: '18px' }}>옵션 합성선물 (풋-콜 패리티)</h2>;

  if (!parity) {
    return (
      <section style={card}>
        {title}
        {error ? (
          <p style={{ color: '#dc2626', marginBottom: 0 }}>{error}</p>
        ) : (
          <p style={{ ...muted, marginBottom: 0 }}>
            옵션 시세를 불러오는 중입니다… 행사가마다 호가를 조회해 몇 초 걸립니다.
          </p>
        )}
      </section>
    );
  }

  if (parity.expiries.length === 0) {
    return (
      <section style={{ ...card, ...muted, fontSize: '13px' }}>
        <strong style={{ color: '#374151' }}>옵션 합성선물</strong> ·{' '}
        {parity.underlying_name}에는 상장된 월물 옵션이 없습니다.
      </section>
    );
  }

  const digits = priceDigits(kind);
  const summary = parity.summary;
  const hasFutures = isNumber(parity.futures_price);
  const pair = (bid?: number | null, ask?: number | null) =>
    `${formatPrice(bid, digits)} / ${formatPrice(ask, digits)}`;

  return (
    <section style={card}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '8px',
        }}
      >
        {title}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {loading && <span style={{ ...muted, fontSize: '13px' }}>조회중…</span>}
          <label style={{ ...muted, fontSize: '13px' }}>
            만기{' '}
            <select
              value={parity.expiry ?? ''}
              onChange={(e) => setExpiry(e.target.value)}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '13px',
                color: '#111827',
                backgroundColor: 'white',
              }}
            >
              {parity.expiries.map((month) => (
                <option key={month} value={month}>
                  {formatExpiry(month)}
                </option>
              ))}
            </select>
          </label>
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ ...muted, fontSize: '13px' }}>행사가</span>
            {STRIKE_CHOICES.map((count) => (
              <button
                key={count}
                onClick={() => setStrikes(count)}
                style={{
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  padding: '4px 10px',
                  fontSize: '13px',
                  cursor: 'pointer',
                  backgroundColor: strikes === count ? '#1d4ed8' : 'white',
                  color: strikes === count ? 'white' : '#111827',
                }}
              >
                {count}개
              </button>
            ))}
          </div>
        </div>
      </div>
      <p style={{ ...muted, fontSize: '13px', margin: '8px 0 0' }}>
        같은 행사가의 콜을 사고 풋을 팔면 선물을 산 것과 손익이 같습니다. 그래서 행사가
        + (콜 − 풋)이 옵션 시장이 매긴 선물 가격이고, 이를 실제 선물·현물과 비교합니다.
        {' '}
        {formatExpiry(parity.expiry)} 만기
        {isNumber(parity.days_to_expiry) ? ` · 잔존 ${parity.days_to_expiry}일` : ''}
        {isNumber(parity.rate)
          ? ` · 콜 − 풋은 연 ${parity.rate.toFixed(2)}%${RATE_LABEL[parity.rate_source]}로 만기까지 환산`
          : ''}
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
          gap: '12px',
          marginTop: '12px',
        }}
      >
        <Stat
          label="합성선물"
          value={formatPrice(summary?.synthetic, digits)}
          hint={
            summary?.source
              ? `${SOURCE_LABEL[summary.source]} 기준 · ${summary.strike_count}개 행사가 중앙값`
              : '계산할 수 있는 행사가 없음'
          }
        />
        <Stat
          label="선물 대비 (합성 − 선물)"
          value={formatSigned(summary?.futures_gap, digits)}
          hint={
            hasFutures
              ? `${
                  isNumber(summary?.futures_gap_percent)
                    ? `${formatSignedPercent(summary.futures_gap_percent)} · `
                    : ''
                }${parity.futures_name ?? '선물'} ${formatPrice(parity.futures_price, digits)}`
              : '같은 만기 선물 없음'
          }
        />
        <Stat
          label="현물 대비 (합성 − 현물)"
          value={formatSigned(summary?.spot_basis, digits)}
          hint={
            isNumber(summary?.spot_basis_percent)
              ? `${formatSignedPercent(summary.spot_basis_percent)} · 내재금리 ${formatSignedPercent(
                  summary.implied_rate
                )}`
              : `현물 ${formatPrice(parity.spot, digits)}`
          }
        />
        <Stat
          label="컨버전 (합성 매도 + 선물 매수)"
          value={formatSigned(summary?.conversion_edge, digits)}
          hint={edgeHint(summary?.conversion_edge, summary?.conversion_strike, hasFutures)}
        />
        <Stat
          label="리버설 (합성 매수 + 선물 매도)"
          value={formatSigned(summary?.reversal_edge, digits)}
          hint={edgeHint(summary?.reversal_edge, summary?.reversal_strike, hasFutures)}
        />
      </div>

      <Notes notes={parity.notes} />

      <div style={{ overflowX: 'auto', marginTop: '16px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ ...th, textAlign: 'left' }} rowSpan={2}>
                행사가
              </th>
              <th style={groupTh} colSpan={2}>
                콜
              </th>
              <th style={groupTh} colSpan={2}>
                풋
              </th>
              <th style={groupTh} colSpan={5}>
                합성선물
              </th>
              <th style={groupTh} colSpan={2}>
                차익 (비용 전)
              </th>
            </tr>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ ...th, ...groupStart }}>체결가 (거래량)</th>
              <th style={th}>매수 / 매도</th>
              <th style={{ ...th, ...groupStart }}>체결가 (거래량)</th>
              <th style={th}>매수 / 매도</th>
              <th style={{ ...th, ...groupStart }}>가격</th>
              <th style={{ ...th, textAlign: 'left' }}>기준</th>
              <th style={th}>선물 대비</th>
              <th style={th}>현물 대비</th>
              <th style={th}>매도 / 매수</th>
              <th style={{ ...th, ...groupStart }}>컨버전</th>
              <th style={th}>리버설</th>
            </tr>
          </thead>
          <tbody>
            {parity.rows.map((row) => (
              <tr
                key={row.strike}
                style={{ backgroundColor: row.is_atm ? '#f9fafb' : undefined }}
              >
                <td style={{ ...td, textAlign: 'left' }}>
                  <strong>{formatStrike(row.strike)}</strong>
                  {row.is_atm && <span style={{ ...muted, fontSize: '11px' }}> ATM</span>}
                </td>
                <td style={{ ...td, ...groupStart }}>
                  {formatPrice(row.call_last, digits)}{' '}
                  <span style={muted}>({formatCount(row.call_volume)})</span>
                </td>
                <td style={td}>{pair(row.call_bid, row.call_ask)}</td>
                <td style={{ ...td, ...groupStart }}>
                  {formatPrice(row.put_last, digits)}{' '}
                  <span style={muted}>({formatCount(row.put_volume)})</span>
                </td>
                <td style={td}>{pair(row.put_bid, row.put_ask)}</td>
                <td style={{ ...td, ...groupStart, fontWeight: 600 }}>
                  {formatPrice(row.synthetic, digits)}
                </td>
                <td style={{ ...td, ...muted, textAlign: 'left' }}>
                  {row.source ? SOURCE_LABEL[row.source] : '-'}
                </td>
                <td style={td}>
                  {formatSigned(row.futures_gap, digits)}{' '}
                  {isNumber(row.futures_gap_percent) && (
                    <span style={muted}>{formatSignedPercent(row.futures_gap_percent)}</span>
                  )}
                </td>
                <td style={td}>{formatSigned(row.spot_basis, digits)}</td>
                <td style={td}>{pair(row.synthetic_bid, row.synthetic_ask)}</td>
                <td style={{ ...td, ...groupStart, ...edgeStyle(row.conversion_edge) }}>
                  {formatSigned(row.conversion_edge, digits)}
                </td>
                <td style={{ ...td, ...edgeStyle(row.reversal_edge) }}>
                  {formatSigned(row.reversal_edge, digits)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p style={{ ...muted, fontSize: '12px', margin: '8px 0 0' }}>
        합성선물 가격은 콜·풋 호가가 모두 양쪽에 있고 간격이 좁으면 호가 중간값, 아니면
        오늘 체결가로 계산합니다. 컨버전·리버설은 호가대로 체결했을 때 수수료·세금 전
        손익으로, 0보다 크면 옵션과 선물 사이에 차익거래 여지가 있다는 뜻입니다. 월물
        옵션만 다루며 미니·위클리 옵션은 포함하지 않습니다.
      </p>
    </section>
  );
};
