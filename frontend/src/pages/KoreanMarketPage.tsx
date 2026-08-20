/**
 * Korean Market page component.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { StockCard } from '../components/StockCard';
import { CandleChart } from '../components/CandleChart';
import { SymbolSearch } from '../components/SymbolSearch';
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
  Select,
  SkeletonPanel,
  StatGrid,
  StatTile,
  Table,
  TableScroll,
  TextInput,
} from '../components/ui';
import { color, fontSize, space } from '../theme/tokens';
import { ko } from '../i18n/ko';
import { formatKrwCompact, formatNumber } from '../utils/format';
import { toUserMessage } from '../utils/apiError';
import {
  useKoreanCandles,
  useKoreanEstimates,
  useKoreanFinancials,
  useKoreanQuote,
  useKoreanValuation,
  type ChartParams,
  type FinancialParams,
} from '../hooks/useKoreanMarket';
import type {
  ChartInterval,
  MinuteInterval,
  PeriodType,
  KoreanFinancialItem,
} from '../types/korean';

const DEFAULT_SYMBOL = '005930'; // Samsung Electronics
const RECENT_KEY = 'kr-recent-symbols';
const RECENT_LIMIT = 6;

type RecentEntry = { symbol: string; name?: string };

const readRecents = (): RecentEntry[] => {
  try {
    const raw = window.localStorage.getItem(RECENT_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.slice(0, RECENT_LIMIT) : [];
  } catch {
    return [];
  }
};

const writeRecents = (entries: RecentEntry[]) => {
  try {
    window.localStorage.setItem(RECENT_KEY, JSON.stringify(entries));
  } catch {
    // Storage can be unavailable (private mode); recents are a convenience.
  }
};

const POPULAR_STOCKS: Array<{ code: string; name: string }> = [
  { code: '005930', name: '삼성전자' },
  { code: '000660', name: 'SK하이닉스' },
  { code: '005380', name: '현대차' },
  { code: '035420', name: 'NAVER' },
  { code: '035720', name: '카카오' },
];

const STATEMENTS: Array<{ value: 'IS' | 'BS' | 'CF'; label: string }> = [
  { value: 'IS', label: ko.financials.incomeStatement },
  { value: 'BS', label: ko.financials.balanceSheet },
  { value: 'CF', label: ko.financials.cashFlow },
];

export const KoreanMarketPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // The symbol lives in the URL so a view is bookmarkable, shareable, and
  // survives a reload instead of snapping back to Samsung.
  const symbol = searchParams.get('symbol')?.trim() || DEFAULT_SYMBOL;

  const [recents, setRecents] = useState<RecentEntry[]>(() => readRecents());

  // Chart controls
  const [chartInterval, setChartInterval] = useState<ChartInterval>('daily');
  const [period, setPeriod] = useState<PeriodType>('D');
  const [minuteInterval, setMinuteInterval] = useState<MinuteInterval>(1);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [minuteTime, setMinuteTime] = useState<string>('15:30');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Financial statement controls
  const [finYear, setFinYear] = useState<number>(new Date().getFullYear() - 1);
  const [finPeriod, setFinPeriod] = useState<'annual' | 'quarterly'>('annual');
  const [finQuarter, setFinQuarter] = useState<number>(1);
  const [finStatement, setFinStatement] = useState<'IS' | 'BS' | 'CF'>('IS');
  const [fsDivision, setFsDivision] = useState<'CFS' | 'OFS'>('CFS');
  const [accountFilter, setAccountFilter] = useState('');

  const financialParams: FinancialParams = useMemo(
    () => ({
      year: finYear,
      quarter: finPeriod === 'quarterly' ? finQuarter : undefined,
      fsDivision,
    }),
    [finYear, finPeriod, finQuarter, fsDivision]
  );

  const chartParams: ChartParams = useMemo(
    () => ({
      interval: chartInterval,
      period,
      minuteInterval,
      date: selectedDate,
      time: minuteTime,
      startDate,
      endDate,
    }),
    [
      chartInterval,
      period,
      minuteInterval,
      selectedDate,
      minuteTime,
      startDate,
      endDate,
    ]
  );

  // The quote gates the page; the other panels wait for it to resolve, then
  // each load independently and cache under their own key.
  const quoteQuery = useKoreanQuote(symbol, true);
  const hasQuote = Boolean(quoteQuery.data);
  const valuationQuery = useKoreanValuation(symbol, financialParams, hasQuote);
  const financialsQuery = useKoreanFinancials(symbol, financialParams, hasQuote);
  const estimatesQuery = useKoreanEstimates(symbol, hasQuote);
  const candlesQuery = useKoreanCandles(symbol, chartParams, hasQuote);

  const quote = quoteQuery.data ?? null;
  const valuation = valuationQuery.data ?? null;
  const comprehensiveFinancials = financialsQuery.data ?? null;
  const estimatePerform = estimatesQuery.data ?? null;
  const candleData = candlesQuery.data ?? [];

  const loading = quoteQuery.isFetching;
  const valuationLoading = valuationQuery.isLoading;
  const financialsLoading = financialsQuery.isLoading;
  const estimateLoading = estimatesQuery.isLoading;
  const candleLoading = candlesQuery.isLoading;

  const error = quoteQuery.error
    ? toUserMessage(quoteQuery.error, ko.stock.loadFailed)
    : null;
  const valuationError = valuationQuery.error
    ? toUserMessage(valuationQuery.error, ko.stock.valuationFailed)
    : null;
  const financialsError = financialsQuery.error
    ? toUserMessage(financialsQuery.error, ko.financials.loadFailed)
    : null;
  const estimateError = estimatesQuery.error
    ? toUserMessage(estimatesQuery.error, ko.estimate.loadFailed)
    : null;
  const candleError = candlesQuery.error
    ? toUserMessage(candlesQuery.error, ko.chart.noData)
    : null;

  const selectSymbol = useCallback(
    (next: string, name?: string) => {
      const trimmed = next.trim();
      if (!trimmed) return;
      setSearchParams((prev) => {
        const params = new URLSearchParams(prev);
        params.set('symbol', trimmed);
        return params;
      });
      setRecents((prev) => {
        const merged = [
          { symbol: trimmed, name },
          ...prev.filter((entry) => entry.symbol !== trimmed),
        ].slice(0, RECENT_LIMIT);
        writeRecents(merged);
        return merged;
      });
    },
    [setSearchParams]
  );

  // Backfill the company name on the recents entry once the quote lands.
  useEffect(() => {
    if (!quote?.name) return;
    setRecents((prev) => {
      const existing = prev.find((entry) => entry.symbol === quote.symbol);
      if (!existing || existing.name === quote.name) return prev;
      const merged = prev.map((entry) =>
        entry.symbol === quote.symbol ? { ...entry, name: quote.name } : entry
      );
      writeRecents(merged);
      return merged;
    });
  }, [quote?.symbol, quote?.name]);

  const handleSearch = useCallback(() => {
    void quoteQuery.refetch();
    void valuationQuery.refetch();
    void financialsQuery.refetch();
    void estimatesQuery.refetch();
    void candlesQuery.refetch();
  }, [
    quoteQuery,
    valuationQuery,
    financialsQuery,
    estimatesQuery,
    candlesQuery,
  ]);

  const formatValue = (value: unknown) => {
    if (value === null || value === undefined || value === '') return '-';
    if (typeof value === 'number') {
      const absValue = Math.abs(value);
      if (!Number.isInteger(value) && absValue < 1000) {
        return value.toLocaleString('ko-KR', { maximumFractionDigits: 2 });
      }
      return value.toLocaleString('ko-KR');
    }
    return String(value);
  };

  const formatPeriodLabel = (year?: number, quarter?: number) => {
    if (!year) return '-';
    return quarter
      ? `${year}년 ${quarter}분기`
      : `${year}년 ${ko.valuation.annual}`;
  };

  const estimateYearLabels = (estimatePerform?.output4 || []) as string[];

  const buildEstimateSummaryEntries = (row: Record<string, unknown>) => {
    const labels: Record<string, string> = ko.estimateSummary;
    const orderedKeys = Object.keys(labels).filter((key) => key in row);
    const remainingKeys = Object.keys(row)
      .filter((key) => !orderedKeys.includes(key))
      .sort();
    return [...orderedKeys, ...remainingKeys].map((key) => ({
      key,
      label: labels[key] ?? key,
      value: row[key],
    }));
  };

  const parseAmount = (value?: string) => {
    if (!value) return null;
    const cleaned = value.replace(/,/g, '').trim();
    if (cleaned === '' || cleaned === '-') return null;
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : null;
  };

  const matchesStatement = (item: KoreanFinancialItem) => {
    const sjDiv = (item.sj_div || '').toUpperCase();
    if (sjDiv) {
      if (finStatement === 'IS') return sjDiv === 'IS' || sjDiv === 'CIS';
      if (finStatement === 'BS') return sjDiv === 'BS';
      if (finStatement === 'CF') return sjDiv === 'CF';
    }
    const sjName = item.sj_nm || '';
    if (finStatement === 'BS') return sjName.includes('재무상태표');
    if (finStatement === 'IS')
      return sjName.includes('손익계산서') || sjName.includes('포괄손익');
    if (finStatement === 'CF') return sjName.includes('현금흐름');
    return false;
  };

  const statementItems = (comprehensiveFinancials?.data || []).filter(
    matchesStatement
  );

  // Highlights summarise the whole statement, so they read the unfiltered set;
  // only the table below narrows to the account search.
  const selectedStatementItems = accountFilter.trim()
    ? statementItems.filter((item) =>
        (item.account_nm || '')
          .toLowerCase()
          .includes(accountFilter.trim().toLowerCase())
      )
    : statementItems;

  const pickValue = (
    items: KoreanFinancialItem[],
    keys: string[]
  ): { key: string; value: number } | null => {
    for (const key of keys) {
      const match = items.find((item) => item.account_nm === key);
      if (match) {
        const parsed = parseAmount(match.thstrm_amount);
        if (parsed !== null) {
          return { key, value: parsed };
        }
      }
    }
    return null;
  };

  const buildHighlights = () => {
    if (!statementItems.length) return [];
    if (finStatement === 'BS') {
      const assets = pickValue(statementItems, ['자산총계']);
      const liabilities = pickValue(statementItems, ['부채총계']);
      const equity = pickValue(statementItems, ['자본총계']);
      return [
        assets && { label: ko.financials.assets, key: assets.key, value: assets.value },
        liabilities && {
          label: ko.financials.liabilities,
          key: liabilities.key,
          value: liabilities.value,
        },
        equity && { label: ko.financials.equity, key: equity.key, value: equity.value },
      ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
    }
    if (finStatement === 'IS') {
      const revenue = pickValue(statementItems, ['매출액']);
      const opIncome = pickValue(statementItems, ['영업이익']);
      const netIncome = pickValue(statementItems, [
        '당기순이익',
        '분기순이익(손실)',
      ]);
      return [
        revenue && { label: ko.financials.revenue, key: revenue.key, value: revenue.value },
        opIncome && {
          label: ko.financials.operatingIncome,
          key: opIncome.key,
          value: opIncome.value,
        },
        netIncome && {
          label: ko.financials.netIncome,
          key: netIncome.key,
          value: netIncome.value,
        },
      ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
    }
    const opCF = pickValue(statementItems, ['영업활동현금흐름']);
    const invCF = pickValue(statementItems, ['투자활동현금흐름']);
    const finCF = pickValue(statementItems, ['재무활동현금흐름']);
    return [
      opCF && {
        label: ko.financials.operatingCashFlow,
        key: opCF.key,
        value: opCF.value,
      },
      invCF && {
        label: ko.financials.investingCashFlow,
        key: invCF.key,
        value: invCF.value,
      },
      finCF && {
        label: ko.financials.financingCashFlow,
        key: finCF.key,
        value: finCF.value,
      },
    ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
  };

  const highlights = buildHighlights();
  const requestedQuarter = finPeriod === 'quarterly' ? finQuarter : undefined;
  const requestedPeriodLabel = formatPeriodLabel(finYear, requestedQuarter);
  const usedPeriodLabel = valuation
    ? formatPeriodLabel(valuation.fiscal_year, valuation.fiscal_quarter)
    : '-';
  const ttmQuarterLabel = valuation?.ttm_quarters?.length
    ? valuation.ttm_quarters
        .map((item) => `${item.year}년 ${item.quarter}분기`)
        .join(', ')
    : '-';
  const estimateLabelText = valuation?.estimate_12mf_labels?.length
    ? valuation.estimate_12mf_labels.join(' + ')
    : '-';
  const fallbackUsed =
    valuation?.fiscal_year !== undefined &&
    (valuation.fiscal_year !== finYear ||
      valuation.fiscal_quarter !== requestedQuarter);

  /** Valuation metrics grouped by the basis they are computed on. */
  const valuationGroups = valuation
    ? [
        {
          title: ko.valuation.actual,
          note: usedPeriodLabel,
          metrics: [
            { label: 'PER', value: valuation.per, unit: '배' },
            { label: 'PBR', value: valuation.pbr, unit: '배' },
            { label: 'EPS', value: valuation.eps, unit: '원' },
            { label: 'BPS', value: valuation.bps, unit: '원' },
          ],
        },
        {
          title: ko.valuation.ttm,
          note: ttmQuarterLabel,
          metrics: [
            { label: 'PER', value: valuation.per_ttm, unit: '배' },
            { label: 'PBR', value: valuation.pbr_ttm, unit: '배' },
            { label: 'EPS', value: valuation.eps_ttm, unit: '원' },
            { label: 'BPS', value: valuation.bps_ttm, unit: '원' },
          ],
        },
        {
          title: ko.valuation.forward12m,
          note: estimateLabelText,
          metrics: [
            { label: 'PER', value: valuation.per_12mf, unit: '배' },
            { label: 'EPS', value: valuation.eps_12mf, unit: '원' },
          ],
        },
      ]
    : [];

  const formatMetric = (value: number | undefined | null, unit: string) => {
    if (value === undefined || value === null || !Number.isFinite(value)) {
      return 'N/A';
    }
    if (unit === '원') return `${formatNumber(value, 0)}원`;
    return `${value.toFixed(2)}${unit}`;
  };

  const yearOptions = Array.from(
    { length: 5 },
    (_, i) => new Date().getFullYear() - i
  );

  return (
    <div className="hts-page">
      <SectionHeader
        title={`🇰🇷 ${ko.stock.title}`}
        description="종목코드로 시세, 투자지표, 재무제표, 추정실적을 조회합니다."
      />

      <div style={{ display: 'flex', gap: space.md, marginBottom: space.lg }}>
        <SymbolSearch
          value={symbol}
          onSelect={(next, item) => selectSymbol(next, item?.name ?? undefined)}
        />
        <Button onClick={handleSearch} disabled={loading}>
          {loading ? ko.common.searching : ko.common.refresh}
        </Button>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: space.sm,
          flexWrap: 'wrap',
          marginBottom: space.xl,
        }}
      >
        <span style={{ fontSize: fontSize.md, color: color.inkDim }}>
          {ko.stock.popular}
        </span>
        {POPULAR_STOCKS.map((item) => (
          <Chip
            key={item.code}
            active={symbol === item.code}
            onClick={() => selectSymbol(item.code, item.name)}
          >
            {item.name}{' '}
            <span className="hts-mono" style={{ color: color.inkDim }}>
              {item.code}
            </span>
          </Chip>
        ))}
      </div>

      {recents.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: space.sm,
            flexWrap: 'wrap',
            marginBottom: space.xl,
          }}
        >
          <span style={{ fontSize: fontSize.md, color: color.inkDim }}>
            {ko.stock.recent}
          </span>
          {recents.map((entry) => (
            <Chip
              key={entry.symbol}
              active={symbol === entry.symbol}
              onClick={() => selectSymbol(entry.symbol, entry.name)}
            >
              {entry.name || entry.symbol}
            </Chip>
          ))}
        </div>
      )}

      {error && (
        <div style={{ marginBottom: space.xl }}>
          <Notice onRetry={handleSearch}>{error}</Notice>
        </div>
      )}

      {quote && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: space.xl,
          }}
        >
          <StockCard
            symbol={quote.symbol}
            name={quote.name}
            currentPrice={quote.current_price}
            change={quote.change}
            changePercent={quote.change_percent}
            currency="KRW"
            open={quote.open}
            high={quote.high}
            low={quote.low}
            previousClose={quote.previous_close}
            volume={quote.volume}
            marketCap={valuation?.market_cap}
            sharesOutstanding={valuation?.shares_outstanding}
            timestamp={quote.timestamp}
          />

          {/* Valuation */}
          <Panel
            title={ko.valuation.title}
            note={`${ko.valuation.requested} ${requestedPeriodLabel}`}
            actions={
              fallbackUsed ? (
                <Badge tone="warning" title="요청한 기간의 데이터가 없어 다른 기간을 사용했습니다.">
                  {ko.valuation.fallback} · {usedPeriodLabel}
                </Badge>
              ) : valuation ? (
                <Badge>{usedPeriodLabel}</Badge>
              ) : null
            }
          >
            {valuationLoading && !valuation ? (
              <SkeletonPanel rows={3} height={28} />
            ) : valuationError ? (
              <Notice onRetry={() => void valuationQuery.refetch()}>{valuationError}</Notice>
            ) : valuation ? (
              <div
                style={{
                  display: 'grid',
                  gap: space.lg,
                  gridTemplateColumns:
                    'repeat(auto-fit, minmax(260px, 1fr))',
                }}
              >
                {valuationGroups.map((group) => (
                  <div key={group.title}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'baseline',
                        gap: space.sm,
                        marginBottom: space.sm,
                      }}
                    >
                      <span
                        style={{
                          fontSize: fontSize.md,
                          fontWeight: 600,
                          color: color.ink,
                        }}
                      >
                        {group.title}
                      </span>
                      <span
                        style={{ fontSize: fontSize.sm, color: color.inkDim }}
                      >
                        {group.note}
                      </span>
                    </div>
                    <StatGrid minWidth={110}>
                      {group.metrics.map((metric) => (
                        <StatTile
                          key={`${group.title}-${metric.label}`}
                          label={metric.label}
                          value={formatMetric(metric.value, metric.unit)}
                        />
                      ))}
                    </StatGrid>
                  </div>
                ))}
                {valuation.market_cap !== undefined &&
                  valuation.market_cap !== null && (
                    <div>
                      <div
                        style={{
                          fontSize: fontSize.md,
                          fontWeight: 600,
                          marginBottom: space.sm,
                        }}
                      >
                        {ko.valuation.marketCap}
                      </div>
                      <StatGrid minWidth={110}>
                        <StatTile
                          label={ko.valuation.marketCap}
                          value={formatKrwCompact(valuation.market_cap)}
                          sub={`${formatNumber(valuation.market_cap)}원`}
                        />
                        {valuation.shares_outstanding ? (
                          <StatTile
                            label={ko.valuation.sharesOutstanding}
                            value={formatNumber(valuation.shares_outstanding)}
                            sub="주"
                          />
                        ) : null}
                      </StatGrid>
                    </div>
                  )}
              </div>
            ) : (
              <EmptyState>{ko.common.noData}</EmptyState>
            )}
            {!valuationError && valuation?.notes?.length ? (
              <div style={{ marginTop: space.md }}>
                <Notice tone="warning">
                  {valuation.notes.map((note, index) => (
                    <div key={`${note}-${index}`}>{note}</div>
                  ))}
                </Notice>
              </div>
            ) : null}
          </Panel>

          {/* Chart */}
          <Panel
            title={ko.chart.title}
            note={
              chartInterval === 'minute' ? ko.chart.minuteTimeHint : undefined
            }
            actions={
              <>
                <Field label={ko.chart.type} inline>
                  <Select
                    value={chartInterval}
                    onChange={(e) =>
                      setChartInterval(e.target.value as ChartInterval)
                    }
                  >
                    <option value="daily">{ko.chart.daily}</option>
                    <option value="minute">{ko.chart.minute}</option>
                  </Select>
                </Field>

                {chartInterval === 'daily' ? (
                  <>
                    <Field label={ko.chart.period} inline>
                      <Select
                        value={period}
                        onChange={(e) => setPeriod(e.target.value as PeriodType)}
                      >
                        <option value="D">일</option>
                        <option value="W">주</option>
                        <option value="M">월</option>
                      </Select>
                    </Field>
                    <Field label={ko.chart.startDate} inline>
                      <TextInput
                        type="date"
                        value={
                          startDate
                            ? `${startDate.slice(0, 4)}-${startDate.slice(4, 6)}-${startDate.slice(6, 8)}`
                            : ''
                        }
                        onChange={(e) =>
                          setStartDate(e.target.value.replace(/-/g, ''))
                        }
                      />
                    </Field>
                    <Field label={ko.chart.endDate} inline>
                      <TextInput
                        type="date"
                        value={
                          endDate
                            ? `${endDate.slice(0, 4)}-${endDate.slice(4, 6)}-${endDate.slice(6, 8)}`
                            : ''
                        }
                        onChange={(e) =>
                          setEndDate(e.target.value.replace(/-/g, ''))
                        }
                      />
                    </Field>
                  </>
                ) : (
                  <>
                    <Field label={ko.chart.interval} inline>
                      <Select
                        value={minuteInterval}
                        onChange={(e) =>
                          setMinuteInterval(
                            Number(e.target.value) as MinuteInterval
                          )
                        }
                      >
                        <option value={1}>1분</option>
                        <option value={5}>5분</option>
                        <option value={10}>10분</option>
                        <option value={30}>30분</option>
                        <option value={60}>60분</option>
                      </Select>
                    </Field>
                    <Field label={ko.chart.date} inline>
                      <TextInput
                        type="date"
                        value={
                          selectedDate
                            ? `${selectedDate.slice(0, 4)}-${selectedDate.slice(4, 6)}-${selectedDate.slice(6, 8)}`
                            : ''
                        }
                        onChange={(e) =>
                          setSelectedDate(e.target.value.replace(/-/g, ''))
                        }
                      />
                    </Field>
                    <Field label={ko.chart.time} inline>
                      <TextInput
                        type="time"
                        value={minuteTime}
                        onChange={(e) => setMinuteTime(e.target.value)}
                      />
                    </Field>
                  </>
                )}
              </>
            }
          >
            {candleError && (
              <div style={{ marginBottom: space.md }}>
                <Notice onRetry={() => void candlesQuery.refetch()}>{candleError}</Notice>
              </div>
            )}
            {candleLoading && candleData.length === 0 ? (
              <SkeletonPanel rows={4} height={60} />
            ) : (
              <CandleChart data={candleData} currency="KRW" height={500} />
            )}
          </Panel>

          {/* Financial statements */}
          <Panel
            title={ko.financials.title}
            note={
              comprehensiveFinancials
                ? `${comprehensiveFinancials.symbol} · ${comprehensiveFinancials.year}년 ${
                    comprehensiveFinancials.quarter
                      ? `${comprehensiveFinancials.quarter}분기`
                      : ko.valuation.annual
                  } · ${ko.financials.items} ${selectedStatementItems.length}`
                : undefined
            }
            actions={
              <>
                <Select
                  value={finYear}
                  onChange={(e) => setFinYear(Number(e.target.value))}
                  aria-label="연도"
                >
                  {yearOptions.map((year) => (
                    <option key={year} value={year}>
                      {year}년
                    </option>
                  ))}
                </Select>
                <Select
                  value={finPeriod}
                  onChange={(e) =>
                    setFinPeriod(e.target.value as 'annual' | 'quarterly')
                  }
                  aria-label={ko.financials.period}
                >
                  <option value="annual">{ko.valuation.annual}</option>
                  <option value="quarterly">{ko.valuation.quarter}</option>
                </Select>
                <Select
                  value={finQuarter}
                  onChange={(e) => setFinQuarter(Number(e.target.value))}
                  disabled={finPeriod === 'annual'}
                  aria-label="분기"
                >
                  <option value={1}>1분기</option>
                  <option value={2}>2분기</option>
                  <option value={3}>3분기</option>
                  <option value={4}>4분기</option>
                </Select>
                <Select
                  value={fsDivision}
                  onChange={(e) =>
                    setFsDivision(e.target.value as 'CFS' | 'OFS')
                  }
                  aria-label="연결/별도"
                >
                  <option value="CFS">{ko.financials.consolidated}</option>
                  <option value="OFS">{ko.financials.separate}</option>
                </Select>
                <ChipGroup label="재무제표 종류">
                  {STATEMENTS.map((statement) => (
                    <Chip
                      key={statement.value}
                      active={finStatement === statement.value}
                      onClick={() => setFinStatement(statement.value)}
                    >
                      {statement.label}
                    </Chip>
                  ))}
                </ChipGroup>
              </>
            }
            flush
          >
            {financialsError ? (
              <div style={{ padding: space.lg }}>
                <Notice onRetry={() => void financialsQuery.refetch()}>{financialsError}</Notice>
              </div>
            ) : financialsLoading && !comprehensiveFinancials ? (
              <div style={{ padding: space.lg }}>
                <SkeletonPanel rows={6} />
              </div>
            ) : comprehensiveFinancials && statementItems.length > 0 ? (
              <>
                {highlights.length > 0 && (
                  <div
                    style={{
                      padding: space.lg,
                      borderBottom: `1px solid ${color.border}`,
                    }}
                  >
                    <StatGrid minWidth={180}>
                      {highlights.map((item) => (
                        <StatTile
                          key={item.key}
                          label={item.label}
                          value={formatValue(item.value)}
                          sub={ko.common.unitKrw}
                        />
                      ))}
                    </StatGrid>
                  </div>
                )}
                <div
                  style={{
                    padding: `${space.md} ${space.lg}`,
                    borderBottom: `1px solid ${color.border}`,
                  }}
                >
                  <TextInput
                    type="search"
                    value={accountFilter}
                    onChange={(e) => setAccountFilter(e.target.value)}
                    placeholder={ko.financials.filterPlaceholder}
                    aria-label={ko.financials.filterPlaceholder}
                    style={{ maxWidth: '360px' }}
                  />
                </div>
                {selectedStatementItems.length > 0 ? (
                  <TableScroll maxHeight={600} bordered={false}>
                    <Table>
                      <thead>
                        <tr>
                          <th>{ko.financials.account}</th>
                          <th className="hts-num">{ko.financials.amount}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedStatementItems.map((item, index) => (
                          <tr key={index}>
                            <td>{item.account_nm || '-'}</td>
                            <td className="hts-num">
                              {formatValue(
                                parseAmount(item.thstrm_amount) ??
                                  item.thstrm_amount ??
                                  '-'
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </TableScroll>
                ) : (
                  <div style={{ padding: space.lg }}>
                    <EmptyState>{ko.financials.filterNoMatch}</EmptyState>
                  </div>
                )}
              </>
            ) : (
              <div style={{ padding: space.lg }}>
                <EmptyState>
                  {comprehensiveFinancials?.note || ko.financials.empty}
                </EmptyState>
              </div>
            )}
          </Panel>

          {/* Estimated performance */}
          <Panel
            title={ko.estimate.title}
            note={estimatePerform?.unit_notes}
            flush
          >
            {estimateError ? (
              <div style={{ padding: space.lg }}>
                <Notice onRetry={() => void estimatesQuery.refetch()}>{estimateError}</Notice>
              </div>
            ) : estimateLoading && !estimatePerform ? (
              <div style={{ padding: space.lg }}>
                <SkeletonPanel rows={5} />
              </div>
            ) : estimatePerform ? (
              <>
                {estimatePerform.output1.length > 0 && (
                  <div
                    style={{
                      padding: space.lg,
                      borderBottom: `1px solid ${color.border}`,
                    }}
                  >
                    <div
                      style={{
                        fontSize: fontSize.md,
                        fontWeight: 600,
                        marginBottom: space.sm,
                      }}
                    >
                      {ko.estimate.summary}
                    </div>
                    <StatGrid minWidth={170}>
                      {buildEstimateSummaryEntries(
                        estimatePerform.output1[0]
                      ).map((entry) => (
                        <StatTile
                          key={entry.key}
                          label={entry.label}
                          value={formatValue(entry.value)}
                        />
                      ))}
                    </StatGrid>
                  </div>
                )}

                {[
                  { rows: estimatePerform.output2, title: ko.estimate.incomeEstimates },
                  {
                    rows: estimatePerform.output3,
                    title: ko.estimate.investmentIndicators,
                  },
                ].map(({ rows, title }) =>
                  rows.length > 0 && estimateYearLabels.length > 0 ? (
                    <div
                      key={title}
                      style={{ borderTop: `1px solid ${color.border}` }}
                    >
                      <div
                        style={{
                          padding: `${space.md} ${space.lg}`,
                          fontSize: fontSize.md,
                          fontWeight: 600,
                          backgroundColor: color.surfaceMuted,
                        }}
                      >
                        {title}
                      </div>
                      <TableScroll maxHeight={400} bordered={false}>
                        <Table>
                          <thead>
                            <tr>
                              <th>항목</th>
                              {estimateYearLabels.map((label, index) => (
                                <th
                                  key={`${label}-${index}`}
                                  className="hts-num"
                                >
                                  {label}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {rows.map((row, rowIndex) => {
                              const metricLabels: Record<string, string> =
                                ko.metric;
                              const label =
                                metricLabels[row.metric] ??
                                row.metric ??
                                `항목 ${rowIndex + 1}`;
                              const values = Array.isArray(row.values)
                                ? row.values
                                : estimateYearLabels.map(
                                    (year) => row.year_values?.[year]
                                  );
                              return (
                                <tr key={label}>
                                  <td>{label}</td>
                                  {values.map((value, index) => (
                                    <td
                                      key={`${label}-${index}`}
                                      className="hts-num"
                                    >
                                      {formatValue(value)}
                                    </td>
                                  ))}
                                </tr>
                              );
                            })}
                          </tbody>
                        </Table>
                      </TableScroll>
                    </div>
                  ) : null
                )}
              </>
            ) : (
              <div style={{ padding: space.lg }}>
                <EmptyState>{ko.estimate.empty}</EmptyState>
              </div>
            )}
          </Panel>
        </div>
      )}

      {!quote && !error && !loading && (
        <EmptyState>
          종목코드를 입력하거나 위의 종목을 선택한 뒤 조회 버튼을 누르세요.
        </EmptyState>
      )}
    </div>
  );
};
