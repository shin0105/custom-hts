/**
 * Yield view of a listed bond: yields at last/bid/ask, the pricing
 * agencies' benchmark, rate sensitivity and daily yield history.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { SignedBarChart, TwoLineChart } from './AnalyticsCharts';
import {
  Caption,
  Disclosure,
  FigureTable,
  Notes,
  Stack,
  SubHeading,
} from './BasisParts';
import { formatSigned, formatSignedPercent, isNumber } from './basisFormat';
import { chartTheme } from './chartTheme';
import {
  Badge,
  Chip,
  ChipGroup,
  EmptyState,
  Notice,
  Panel,
  SkeletonPanel,
  StatGrid,
  StatTile,
} from './ui';
import { koreanAnalyticsService } from '../services/koreanAnalytics';
import { useMarketColors } from '../theme/marketColorContext';
import { space } from '../theme/tokens';
import type {
  BondReferenceSource,
  KoreanBondAnalytics,
  KoreanBondYieldHistory,
} from '../types/koreanAnalytics';
import { toUserMessage } from '../utils/apiError';
import { formatNumber, formatYyyymmdd } from '../utils/format';

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

/** A grid cell holding a table: the table scrolls sideways inside the cell
 * rather than spilling into its neighbour. */
const tableCell: React.CSSProperties = { minWidth: 0 };

const formatYield = (value?: number | null) =>
  isNumber(value) ? `${value.toFixed(3)}%` : '-';

/** Market yield above the benchmark means the bond is cheaper than it. */
const relativeValueLabel = (spreadBp?: number | null) => {
  if (!isNumber(spreadBp) || Math.abs(spreadBp) < 0.5) return '민평 수준';
  return spreadBp > 0 ? '민평보다 싸게 거래 (수익률 높음)' : '민평보다 비싸게 거래 (수익률 낮음)';
};

/**
 * Renders two panels — the analysis and its history — as siblings, so place
 * it straight inside a page's panel stack.
 */
export const BondYieldPanel: React.FC<{ pdno: string }> = ({ pdno }) => {
  const { colorFor } = useMarketColors();
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
          setAnalyticsError(toUserMessage(err, '수익률 분석을 불러오지 못했습니다.'));
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
          setHistoryError(toUserMessage(err, '수익률 추이를 불러오지 못했습니다.'));
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
    <>
      <Panel
        title="수익률 분석"
        note={
          analytics
            ? `결제일 ${formatYyyymmdd(analytics.settlement_date)} 기준 · 가격은 액면 10,000원당 (경과이자 포함)`
            : analyticsError
              ? undefined
              : '수익률을 계산하는 중입니다…'
        }
        actions={
          analytics?.kind_label ? (
            <Badge>
              {analytics.kind_label}
              {isNumber(analytics.remaining_years)
                ? ` · 잔존 ${analytics.remaining_years.toFixed(2)}년`
                : ''}
            </Badge>
          ) : undefined
        }
      >
        {analyticsError && <Notice>{analyticsError}</Notice>}
        {!analytics && !analyticsError && <SkeletonPanel rows={4} height={20} />}

        {analytics && (
          <Stack>
            <Notes notes={analytics.notes} />

            <StatGrid minWidth={170}>
              <StatTile
                label="만기수익률 (YTM)"
                value={formatYield(analytics.reference_yield ?? analytics.last_yield)}
                sub={
                  analytics.reference_source
                    ? REFERENCE_LABEL[analytics.reference_source]
                    : analytics.last_yield
                      ? '증권사 제공값'
                      : undefined
                }
              />
              <StatTile
                label="세후 수익률"
                value={formatYield(analytics.after_tax_yield)}
                sub={
                  isNumber(analytics.tax_rate)
                    ? `이자소득세 ${analytics.tax_rate.toFixed(1)}% 가정`
                    : undefined
                }
              />
              <StatTile
                label="민평 수익률"
                value={formatYield(analytics.agency_yield)}
                sub={
                  analytics.agency_date
                    ? `${formatYyyymmdd(analytics.agency_date)} 평가`
                    : undefined
                }
              />
              <StatTile
                label="민평 대비"
                value={formatSigned(analytics.agency_spread_bp, 1, 'bp')}
                sub={
                  isNumber(analytics.agency_spread_bp)
                    ? relativeValueLabel(analytics.agency_spread_bp)
                    : undefined
                }
              />
              <StatTile
                label="매수·매도 호가 수익률"
                value={`${formatYield(analytics.best_bid_yield)} / ${formatYield(
                  analytics.best_ask_yield
                )}`}
                sub={
                  isNumber(analytics.bid_ask_spread_bp)
                    ? `스프레드 ${analytics.bid_ask_spread_bp.toFixed(1)}bp`
                    : undefined
                }
              />
              <StatTile
                label="수정 듀레이션"
                value={
                  isNumber(analytics.modified_duration)
                    ? `${analytics.modified_duration.toFixed(2)}년`
                    : '-'
                }
                sub={
                  isNumber(analytics.macaulay_duration)
                    ? `맥컬리 ${analytics.macaulay_duration.toFixed(2)}년`
                    : undefined
                }
              />
              <StatTile
                label="DV01 (1bp당 가격)"
                value={formatNumber(analytics.dv01, 2)}
                sub={
                  isNumber(analytics.convexity)
                    ? `볼록성 ${analytics.convexity.toFixed(1)}`
                    : undefined
                }
              />
              <StatTile
                label="경과이자"
                value={formatNumber(analytics.accrued_interest, 2)}
                sub={
                  isNumber(analytics.clean_price)
                    ? `제외 가격 ${formatNumber(analytics.clean_price, 2)}`
                    : analytics.next_coupon_date
                      ? `다음 이자 ${formatYyyymmdd(analytics.next_coupon_date)}`
                      : undefined
                }
              />
            </StatGrid>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(min(440px, 100%), 1fr))',
                gap: space.lg,
              }}
            >
              {analytics.levels.length > 0 && (
                <div style={tableCell}>
                  <SubHeading>호가별 수익률</SubHeading>
                  <FigureTable>
                    <thead>
                      <tr>
                        <th className="hts-num">매도잔량</th>
                        <th className="hts-num">매도 수익률</th>
                        <th className="hts-num">매도가</th>
                        <th className="hts-num">매수가</th>
                        <th className="hts-num">매수 수익률</th>
                        <th className="hts-num">매수잔량</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analytics.levels.map((level) => (
                        <tr key={level.level}>
                          <td className="hts-num">{formatNumber(level.ask_quantity)}</td>
                          <td className="hts-num">{formatYield(level.ask_yield)}</td>
                          <td className="hts-num">{formatNumber(level.ask_price, 1)}</td>
                          <td className="hts-num">{formatNumber(level.bid_price, 1)}</td>
                          <td className="hts-num">{formatYield(level.bid_yield)}</td>
                          <td className="hts-num">{formatNumber(level.bid_quantity)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </FigureTable>
                  <Caption>
                    매도가에 사면 매도 수익률을, 매수가에 팔면 매수 수익률을 확정합니다.
                  </Caption>
                </div>
              )}

              {analytics.scenarios.length > 0 && (
                <div style={tableCell}>
                  <SubHeading>금리 변동 시 가격</SubHeading>
                  <FigureTable>
                    <thead>
                      <tr>
                        <th className="hts-num">금리 변동</th>
                        <th className="hts-num">수익률</th>
                        <th className="hts-num">가격</th>
                        <th className="hts-num">가격 변화</th>
                        <th className="hts-num">변화율</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analytics.scenarios.map((row) => (
                        <tr key={row.shift_bp}>
                          <td className="hts-num">{formatSigned(row.shift_bp, 0, 'bp')}</td>
                          <td className="hts-num">{formatYield(row.yield_rate)}</td>
                          <td className="hts-num">{formatNumber(row.price, 1)}</td>
                          <td
                            className="hts-num"
                            style={{ color: colorFor(row.price_change) }}
                          >
                            {formatSigned(row.price_change, 1)}
                          </td>
                          <td
                            className="hts-num"
                            style={{ color: colorFor(row.price_change) }}
                          >
                            {formatSignedPercent(row.price_change_percent)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </FigureTable>
                </div>
              )}

              {analytics.agencies.length > 0 && (
                <div style={tableCell}>
                  <SubHeading>채권평가사별 평가</SubHeading>
                  <FigureTable>
                    <thead>
                      <tr>
                        <th>평가사</th>
                        <th className="hts-num">평가수익률</th>
                        <th className="hts-num">평가단가</th>
                        <th className="hts-num">신용등급</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analytics.agencies.map((agency) => (
                        <tr key={agency.agency}>
                          <td>{agency.agency}</td>
                          <td className="hts-num">{formatYield(agency.yield_rate)}</td>
                          <td className="hts-num">{formatNumber(agency.price, 2)}</td>
                          <td className="hts-num">{agency.credit_rating || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </FigureTable>
                  {isNumber(analytics.price_vs_agency) && (
                    <Caption>
                      시장 가격이 민평 수익률로 계산한 가격{' '}
                      {formatNumber(analytics.agency_implied_price, 2)}보다{' '}
                      {formatNumber(Math.abs(analytics.price_vs_agency), 2)}원{' '}
                      {analytics.price_vs_agency >= 0 ? '높습니다' : '낮습니다'}.
                    </Caption>
                  )}
                </div>
              )}
            </div>
          </Stack>
        )}
      </Panel>

      <Panel
        title="수익률 추이: 시장 vs 민평"
        note={!history && !historyError ? '추이를 불러오는 중입니다…' : undefined}
        actions={
          <ChipGroup label="조회 기간">
            {HISTORY_RANGES.map((range) => (
              <Chip
                key={range.value}
                active={historyDays === range.value}
                onClick={() => setHistoryDays(range.value)}
              >
                {range.label}
              </Chip>
            ))}
          </ChipGroup>
        }
      >
        {historyError && <Notice>{historyError}</Notice>}
        {!history && !historyError && <SkeletonPanel rows={4} height={40} />}
        {history && !hasYieldHistory && (
          <EmptyState>조회 기간에 표시할 수익률 데이터가 없습니다.</EmptyState>
        )}
        {history && hasYieldHistory && (
          <Stack>
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
              <div>
                <SubHeading
                  note={
                    isNumber(history.average_spread_bp)
                      ? `· 평균 ${formatSigned(history.average_spread_bp, 1, 'bp')}, 최근 ${formatSigned(
                          history.latest_spread_bp,
                          1,
                          'bp'
                        )}`
                      : undefined
                  }
                >
                  시장 − 민평 (bp)
                </SubHeading>
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
              </div>
            )}
            <div>
              <Disclosure summary={`표로 보기 (${history.points.length}일)`}>
                <FigureTable maxHeight={280}>
                  <thead>
                    <tr>
                      <th>일자</th>
                      <th className="hts-num">종가</th>
                      <th className="hts-num">거래량</th>
                      <th className="hts-num">시장 수익률</th>
                      <th className="hts-num">민평 수익률</th>
                      <th className="hts-num">차이</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...history.points].reverse().map((point) => (
                      <tr key={point.date}>
                        <td>{formatYyyymmdd(point.date)}</td>
                        <td className="hts-num">{formatNumber(point.close, 1)}</td>
                        <td className="hts-num">{formatNumber(point.volume)}</td>
                        <td className="hts-num">{formatYield(point.market_yield)}</td>
                        <td className="hts-num">{formatYield(point.agency_yield)}</td>
                        <td className="hts-num">{formatSigned(point.spread_bp, 1, 'bp')}</td>
                      </tr>
                    ))}
                  </tbody>
                </FigureTable>
              </Disclosure>
              {history.notes.length > 0 && <Caption>{history.notes.join(' ')}</Caption>}
            </div>
          </Stack>
        )}
      </Panel>
    </>
  );
};
