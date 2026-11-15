/**
 * Basis between listed futures and their underlying stock or index.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { SignedBarChart, TwoLineChart } from '../components/AnalyticsCharts';
import {
  Caption,
  Disclosure,
  FigureTable,
  Notes,
  Stack,
  SubHeading,
} from '../components/BasisParts';
import {
  formatSigned,
  formatSignedPercent,
  isNumber,
  priceDigits,
} from '../components/basisFormat';
import { chartTheme } from '../components/chartTheme';
import { OptionParityPanel } from '../components/OptionParityPanel';
import {
  Badge,
  Button,
  Chip,
  ChipGroup,
  EmptyState,
  Field,
  Notice,
  Panel,
  SectionHeader,
  SkeletonPanel,
  StatGrid,
  StatTile,
  TextInput,
} from '../components/ui';
import { koreanAnalyticsService } from '../services/koreanAnalytics';
import {
  color,
  fontSize,
  fontWeight,
  radius,
  shadow,
  space,
  zIndex,
} from '../theme/tokens';
import type {
  KoreanBasisContract,
  KoreanBasisHistory,
  KoreanBasisSnapshot,
  KoreanBasisUnderlying,
} from '../types/koreanAnalytics';
import { toUserMessage } from '../utils/apiError';
import { formatNumber, formatYyyymmdd } from '../utils/format';

const HISTORY_RANGES = [
  { value: 30, label: '1개월' },
  { value: 90, label: '3개월' },
  { value: 180, label: '6개월' },
] as const;

const QUICK_PICKS = ['2001', '3003', '005930', '000660'];
const MAX_SUGGESTIONS = 8;

const dim: React.CSSProperties = { color: color.inkDim };

const valuationLabel = (discrepancy?: number | null) => {
  if (!isNumber(discrepancy) || Math.abs(discrepancy) < 0.005) return '';
  return discrepancy > 0 ? '선물 고평가' : '선물 저평가';
};

export const BasisPage: React.FC = () => {
  const [underlyings, setUnderlyings] = useState<KoreanBasisUnderlying[]>([]);
  const [listError, setListError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selected, setSelected] = useState<KoreanBasisUnderlying | null>(null);
  const [rateInput, setRateInput] = useState('');
  const [dividendInput, setDividendInput] = useState('');
  const [snapshot, setSnapshot] = useState<KoreanBasisSnapshot | null>(null);
  const [snapshotLoading, setSnapshotLoading] = useState(false);
  const [snapshotError, setSnapshotError] = useState<string | null>(null);
  const [historySymbol, setHistorySymbol] = useState<string | null>(null);
  const [historyDays, setHistoryDays] = useState<number>(90);
  const [history, setHistory] = useState<KoreanBasisHistory | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const snapshotRequest = useRef(0);
  const historyRequest = useRef(0);

  useEffect(() => {
    koreanAnalyticsService
      .getBasisUnderlyings()
      .then(setUnderlyings)
      .catch((err: unknown) =>
        setListError(toUserMessage(err, '기초자산 목록을 불러오지 못했습니다.'))
      );
  }, []);

  const suggestions = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return [];
    return underlyings
      .filter(
        (item) =>
          item.code.toLowerCase().includes(needle) ||
          item.name.toLowerCase().includes(needle)
      )
      .slice(0, MAX_SUGGESTIONS);
  }, [search, underlyings]);

  const quickPicks = useMemo(
    () =>
      QUICK_PICKS.map((code) => underlyings.find((item) => item.code === code)).filter(
        (item): item is KoreanBasisUnderlying => Boolean(item)
      ),
    [underlyings]
  );

  const loadSnapshot = useCallback(
    async (underlying: KoreanBasisUnderlying, rateText: string, dividendText: string) => {
      const requestId = ++snapshotRequest.current;
      const rate = rateText.trim() === '' ? undefined : Number(rateText);
      const dividend = dividendText.trim() === '' ? undefined : Number(dividendText);
      if (rate !== undefined && !Number.isFinite(rate)) {
        setSnapshotError('금리는 숫자로 입력하세요.');
        return;
      }
      if (dividend !== undefined && (!Number.isFinite(dividend) || dividend < 0)) {
        setSnapshotError('예상 배당은 0 이상의 숫자로 입력하세요.');
        return;
      }
      setSnapshotLoading(true);
      setSnapshotError(null);
      try {
        const result = await koreanAnalyticsService.getBasisSnapshot(underlying.code, {
          rate,
          dividend: rate !== undefined ? dividend : undefined,
        });
        if (requestId === snapshotRequest.current) setSnapshot(result);
      } catch (err: unknown) {
        if (requestId === snapshotRequest.current) {
          setSnapshot(null);
          setSnapshotError(toUserMessage(err, '베이시스를 불러오지 못했습니다.'));
        }
      } finally {
        if (requestId === snapshotRequest.current) setSnapshotLoading(false);
      }
    },
    []
  );

  const loadHistory = useCallback(
    async (underlying: KoreanBasisUnderlying, symbol: string | null, days: number) => {
      const requestId = ++historyRequest.current;
      setHistoryLoading(true);
      setHistoryError(null);
      try {
        const result = await koreanAnalyticsService.getBasisHistory(underlying.code, {
          symbol: symbol ?? undefined,
          days,
        });
        if (requestId === historyRequest.current) setHistory(result);
      } catch (err: unknown) {
        if (requestId === historyRequest.current) {
          setHistory(null);
          setHistoryError(toUserMessage(err, '베이시스 추이를 불러오지 못했습니다.'));
        }
      } finally {
        if (requestId === historyRequest.current) setHistoryLoading(false);
      }
    },
    []
  );

  const selectUnderlying = (underlying: KoreanBasisUnderlying) => {
    setSelected(underlying);
    setSearch(underlying.name);
    setShowSuggestions(false);
    setSnapshot(null);
    setHistory(null);
    setHistorySymbol(null);
    loadSnapshot(underlying, rateInput, dividendInput);
    loadHistory(underlying, null, historyDays);
  };

  const selectContract = (contract: KoreanBasisContract) => {
    if (!selected) return;
    setHistorySymbol(contract.symbol);
    loadHistory(selected, contract.symbol, historyDays);
  };

  const changeRange = (days: number) => {
    setHistoryDays(days);
    if (selected) loadHistory(selected, historySymbol, days);
  };

  const digits = priceDigits(snapshot?.kind ?? selected?.kind);
  const front = snapshot?.contracts[0];
  const activeSymbol = historySymbol ?? history?.symbol ?? front?.symbol;
  const hasRate = rateInput.trim() !== '';

  const priceLines = useMemo(
    () =>
      (history?.points ?? []).map((point) => ({
        date: point.date,
        first: point.spot,
        second: point.futures,
      })),
    [history]
  );
  const basisBars = useMemo(
    () =>
      (history?.points ?? []).map((point) => ({
        date: point.date,
        value: point.basis_percent,
      })),
    [history]
  );

  return (
    <div className="hts-page">
      <SectionHeader
        title="선물·현물 베이시스"
        description="종목이나 지수를 고르면 상장된 선물 월물과 현물을 비교해 베이시스, 이론가 대비 괴리율, 선물 가격에 내재된 금리를 보여줍니다. 옵션이 상장된 기초자산은 콜·풋으로 만든 합성선물도 함께 비교합니다."
      />

      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'flex-end',
          gap: space.md,
          marginBottom: space.md,
        }}
      >
        <div style={{ position: 'relative', flex: '2 1 260px', minWidth: 0 }}>
          <Field label="기초자산 (종목명·종목코드·지수)">
            <TextInput
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setShowSuggestions(true);
              }}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => window.setTimeout(() => setShowSuggestions(false), 150)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && suggestions[0]) selectUnderlying(suggestions[0]);
              }}
              placeholder="예: 삼성전자, 005930, KOSPI200"
            />
          </Field>
          {showSuggestions && suggestions.length > 0 && (
            <ul
              style={{
                position: 'absolute',
                zIndex: zIndex.dropdown,
                top: `calc(100% + ${space.xs})`,
                left: 0,
                right: 0,
                margin: 0,
                padding: 0,
                listStyle: 'none',
                maxHeight: '320px',
                overflowY: 'auto',
                backgroundColor: color.surface,
                border: `1px solid ${color.border}`,
                borderRadius: radius.md,
                boxShadow: shadow.overlay,
              }}
            >
              {suggestions.map((item) => (
                <li
                  key={item.code}
                  style={{ borderBottom: `1px solid ${color.borderSoft}` }}
                >
                  <Button
                    variant="ghost"
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => selectUnderlying(item)}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'baseline',
                      gap: space.md,
                      width: '100%',
                      padding: `${space.sm} ${space.md}`,
                      borderRadius: 0,
                      textAlign: 'left',
                      whiteSpace: 'normal',
                      color: color.ink,
                    }}
                  >
                    <span style={{ fontWeight: fontWeight.semibold }}>{item.name}</span>
                    <span
                      style={{
                        ...dim,
                        flexShrink: 0,
                        fontSize: fontSize.sm,
                        fontWeight: fontWeight.regular,
                      }}
                    >
                      <span className="hts-mono">{item.code}</span> ·{' '}
                      {item.kind === 'index' ? '지수' : '주식'} · {item.contract_count}개 월물
                    </span>
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <Field label="조달금리 (연 %)" style={{ flex: '1 1 140px' }}>
          <TextInput
            value={rateInput}
            onChange={(e) => setRateInput(e.target.value)}
            inputMode="decimal"
            placeholder="비우면 증권사 이론가"
          />
        </Field>
        <Field label="만기 전 예상 배당" style={{ flex: '1 1 140px' }}>
          <TextInput
            value={dividendInput}
            onChange={(e) => setDividendInput(e.target.value)}
            inputMode="decimal"
            disabled={!hasRate}
            placeholder={hasRate ? '0' : '금리 입력 시 사용'}
          />
        </Field>
        <Button
          onClick={() => selected && loadSnapshot(selected, rateInput, dividendInput)}
          disabled={!selected || snapshotLoading}
          style={{ minWidth: '110px', paddingBlock: '9px' }}
        >
          {snapshotLoading ? '조회중' : '새로고침'}
        </Button>
      </div>

      {quickPicks.length > 0 && (
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: space.sm,
            marginBottom: space.xl,
          }}
        >
          {quickPicks.map((item) => (
            <Chip
              key={item.code}
              active={selected?.code === item.code}
              onClick={() => selectUnderlying(item)}
            >
              {item.name}
            </Chip>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: space.lg }}>
        {listError && <Notice>{listError}</Notice>}
        {snapshotError && <Notice>{snapshotError}</Notice>}

        {!selected && !snapshotError && (
          <EmptyState>
            기초자산을 검색해 선택하세요.
            {underlyings.length > 0 &&
              ` 선물이 상장된 주식 ${
                underlyings.filter((item) => item.kind === 'stock').length
              }종목과 지수 ${
                underlyings.filter((item) => item.kind === 'index').length
              }개를 조회할 수 있습니다.`}
          </EmptyState>
        )}

        {selected && !snapshot && snapshotLoading && (
          <Panel title={selected.name} note="시세를 불러오는 중입니다…">
            <SkeletonPanel rows={4} height={20} />
          </Panel>
        )}

        {snapshot && (
          <Panel
            title={snapshot.underlying_name}
            note={
              <>
                <span className="hts-mono">{snapshot.underlying_code}</span> ·{' '}
                {new Date(snapshot.as_of).toLocaleString('ko-KR')} 기준
              </>
            }
            actions={
              snapshot.rate_source === 'user' ? (
                <Badge tone="accent">이론가: 금리 {snapshot.rate}% 적용</Badge>
              ) : (
                <Badge>이론가: 증권사 제공값</Badge>
              )
            }
          >
            <Stack>
              <StatGrid minWidth={170}>
                <StatTile
                  label="현물"
                  value={formatNumber(snapshot.spot, digits)}
                  sub={
                    snapshot.spot_source === 'futures_synced'
                      ? '선물 시세와 같은 시점'
                      : '현물 현재가'
                  }
                />
                <StatTile
                  label={`최근월물 ${front?.expiry_month ?? ''}`}
                  value={formatNumber(front?.price, digits)}
                  sub={
                    isNumber(front?.days_to_expiry)
                      ? `잔존 ${front?.days_to_expiry}일`
                      : undefined
                  }
                />
                <StatTile
                  label="베이시스 (선물 − 현물)"
                  value={formatSigned(front?.basis, digits)}
                  sub={formatSignedPercent(front?.basis_percent)}
                />
                <StatTile
                  label="괴리율 (이론가 대비)"
                  value={formatSignedPercent(front?.discrepancy_percent)}
                  sub={valuationLabel(front?.discrepancy_percent) || undefined}
                />
                <StatTile
                  label="내재금리 (연)"
                  value={formatSignedPercent(front?.implied_rate)}
                  sub={
                    isNumber(front?.carry_rate)
                      ? `이론가 기준 ${front.carry_rate.toFixed(2)}%`
                      : undefined
                  }
                />
              </StatGrid>

              <Notes notes={snapshot.notes} />

              <div>
                <FigureTable>
                  <thead>
                    <tr>
                      <th>월물</th>
                      <th className="hts-num">잔존일</th>
                      <th className="hts-num">현재가</th>
                      <th className="hts-num">매수 / 매도</th>
                      <th className="hts-num">베이시스</th>
                      <th className="hts-num">베이시스 %</th>
                      <th className="hts-num">호가중간 베이시스</th>
                      <th className="hts-num">이론가</th>
                      <th className="hts-num">괴리율</th>
                      <th className="hts-num">내재금리</th>
                      <th className="hts-num">거래량</th>
                      <th className="hts-num">미결제</th>
                    </tr>
                  </thead>
                  <tbody>
                    {snapshot.contracts.map((contract) => {
                      const active = contract.symbol === activeSymbol;
                      return (
                        <tr
                          key={contract.symbol}
                          className="hts-row--clickable"
                          onClick={() => selectContract(contract)}
                          title="클릭하면 이 월물의 베이시스 추이를 봅니다"
                          aria-selected={active}
                          style={active ? { backgroundColor: color.accentSoft } : undefined}
                        >
                          <td
                            style={
                              active
                                ? { boxShadow: `inset 3px 0 0 ${color.accent}` }
                                : undefined
                            }
                          >
                            <strong>{contract.expiry_month}</strong>{' '}
                            <span className="hts-mono" style={dim}>
                              {contract.symbol}
                            </span>
                          </td>
                          <td className="hts-num">{formatNumber(contract.days_to_expiry)}</td>
                          <td className="hts-num">{formatNumber(contract.price, digits)}</td>
                          <td className="hts-num">
                            {formatNumber(contract.bid, digits)} /{' '}
                            {formatNumber(contract.ask, digits)}
                          </td>
                          <td className="hts-num">{formatSigned(contract.basis, digits)}</td>
                          <td className="hts-num">
                            {formatSignedPercent(contract.basis_percent)}
                          </td>
                          <td className="hts-num">{formatSigned(contract.mid_basis, digits)}</td>
                          <td className="hts-num">
                            {formatNumber(contract.theoretical_price, digits)}
                          </td>
                          <td className="hts-num">
                            {formatSignedPercent(contract.discrepancy_percent)}{' '}
                            <span style={dim}>
                              {valuationLabel(contract.discrepancy_percent)}
                            </span>
                          </td>
                          <td className="hts-num">
                            {formatSignedPercent(contract.implied_rate)}
                          </td>
                          <td className="hts-num">{formatNumber(contract.volume)}</td>
                          <td className="hts-num">{formatNumber(contract.open_interest)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </FigureTable>
                <Caption>
                  내재금리는 현물을 사서 만기까지 보유하는 대신 선물을 살 때 시장 가격에
                  반영된 연환산 비용입니다. 거래가 드문 원월물은 현재가가 오래된 체결가일
                  수 있어 호가중간 베이시스를 함께 보세요.
                </Caption>
              </div>
            </Stack>
          </Panel>
        )}

        {snapshot && (
          <OptionParityPanel
            key={snapshot.underlying_code}
            underlying={snapshot.underlying_code}
            kind={snapshot.kind}
            rate={snapshot.rate_source === 'user' ? snapshot.rate ?? undefined : undefined}
            refreshToken={snapshot.as_of}
          />
        )}

        {selected && (history || historyLoading || historyError) && (
          <Panel
            title="베이시스 추이"
            note={
              history?.contract_name ||
              (historyLoading && !history ? '추이를 불러오는 중입니다…' : undefined)
            }
            actions={
              <ChipGroup label="조회 기간">
                {HISTORY_RANGES.map((range) => (
                  <Chip
                    key={range.value}
                    active={historyDays === range.value}
                    onClick={() => changeRange(range.value)}
                  >
                    {range.label}
                  </Chip>
                ))}
              </ChipGroup>
            }
          >
            <Stack>
              {historyError && <Notice>{historyError}</Notice>}
              {historyLoading && !history && <SkeletonPanel rows={4} height={40} />}
              {history && history.points.length === 0 && (
                <EmptyState>조회 기간에 비교할 일별 데이터가 없습니다.</EmptyState>
              )}

              {history && history.points.length > 0 && (
                <>
                  {history.stats && (
                    <StatGrid minWidth={150}>
                      <StatTile
                        label="최근 베이시스"
                        value={formatSignedPercent(history.stats.latest)}
                      />
                      <StatTile
                        label={`평균 (${history.stats.count}일)`}
                        value={formatSignedPercent(history.stats.mean)}
                        sub={`표준편차 ${history.stats.std.toFixed(2)}%p`}
                      />
                      <StatTile
                        label="범위"
                        value={`${formatSignedPercent(history.stats.min)} ~ ${formatSignedPercent(
                          history.stats.max
                        )}`}
                      />
                      <StatTile
                        label="Z-점수"
                        value={
                          isNumber(history.stats.zscore)
                            ? `${history.stats.zscore > 0 ? '+' : ''}${history.stats.zscore.toFixed(2)}`
                            : '-'
                        }
                        sub={`기간 내 하위 ${history.stats.percentile.toFixed(0)}% 위치`}
                      />
                    </StatGrid>
                  )}

                  <div>
                    <SubHeading>현물과 선물 종가</SubHeading>
                    <TwoLineChart
                      data={priceLines}
                      firstName="현물"
                      secondName="선물"
                      format={(value) => formatNumber(value, digits)}
                    />
                  </div>
                  <div>
                    <SubHeading>베이시스 (현물 대비 %)</SubHeading>
                    <SignedBarChart
                      data={basisBars}
                      name="베이시스"
                      positiveLabel="선물이 현물보다 높음 (콘탱고)"
                      negativeLabel="선물이 현물보다 낮음 (백워데이션)"
                      positiveColor={chartTheme.series2}
                      negativeColor={chartTheme.series1}
                      format={(value) => `${value.toFixed(2)}%`}
                    />
                  </div>

                  <Disclosure summary={`표로 보기 (${history.points.length}일)`}>
                    <FigureTable maxHeight={320}>
                      <thead>
                        <tr>
                          <th>일자</th>
                          <th className="hts-num">현물</th>
                          <th className="hts-num">선물</th>
                          <th className="hts-num">베이시스</th>
                          <th className="hts-num">베이시스 %</th>
                          <th className="hts-num">내재금리</th>
                          <th className="hts-num">선물 거래량</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[...history.points].reverse().map((point) => (
                          <tr key={point.date}>
                            <td>{formatYyyymmdd(point.date)}</td>
                            <td className="hts-num">{formatNumber(point.spot, digits)}</td>
                            <td className="hts-num">{formatNumber(point.futures, digits)}</td>
                            <td className="hts-num">{formatSigned(point.basis, digits)}</td>
                            <td className="hts-num">
                              {formatSignedPercent(point.basis_percent)}
                            </td>
                            <td className="hts-num">
                              {formatSignedPercent(point.implied_rate)}
                            </td>
                            <td className="hts-num">{formatNumber(point.volume)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </FigureTable>
                  </Disclosure>
                  <Notes notes={history.notes} />
                </>
              )}
            </Stack>
          </Panel>
        )}
      </div>
    </div>
  );
};
