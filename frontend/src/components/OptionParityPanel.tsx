/**
 * Put-call parity view: the futures price a call and a put at the same
 * strike imply together, against the listed futures and spot.
 */

import React, { useEffect, useState } from 'react';
import { Caption, FigureTable, Notes, Stack } from './BasisParts';
import {
  formatSigned,
  formatSignedPercent,
  isNumber,
  priceDigits,
} from './basisFormat';
import {
  Badge,
  Chip,
  ChipGroup,
  EmptyState,
  Field,
  Notice,
  Panel,
  Select,
  SkeletonPanel,
  StatGrid,
  StatTile,
} from './ui';
import { koreanAnalyticsService } from '../services/koreanAnalytics';
import { color, fontSize, fontWeight, space } from '../theme/tokens';
import type {
  BasisUnderlyingKind,
  KoreanOptionParity,
  OptionParitySource,
} from '../types/koreanAnalytics';
import { toUserMessage } from '../utils/apiError';
import { formatNumber } from '../utils/format';

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

const TITLE = '옵션 합성선물 (풋-콜 패리티)';

/** Rule in front of the first column of each column group. */
const groupStart: React.CSSProperties = { borderLeft: `1px solid ${color.border}` };
const groupTh: React.CSSProperties = { ...groupStart, textAlign: 'center' };
const dim: React.CSSProperties = { color: color.inkDim };

const formatExpiry = (expiry?: string | null) =>
  expiry && expiry.length === 6 ? `${expiry.slice(0, 4)}-${expiry.slice(4)}` : '-';

/** Strikes are listed in halves for the index and whole won for stocks. */
const formatStrike = (value?: number | null) =>
  isNumber(value) ? value.toLocaleString('ko-KR', { maximumFractionDigits: 2 }) : '-';

/**
 * A positive edge is money on the table; anything else is just the spread.
 * Weight and ink carry the difference: an edge is not a price change, so it
 * takes no up/down colour.
 */
const edgeStyle = (value?: number | null): React.CSSProperties =>
  isNumber(value) && value > 0
    ? { color: color.ink, fontWeight: fontWeight.bold }
    : dim;

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
          setError(toUserMessage(err, '옵션 시세를 불러오지 못했습니다.'));
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [underlying, expiry, rate, strikes, refreshToken]);

  if (!parity) {
    return (
      <Panel
        title={TITLE}
        note={
          error
            ? undefined
            : '옵션 시세를 불러오는 중입니다… 행사가마다 호가를 조회해 몇 초 걸립니다.'
        }
      >
        {error ? <Notice>{error}</Notice> : <SkeletonPanel rows={4} height={20} />}
      </Panel>
    );
  }

  if (parity.expiries.length === 0) {
    return (
      <EmptyState>
        <strong style={{ color: color.inkMid }}>옵션 합성선물</strong> ·{' '}
        {parity.underlying_name}에는 상장된 월물 옵션이 없습니다.
      </EmptyState>
    );
  }

  const digits = priceDigits(kind);
  const summary = parity.summary;
  const hasFutures = isNumber(parity.futures_price);
  const pair = (bid?: number | null, ask?: number | null) =>
    `${formatNumber(bid, digits)} / ${formatNumber(ask, digits)}`;

  return (
    <Panel
      title={TITLE}
      note={
        <>
          {formatExpiry(parity.expiry)} 만기
          {isNumber(parity.days_to_expiry) ? ` · 잔존 ${parity.days_to_expiry}일` : ''}
          {isNumber(parity.rate)
            ? ` · 콜 − 풋은 연 ${parity.rate.toFixed(2)}%${RATE_LABEL[parity.rate_source]}로 만기까지 환산`
            : ''}
        </>
      }
      actions={
        <>
          {loading && <span style={{ ...dim, fontSize: fontSize.md }}>조회중…</span>}
          <Field label="만기" inline>
            <Select value={parity.expiry ?? ''} onChange={(e) => setExpiry(e.target.value)}>
              {parity.expiries.map((month) => (
                <option key={month} value={month}>
                  {formatExpiry(month)}
                </option>
              ))}
            </Select>
          </Field>
          <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
            <span
              style={{
                fontSize: fontSize.md,
                fontWeight: fontWeight.medium,
                color: color.inkMid,
              }}
            >
              행사가
            </span>
            <ChipGroup label="행사가 개수">
              {STRIKE_CHOICES.map((count) => (
                <Chip key={count} active={strikes === count} onClick={() => setStrikes(count)}>
                  {count}개
                </Chip>
              ))}
            </ChipGroup>
          </div>
        </>
      }
    >
      <Stack>
        <p
          style={{
            margin: 0,
            fontSize: fontSize.md,
            lineHeight: 1.5,
            color: color.inkMid,
          }}
        >
          같은 행사가의 콜을 사고 풋을 팔면 선물을 산 것과 손익이 같습니다. 그래서 행사가
          + (콜 − 풋)이 옵션 시장이 매긴 선물 가격이고, 이를 실제 선물·현물과 비교합니다.
        </p>

        <StatGrid minWidth={190}>
          <StatTile
            label="합성선물"
            value={formatNumber(summary?.synthetic, digits)}
            sub={
              summary?.source
                ? `${SOURCE_LABEL[summary.source]} 기준 · ${summary.strike_count}개 행사가 중앙값`
                : '계산할 수 있는 행사가 없음'
            }
          />
          <StatTile
            label="선물 대비 (합성 − 선물)"
            value={formatSigned(summary?.futures_gap, digits)}
            sub={
              hasFutures
                ? `${
                    isNumber(summary?.futures_gap_percent)
                      ? `${formatSignedPercent(summary.futures_gap_percent)} · `
                      : ''
                  }${parity.futures_name ?? '선물'} ${formatNumber(parity.futures_price, digits)}`
                : '같은 만기 선물 없음'
            }
          />
          <StatTile
            label="현물 대비 (합성 − 현물)"
            value={formatSigned(summary?.spot_basis, digits)}
            sub={
              isNumber(summary?.spot_basis_percent)
                ? `${formatSignedPercent(summary.spot_basis_percent)} · 내재금리 ${formatSignedPercent(
                    summary.implied_rate
                  )}`
                : `현물 ${formatNumber(parity.spot, digits)}`
            }
          />
          <StatTile
            label="컨버전 (합성 매도 + 선물 매수)"
            value={formatSigned(summary?.conversion_edge, digits)}
            sub={edgeHint(summary?.conversion_edge, summary?.conversion_strike, hasFutures)}
          />
          <StatTile
            label="리버설 (합성 매수 + 선물 매도)"
            value={formatSigned(summary?.reversal_edge, digits)}
            sub={edgeHint(summary?.reversal_edge, summary?.reversal_strike, hasFutures)}
          />
        </StatGrid>

        <Notes notes={parity.notes} />

        <div>
          <FigureTable>
            <thead>
              <tr>
                <th rowSpan={2}>행사가</th>
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
              <tr>
                <th className="hts-num" style={groupStart}>
                  체결가 (거래량)
                </th>
                <th className="hts-num">매수 / 매도</th>
                <th className="hts-num" style={groupStart}>
                  체결가 (거래량)
                </th>
                <th className="hts-num">매수 / 매도</th>
                <th className="hts-num" style={groupStart}>
                  가격
                </th>
                <th>기준</th>
                <th className="hts-num">선물 대비</th>
                <th className="hts-num">현물 대비</th>
                <th className="hts-num">매도 / 매수</th>
                <th className="hts-num" style={groupStart}>
                  컨버전
                </th>
                <th className="hts-num">리버설</th>
              </tr>
            </thead>
            <tbody>
              {parity.rows.map((row) => (
                <tr
                  key={row.strike}
                  style={row.is_atm ? { backgroundColor: color.surfaceSunken } : undefined}
                >
                  <td>
                    <strong>{formatStrike(row.strike)}</strong>
                    {row.is_atm && (
                      <>
                        {' '}
                        <Badge tone="accent">ATM</Badge>
                      </>
                    )}
                  </td>
                  <td className="hts-num" style={groupStart}>
                    {formatNumber(row.call_last, digits)}{' '}
                    <span style={dim}>({formatNumber(row.call_volume)})</span>
                  </td>
                  <td className="hts-num">{pair(row.call_bid, row.call_ask)}</td>
                  <td className="hts-num" style={groupStart}>
                    {formatNumber(row.put_last, digits)}{' '}
                    <span style={dim}>({formatNumber(row.put_volume)})</span>
                  </td>
                  <td className="hts-num">{pair(row.put_bid, row.put_ask)}</td>
                  <td
                    className="hts-num"
                    style={{ ...groupStart, fontWeight: fontWeight.semibold }}
                  >
                    {formatNumber(row.synthetic, digits)}
                  </td>
                  <td style={dim}>{row.source ? SOURCE_LABEL[row.source] : '-'}</td>
                  <td className="hts-num">
                    {formatSigned(row.futures_gap, digits)}{' '}
                    {isNumber(row.futures_gap_percent) && (
                      <span style={dim}>{formatSignedPercent(row.futures_gap_percent)}</span>
                    )}
                  </td>
                  <td className="hts-num">{formatSigned(row.spot_basis, digits)}</td>
                  <td className="hts-num">{pair(row.synthetic_bid, row.synthetic_ask)}</td>
                  <td
                    className="hts-num"
                    style={{ ...groupStart, ...edgeStyle(row.conversion_edge) }}
                  >
                    {formatSigned(row.conversion_edge, digits)}
                  </td>
                  <td className="hts-num" style={edgeStyle(row.reversal_edge)}>
                    {formatSigned(row.reversal_edge, digits)}
                  </td>
                </tr>
              ))}
            </tbody>
          </FigureTable>
          <Caption>
            합성선물 가격은 콜·풋 호가가 모두 양쪽에 있고 간격이 좁으면 호가 중간값, 아니면
            오늘 체결가로 계산합니다. 컨버전·리버설은 호가대로 체결했을 때 수수료·세금 전
            손익으로, 0보다 크면 옵션과 선물 사이에 차익거래 여지가 있다는 뜻입니다. 월물
            옵션만 다루며 미니·위클리 옵션은 포함하지 않습니다.
          </Caption>
        </div>
      </Stack>
    </Panel>
  );
};
