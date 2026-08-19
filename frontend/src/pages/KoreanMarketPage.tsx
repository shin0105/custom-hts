/**
 * Korean Market page component.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { StockCard } from '../components/StockCard';
import { CandleChart } from '../components/CandleChart';
import { SymbolSearch } from '../components/SymbolSearch';
import {
  SkeletonPanel,
  SkeletonTiles,
  StaleOverlay,
} from '../components/Skeleton';
import {
  getApiErrorMessage,
  useKoreanCandles,
  useKoreanEstimates,
  useKoreanFinancials,
  useKoreanQuote,
  useKoreanValuation,
  type ChartParams,
  type FinancialItem,
  type FinancialParams,
} from '../hooks/useKoreanMarket';
import { formatKoreanUnits, formatKoreanUnitsDetailed } from '../utils/format';
import type {
  ChartInterval,
  MinuteInterval,
  PeriodType,
} from '../types/korean';

const DEFAULT_SYMBOL = '005930'; // Samsung Electronics
const RECENT_KEY = 'kr-recent-symbols';
const RECENT_LIMIT = 6;

const POPULAR_STOCKS: Array<{ symbol: string; name: string }> = [
  { symbol: '005930', name: '삼성전자' },
  { symbol: '000660', name: 'SK하이닉스' },
  { symbol: '005380', name: '현대차' },
  { symbol: '035420', name: 'NAVER' },
  { symbol: '035720', name: '카카오' },
];

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

export const KoreanMarketPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // The symbol lives in the URL so a view can be bookmarked and shared, and
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

  const quoteQuery = useKoreanQuote(symbol, true);
  const hasQuote = Boolean(quoteQuery.data);

  // Dependent sections only run once the symbol resolves to a real quote.
  const valuationQuery = useKoreanValuation(symbol, financialParams, hasQuote);
  const financialsQuery = useKoreanFinancials(symbol, financialParams, hasQuote);
  const estimatesQuery = useKoreanEstimates(symbol, hasQuote);
  const candlesQuery = useKoreanCandles(symbol, chartParams, hasQuote);

  const quote = quoteQuery.data ?? null;
  const valuation = valuationQuery.data ?? null;
  const comprehensiveFinancials = financialsQuery.data ?? null;
  const estimatePerform = estimatesQuery.data ?? null;
  const candleData = candlesQuery.data ?? [];

  const selectSymbol = useCallback(
    (next: string, name?: string) => {
      const trimmed = next.trim();
      if (!trimmed) return;
      setSearchParams(
        (prev) => {
          const params = new URLSearchParams(prev);
          params.set('symbol', trimmed);
          return params;
        },
        { replace: false }
      );
      setRecents((prev) => {
        const merged = [
          { symbol: trimmed, name },
          ...prev.filter((entry) => entry.symbol !== trimmed),
        ].slice(0, RECENT_LIMIT);
        try {
          window.localStorage.setItem(RECENT_KEY, JSON.stringify(merged));
        } catch {
          // Storage can be unavailable (private mode); recents are optional.
        }
        return merged;
      });
    },
    [setSearchParams]
  );

  // Record the resolved company name once the quote arrives.
  useEffect(() => {
    if (!quote?.name) return;
    setRecents((prev) => {
      const existing = prev.find((entry) => entry.symbol === quote.symbol);
      if (!existing || existing.name === quote.name) return prev;
      const merged = prev.map((entry) =>
        entry.symbol === quote.symbol ? { ...entry, name: quote.name } : entry
      );
      try {
        window.localStorage.setItem(RECENT_KEY, JSON.stringify(merged));
      } catch {
        // Ignore storage failures.
      }
      return merged;
    });
  }, [quote?.symbol, quote?.name]);

  const containerStyle: React.CSSProperties = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: 'clamp(12px, 3vw, 24px)',
  };

  const controlsStyle: React.CSSProperties = {
    display: 'flex',
    gap: '12px',
    marginBottom: '16px',
    flexWrap: 'wrap',
    alignItems: 'center',
  };

  const selectStyle: React.CSSProperties = {
    padding: '8px 12px',
    fontSize: '14px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: 'white',
  };

  const statementBadgeStyle = (active: boolean): React.CSSProperties => ({
    padding: '6px 10px',
    fontSize: '12px',
    fontWeight: 600,
    borderRadius: '999px',
    border: active ? '1px solid #2563eb' : '1px solid #d1d5db',
    backgroundColor: active ? '#eff6ff' : 'white',
    color: active ? '#1d4ed8' : '#374151',
    cursor: 'pointer',
  });

  const chipStyle: React.CSSProperties = {
    padding: '6px 12px',
    fontSize: '13px',
    borderRadius: '999px',
    border: '1px solid #d1d5db',
    backgroundColor: 'white',
    color: '#334155',
    cursor: 'pointer',
  };

  const sectionHeadingStyle: React.CSSProperties = {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
  };

  const formatValue = (value: unknown) => {
    if (value === null || value === undefined || value === '') return '-';
    if (typeof value === 'number') {
      const absValue = Math.abs(value);
      if (!Number.isInteger(value) && absValue < 1000) {
        return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
      }
      return value.toLocaleString();
    }
    return String(value);
  };

  const formatPeriodLabel = (year?: number, quarter?: number) => {
    if (!year) return '-';
    return quarter ? `${year} Q${quarter}` : `${year} Annual`;
  };

  const estimateOutput1Labels: Record<string, string> = {
    elw_short_code: 'ELW Short Code',
    hts_korean_name: 'HTS Korean Name',
    elw_current_price: 'ELW Current Price',
    change_vs_prev_close: 'Change vs Prev Close',
    change_sign: 'Change Sign',
    change_rate: 'Change Rate',
    cumulative_volume: 'Cumulative Volume',
    strike_price: 'Strike Price',
  };

  const estimateMetricLabels: Record<string, string> = {
    revenue: 'Revenue',
    revenue_growth_rate: 'Revenue Growth Rate',
    operating_income: 'Operating Income',
    operating_income_growth_rate: 'Operating Income Growth Rate',
    net_income: 'Net Income',
    net_income_growth_rate: 'Net Income Growth Rate',
    ebitda: 'EBITDA',
    eps: 'EPS',
    eps_growth_rate: 'EPS Growth Rate',
    per: 'PER',
    ev_ebitda: 'EV/EBITDA',
    roe: 'ROE',
    debt_ratio: 'Debt Ratio',
    interest_coverage_ratio: 'Interest Coverage Ratio',
  };

  const estimateYearLabels = (estimatePerform?.output4 || []) as string[];

  const buildEstimateSummaryEntries = (row: Record<string, unknown>) => {
    const orderedKeys = Object.keys(estimateOutput1Labels).filter(
      (key) => key in row
    );
    const remainingKeys = Object.keys(row)
      .filter((key) => !orderedKeys.includes(key))
      .sort();
    const allKeys = [...orderedKeys, ...remainingKeys];
    return allKeys.map((key) => ({
      key,
      label: estimateOutput1Labels[key] ?? key,
      value: row[key],
    }));
  };

  const statementMap = {
    IS: { label: 'Income Statement', key: 'income_statement' as const },
    BS: { label: 'Balance Sheet', key: 'balance_sheet' as const },
    CF: { label: 'Cash Flow', key: 'cashflow_statement' as const },
  };

  const parseAmount = (value?: string) => {
    if (!value) return null;
    const cleaned = value.replace(/,/g, '').trim();
    if (cleaned === '' || cleaned === '-') return null;
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : null;
  };

  const matchesStatement = useCallback((item: FinancialItem) => {
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
  }, [finStatement]);

  const statementItems = useMemo(
    () => (comprehensiveFinancials?.data || []).filter(matchesStatement),
    [comprehensiveFinancials, matchesStatement]
  );

  const selectedStatementItems = useMemo(() => {
    const needle = accountFilter.trim().toLowerCase();
    if (!needle) return statementItems;
    return statementItems.filter((item) =>
      (item.account_nm || '').toLowerCase().includes(needle)
    );
  }, [statementItems, accountFilter]);

  const pickValue = (
    items: FinancialItem[],
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
        assets && { label: 'Assets', key: assets.key, value: assets.value },
        liabilities && {
          label: 'Liabilities',
          key: liabilities.key,
          value: liabilities.value,
        },
        equity && { label: 'Equity', key: equity.key, value: equity.value },
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
        revenue && { label: 'Revenue', key: revenue.key, value: revenue.value },
        opIncome && {
          label: 'Operating Income',
          key: opIncome.key,
          value: opIncome.value,
        },
        netIncome && {
          label: 'Net Income',
          key: netIncome.key,
          value: netIncome.value,
        },
      ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
    }
    const opCF = pickValue(statementItems, ['영업활동현금흐름']);
    const invCF = pickValue(statementItems, ['투자활동현금흐름']);
    const finCF = pickValue(statementItems, ['재무활동현금흐름']);
    return [
      opCF && { label: 'Operating CF', key: opCF.key, value: opCF.value },
      invCF && { label: 'Investing CF', key: invCF.key, value: invCF.value },
      finCF && { label: 'Financing CF', key: finCF.key, value: finCF.value },
    ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
  };

  const highlights = buildHighlights();
  const requestedQuarter = finPeriod === 'quarterly' ? finQuarter : undefined;
  const requestedPeriodLabel =
    finPeriod === 'quarterly' ? `${finYear} Q${finQuarter}` : `${finYear} Annual`;
  const usedPeriodLabel = valuation
    ? formatPeriodLabel(valuation.fiscal_year, valuation.fiscal_quarter)
    : '-';
  const ttmQuarterLabel = valuation?.ttm_quarters?.length
    ? valuation.ttm_quarters
        .map((item) => `${item.year} Q${item.quarter}`)
        .join(', ')
    : '-';
  const estimateLabelText = valuation?.estimate_12mf_labels?.length
    ? valuation.estimate_12mf_labels.join(' + ')
    : '-';
  const fallbackUsed =
    valuation?.fiscal_year !== undefined &&
    (valuation.fiscal_year !== finYear ||
      valuation.fiscal_quarter !== requestedQuarter);

  const valuationError = valuationQuery.error
    ? getApiErrorMessage(
        valuationQuery.error,
        'Failed to load valuation metrics.'
      )
    : null;
  const financialsError = financialsQuery.error
    ? getApiErrorMessage(
        financialsQuery.error,
        'Failed to load financial statements.'
      )
    : null;
  const estimateError = estimatesQuery.error
    ? getApiErrorMessage(
        estimatesQuery.error,
        'Failed to load estimate performance data.'
      )
    : null;
  const quoteError = quoteQuery.error
    ? getApiErrorMessage(
        quoteQuery.error,
        'Failed to load stock data. Please check the symbol and try again.'
      )
    : null;
  const candlesError = candlesQuery.error
    ? getApiErrorMessage(candlesQuery.error, 'Failed to load chart data.')
    : null;

  const valuationMetrics: Array<{
    label: string;
    value: string;
  }> = valuation
    ? [
        { label: 'PER', value: valuation.per?.toFixed(2) ?? 'N/A' },
        { label: 'PER (TTM)', value: valuation.per_ttm?.toFixed(2) ?? 'N/A' },
        { label: 'PER (12MF)', value: valuation.per_12mf?.toFixed(2) ?? 'N/A' },
        { label: 'PBR', value: valuation.pbr?.toFixed(2) ?? 'N/A' },
        { label: 'PBR (TTM)', value: valuation.pbr_ttm?.toFixed(2) ?? 'N/A' },
        {
          label: 'EPS',
          value:
            valuation.eps !== undefined && valuation.eps !== null
              ? `₩${valuation.eps.toFixed(2)}`
              : 'N/A',
        },
        {
          label: 'EPS (TTM)',
          value:
            valuation.eps_ttm !== undefined && valuation.eps_ttm !== null
              ? `₩${valuation.eps_ttm.toFixed(2)}`
              : 'N/A',
        },
        {
          label: 'EPS (12MF)',
          value:
            valuation.eps_12mf !== undefined && valuation.eps_12mf !== null
              ? `₩${valuation.eps_12mf.toFixed(2)}`
              : 'N/A',
        },
        {
          label: 'BPS',
          value:
            valuation.bps !== undefined && valuation.bps !== null
              ? `₩${valuation.bps.toFixed(2)}`
              : 'N/A',
        },
        {
          label: 'BPS (TTM)',
          value:
            valuation.bps_ttm !== undefined && valuation.bps_ttm !== null
              ? `₩${valuation.bps_ttm.toFixed(2)}`
              : 'N/A',
        },
      ]
    : [];

  const errorBanner = (message: string, onRetry?: () => void) => (
    <div
      role="alert"
      style={{
        padding: '12px',
        marginBottom: '12px',
        backgroundColor: '#fee2e2',
        color: '#991b1b',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
        flexWrap: 'wrap',
      }}
    >
      <span>{message}</span>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          style={{
            padding: '6px 12px',
            fontSize: '13px',
            fontWeight: 600,
            borderRadius: '6px',
            border: '1px solid #991b1b',
            backgroundColor: 'white',
            color: '#991b1b',
            cursor: 'pointer',
          }}
        >
          Retry
        </button>
      )}
    </div>
  );

  return (
    <div style={containerStyle}>
      <h1 style={{ fontSize: 'clamp(24px, 5vw, 32px)', fontWeight: 'bold', marginBottom: '24px' }}>
        🇰🇷 Korean Market
      </h1>

      <div
        style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '12px',
          flexWrap: 'wrap',
          alignItems: 'flex-start',
        }}
      >
        <SymbolSearch
          value={symbol}
          onSelect={(next, item) => selectSymbol(next, item?.name ?? undefined)}
        />
        <button
          type="button"
          onClick={() => {
            quoteQuery.refetch();
            valuationQuery.refetch();
            financialsQuery.refetch();
            estimatesQuery.refetch();
            candlesQuery.refetch();
          }}
          disabled={quoteQuery.isFetching}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          {quoteQuery.isFetching ? 'Loading…' : 'Refresh'}
        </button>
      </div>

      {/* Popular + recently viewed shortcuts */}
      <div style={{ ...controlsStyle, gap: '8px' }}>
        <span style={{ fontSize: '13px', color: '#6b7280', fontWeight: 500 }}>
          Popular:
        </span>
        {POPULAR_STOCKS.map((stock) => (
          <button
            key={stock.symbol}
            type="button"
            onClick={() => selectSymbol(stock.symbol, stock.name)}
            aria-current={stock.symbol === symbol ? 'true' : undefined}
            style={{
              ...chipStyle,
              borderColor: stock.symbol === symbol ? '#2563eb' : '#d1d5db',
              backgroundColor: stock.symbol === symbol ? '#eff6ff' : 'white',
            }}
          >
            {stock.name}{' '}
            <span style={{ color: '#94a3b8', fontFamily: 'monospace' }}>
              {stock.symbol}
            </span>
          </button>
        ))}
      </div>

      {recents.length > 0 && (
        <div style={{ ...controlsStyle, gap: '8px' }}>
          <span style={{ fontSize: '13px', color: '#6b7280', fontWeight: 500 }}>
            Recent:
          </span>
          {recents.map((entry) => (
            <button
              key={entry.symbol}
              type="button"
              onClick={() => selectSymbol(entry.symbol, entry.name)}
              style={{
                ...chipStyle,
                borderColor: entry.symbol === symbol ? '#2563eb' : '#e2e8f0',
                backgroundColor: entry.symbol === symbol ? '#eff6ff' : '#f8fafc',
              }}
            >
              {entry.name || entry.symbol}
            </button>
          ))}
        </div>
      )}

      {quoteError && errorBanner(quoteError, () => quoteQuery.refetch())}

      {quoteQuery.isLoading && <SkeletonPanel rows={4} label="Loading quote" />}

      {quote && (
        <div style={{ marginBottom: '24px' }}>
          <StaleOverlay stale={quoteQuery.isFetching}>
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
          </StaleOverlay>

          {valuationQuery.isLoading && (
            <div style={{ marginTop: '12px' }}>
              <SkeletonTiles count={6} label="Loading valuation metrics" />
            </div>
          )}

          {valuation && (
            <StaleOverlay stale={valuationQuery.isFetching}>
              <div
                style={{
                  marginTop: '12px',
                  padding: '16px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  backgroundColor: 'white',
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: '12px',
                }}
              >
                <div
                  style={{
                    gridColumn: '1 / -1',
                    marginBottom: '4px',
                    fontSize: '12px',
                    color: '#6b7280',
                  }}
                >
                  <strong>Requested:</strong> {requestedPeriodLabel} |{' '}
                  <strong>Used:</strong> {usedPeriodLabel}
                  {fallbackUsed ? ' (fallback)' : ''} |{' '}
                  <strong>TTM:</strong> {ttmQuarterLabel} |{' '}
                  <strong>12MF:</strong> {estimateLabelText}
                </div>
                {valuationMetrics.map((metric) => (
                  <div key={metric.label}>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>
                      {metric.label}
                    </div>
                    <div style={{ fontSize: '18px', fontWeight: 700 }}>
                      {metric.value}
                    </div>
                  </div>
                ))}
                {valuation.market_cap !== undefined &&
                  valuation.market_cap !== null && (
                    <div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        Market Cap
                      </div>
                      <div style={{ fontSize: '18px', fontWeight: 700 }}>
                        {formatKoreanUnits(valuation.market_cap)}
                      </div>
                    </div>
                  )}
              </div>
            </StaleOverlay>
          )}

          {(valuationError || Boolean(valuation?.notes?.length)) && (
            <div
              role={valuationError ? 'alert' : undefined}
              style={{
                marginTop: '12px',
                padding: '12px',
                backgroundColor: '#fff7ed',
                color: '#9a3412',
                borderRadius: '6px',
                border: '1px solid #fdba74',
                fontSize: '13px',
              }}
            >
              {valuationError && (
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    gap: '12px',
                    flexWrap: 'wrap',
                  }}
                >
                  <span>{valuationError}</span>
                  <button
                    type="button"
                    onClick={() => valuationQuery.refetch()}
                    style={{
                      padding: '4px 10px',
                      fontSize: '12px',
                      fontWeight: 600,
                      borderRadius: '6px',
                      border: '1px solid #9a3412',
                      backgroundColor: 'white',
                      color: '#9a3412',
                      cursor: 'pointer',
                    }}
                  >
                    Retry
                  </button>
                </div>
              )}
              {!valuationError &&
                valuation?.notes?.map((note, index) => (
                  <div key={`${note}-${index}`}>{note}</div>
                ))}
            </div>
          )}
        </div>
      )}

      {/* Chart Section */}
      {quote && (
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ ...sectionHeadingStyle, marginBottom: '16px' }}>
            Price Chart
          </h2>

          {/* Chart Controls */}
          <div style={controlsStyle}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Type:</span>
              <select
                value={chartInterval}
                onChange={(e) => setChartInterval(e.target.value as ChartInterval)}
                style={selectStyle}
              >
                <option value="daily">Daily</option>
                <option value="minute">Minute</option>
              </select>
            </label>

            {chartInterval === 'daily' ? (
              <>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>Period:</span>
                  <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value as PeriodType)}
                    style={selectStyle}
                  >
                    <option value="D">Daily</option>
                    <option value="W">Weekly</option>
                    <option value="M">Monthly</option>
                  </select>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>Start:</span>
                  <input
                    type="date"
                    value={
                      startDate
                        ? `${startDate.slice(0, 4)}-${startDate.slice(4, 6)}-${startDate.slice(6, 8)}`
                        : ''
                    }
                    onChange={(e) => setStartDate(e.target.value.replace(/-/g, ''))}
                    style={selectStyle}
                  />
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>End:</span>
                  <input
                    type="date"
                    value={
                      endDate
                        ? `${endDate.slice(0, 4)}-${endDate.slice(4, 6)}-${endDate.slice(6, 8)}`
                        : ''
                    }
                    onChange={(e) => setEndDate(e.target.value.replace(/-/g, ''))}
                    style={selectStyle}
                  />
                </label>
              </>
            ) : (
              <>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>Interval:</span>
                  <select
                    value={minuteInterval}
                    onChange={(e) =>
                      setMinuteInterval(Number(e.target.value) as MinuteInterval)
                    }
                    style={selectStyle}
                  >
                    <option value={1}>1 Minute</option>
                    <option value={5}>5 Minutes</option>
                    <option value={10}>10 Minutes</option>
                    <option value={30}>30 Minutes</option>
                    <option value={60}>60 Minutes</option>
                  </select>
                </label>

                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>Date:</span>
                  <input
                    type="date"
                    value={
                      selectedDate
                        ? `${selectedDate.slice(0, 4)}-${selectedDate.slice(4, 6)}-${selectedDate.slice(6, 8)}`
                        : ''
                    }
                    onChange={(e) => setSelectedDate(e.target.value.replace(/-/g, ''))}
                    style={selectStyle}
                  />
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>Time:</span>
                  <input
                    type="time"
                    value={minuteTime}
                    onChange={(e) => setMinuteTime(e.target.value)}
                    style={selectStyle}
                  />
                </label>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>
                  Time is the KST end of the requested window (defaults to the
                  15:30 close).
                </div>
              </>
            )}
          </div>

          {candlesError && errorBanner(candlesError, () => candlesQuery.refetch())}

          {/* Chart Display */}
          {candlesQuery.isLoading ? (
            <SkeletonPanel rows={8} label="Loading chart" />
          ) : (
            <StaleOverlay stale={candlesQuery.isFetching}>
              <CandleChart data={candleData} currency="KRW" height={500} />
            </StaleOverlay>
          )}
        </div>
      )}

      {/* Financial Statements Section */}
      {quote && (
        <div style={{ marginBottom: '24px' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <h2 style={sectionHeadingStyle}>Financial Statements (OpenDart)</h2>
            <div
              style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'center',
                flexWrap: 'wrap',
              }}
            >
              <select
                value={finYear}
                onChange={(e) => setFinYear(Number(e.target.value))}
                aria-label="Fiscal year"
                style={selectStyle}
              >
                {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map(
                  (year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  )
                )}
              </select>
              <select
                value={finPeriod}
                onChange={(e) =>
                  setFinPeriod(e.target.value as 'annual' | 'quarterly')
                }
                aria-label="Reporting period"
                style={selectStyle}
              >
                <option value="annual">Annual</option>
                <option value="quarterly">Quarterly</option>
              </select>
              <select
                value={finQuarter}
                onChange={(e) => setFinQuarter(Number(e.target.value))}
                aria-label="Quarter"
                style={selectStyle}
                disabled={finPeriod === 'annual'}
              >
                <option value={1}>Q1</option>
                <option value={2}>Q2</option>
                <option value={3}>Q3</option>
                <option value={4}>Q4</option>
              </select>
              <select
                value={fsDivision}
                onChange={(e) => setFsDivision(e.target.value as 'CFS' | 'OFS')}
                aria-label="Consolidated or separate statements"
                style={selectStyle}
              >
                <option value="CFS">Consolidated</option>
                <option value="OFS">Separate</option>
              </select>
              <div
                role="group"
                aria-label="Statement type"
                style={{ display: 'flex', gap: '6px', alignItems: 'center' }}
              >
                {(['IS', 'BS', 'CF'] as const).map((code) => (
                  <button
                    key={code}
                    type="button"
                    onClick={() => setFinStatement(code)}
                    aria-pressed={finStatement === code}
                    aria-label={statementMap[code].label}
                    style={statementBadgeStyle(finStatement === code)}
                  >
                    {code}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {financialsError &&
            errorBanner(financialsError, () => financialsQuery.refetch())}

          {financialsQuery.isLoading ? (
            <SkeletonPanel rows={8} label="Loading financial statements" />
          ) : comprehensiveFinancials && comprehensiveFinancials.count > 0 ? (
            <StaleOverlay stale={financialsQuery.isFetching}>
              <div
                style={{
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  backgroundColor: 'white',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    padding: '16px',
                    backgroundColor: '#f9fafb',
                    borderBottom: '1px solid #e5e7eb',
                  }}
                >
                  <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
                    <strong>Symbol:</strong> {comprehensiveFinancials.symbol} |
                    <strong> Year:</strong> {comprehensiveFinancials.year} |
                    <strong> Period:</strong>{' '}
                    {comprehensiveFinancials.quarter
                      ? `Q${comprehensiveFinancials.quarter}`
                      : 'Annual'}{' '}
                    |<strong> Statement:</strong> {statementMap[finStatement].label} |
                    <strong> Items:</strong> {selectedStatementItems.length}
                    {accountFilter.trim() !== '' &&
                      ` / ${statementItems.length}`}
                  </p>
                  <p style={{ margin: '6px 0 0', fontSize: '12px', color: '#9ca3af' }}>
                    Amounts are reported in KRW; 조 = trillion, 억 = 100 million.
                  </p>
                  {comprehensiveFinancials.note && (
                    <p style={{ margin: '6px 0 0', fontSize: '12px', color: '#9ca3af' }}>
                      {comprehensiveFinancials.note}
                    </p>
                  )}
                </div>

                {highlights.length > 0 && (
                  <div
                    style={{
                      display: 'grid',
                      gap: '12px',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                      padding: '16px',
                      borderBottom: '1px solid #e5e7eb',
                    }}
                  >
                    {highlights.map((item) => (
                      <div
                        key={item.key}
                        style={{
                          backgroundColor: '#f8fafc',
                          borderRadius: '8px',
                          padding: '12px',
                          border: '1px solid #e2e8f0',
                        }}
                      >
                        <div
                          style={{
                            fontSize: '12px',
                            fontWeight: 600,
                            color: '#475569',
                          }}
                        >
                          {item.label}
                        </div>
                        <div
                          style={{
                            fontSize: '18px',
                            fontWeight: 700,
                            color: '#0f172a',
                            marginTop: '4px',
                          }}
                          title={item.value.toLocaleString('ko-KR')}
                        >
                          {formatKoreanUnits(item.value)}
                        </div>
                        <div
                          style={{
                            fontSize: '11px',
                            color: '#94a3b8',
                            marginTop: '2px',
                          }}
                        >
                          {item.key}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid #e5e7eb',
                  }}
                >
                  <input
                    type="search"
                    value={accountFilter}
                    onChange={(e) => setAccountFilter(e.target.value)}
                    placeholder="계정과목 검색 / Filter accounts (e.g. 매출)"
                    aria-label="Filter financial statement accounts"
                    style={{
                      width: '100%',
                      maxWidth: '360px',
                      padding: '8px 12px',
                      fontSize: '14px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                    }}
                  />
                </div>

                {selectedStatementItems.length > 0 ? (
                  <div style={{ maxHeight: '600px', overflow: 'auto' }}>
                    <table
                      style={{
                        width: '100%',
                        borderCollapse: 'collapse',
                        fontSize: '14px',
                      }}
                    >
                      <thead
                        style={{
                          position: 'sticky',
                          top: 0,
                          backgroundColor: '#f9fafb',
                          zIndex: 1,
                        }}
                      >
                        <tr>
                          <th
                            scope="col"
                            style={{
                              padding: '12px',
                              textAlign: 'left',
                              borderBottom: '2px solid #e5e7eb',
                              fontWeight: '600',
                            }}
                          >
                            Account
                          </th>
                          <th
                            scope="col"
                            style={{
                              padding: '12px',
                              textAlign: 'right',
                              borderBottom: '2px solid #e5e7eb',
                              fontWeight: '600',
                            }}
                          >
                            Value
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedStatementItems.map((item, index) => {
                          const bgColor = index % 2 === 0 ? '#f8fafc' : 'white';
                          const amount = parseAmount(item.thstrm_amount);
                          return (
                            <tr key={index} style={{ backgroundColor: bgColor }}>
                              <td
                                style={{
                                  padding: '8px 12px',
                                  borderBottom: '1px solid #f3f4f6',
                                }}
                              >
                                {item.account_nm || '-'}
                              </td>
                              <td
                                style={{
                                  padding: '8px 12px',
                                  borderBottom: '1px solid #f3f4f6',
                                  textAlign: 'right',
                                  fontFamily: 'monospace',
                                  whiteSpace: 'nowrap',
                                }}
                                title={
                                  amount !== null
                                    ? amount.toLocaleString('ko-KR')
                                    : undefined
                                }
                              >
                                {amount !== null
                                  ? formatKoreanUnitsDetailed(amount)
                                  : formatValue(item.thstrm_amount ?? '-')}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div
                    style={{
                      padding: '24px',
                      textAlign: 'center',
                      color: '#6b7280',
                    }}
                  >
                    {accountFilter.trim() !== ''
                      ? `No accounts match "${accountFilter}".`
                      : 'No items for this statement in the selected period.'}
                  </div>
                )}
              </div>
            </StaleOverlay>
          ) : (
            <div
              style={{
                padding: '24px',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                backgroundColor: '#f9fafb',
                textAlign: 'center',
              }}
            >
              <p style={{ color: '#6b7280', margin: 0 }}>
                {comprehensiveFinancials?.note ||
                  'No financial data available for the selected period. Try a different year or quarter.'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Estimated Performance Section */}
      {quote && (
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ ...sectionHeadingStyle, marginBottom: '16px' }}>
            Estimated Performance (KDevelopers)
          </h2>

          {estimateError &&
            errorBanner(estimateError, () => estimatesQuery.refetch())}

          {estimatesQuery.isLoading ? (
            <SkeletonPanel rows={6} label="Loading estimates" />
          ) : estimatePerform ? (
            <StaleOverlay stale={estimatesQuery.isFetching}>
              <div
                style={{
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  backgroundColor: 'white',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    padding: '16px',
                    backgroundColor: '#f9fafb',
                    borderBottom: '1px solid #e5e7eb',
                  }}
                >
                  <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
                    <strong>Symbol:</strong> {estimatePerform.symbol}
                  </p>
                  {estimatePerform.unit_notes && (
                    <p style={{ margin: '6px 0 0', fontSize: '12px', color: '#9ca3af' }}>
                      {estimatePerform.unit_notes}
                    </p>
                  )}
                </div>

                {estimatePerform.output1.length > 0 && (
                  <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>
                    <div
                      style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}
                    >
                      Summary
                    </div>
                    <div
                      style={{
                        display: 'grid',
                        gap: '12px',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                      }}
                    >
                      {buildEstimateSummaryEntries(estimatePerform.output1[0]).map(
                        (entry) => (
                          <div
                            key={entry.key}
                            style={{
                              backgroundColor: '#f8fafc',
                              borderRadius: '8px',
                              padding: '12px',
                              border: '1px solid #e2e8f0',
                            }}
                          >
                            <div
                              style={{
                                fontSize: '12px',
                                fontWeight: 600,
                                color: '#475569',
                              }}
                            >
                              {entry.label}
                            </div>
                            <div
                              style={{
                                fontSize: '14px',
                                fontWeight: 700,
                                color: '#0f172a',
                                marginTop: '4px',
                              }}
                            >
                              {formatValue(entry.value)}
                            </div>
                            <div
                              style={{
                                fontSize: '11px',
                                color: '#94a3b8',
                                marginTop: '2px',
                              }}
                            >
                              {entry.key}
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {([
                  { rows: estimatePerform.output2, title: 'Income Statement Estimates' },
                  { rows: estimatePerform.output3, title: 'Investment Indicators' },
                ] as const).map(
                  (table) =>
                    table.rows.length > 0 &&
                    estimateYearLabels.length > 0 && (
                      <div key={table.title} style={{ borderTop: '1px solid #e5e7eb' }}>
                        <div
                          style={{
                            padding: '12px 16px',
                            fontSize: '14px',
                            fontWeight: 600,
                            backgroundColor: '#f9fafb',
                          }}
                        >
                          {table.title}
                        </div>
                        <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                          <table
                            style={{
                              width: '100%',
                              borderCollapse: 'collapse',
                              fontSize: '13px',
                            }}
                          >
                            <thead
                              style={{
                                position: 'sticky',
                                top: 0,
                                backgroundColor: '#f9fafb',
                                zIndex: 1,
                              }}
                            >
                              <tr>
                                <th
                                  scope="col"
                                  style={{
                                    padding: '10px 12px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e5e7eb',
                                    fontWeight: 600,
                                  }}
                                >
                                  Metric
                                </th>
                                {estimateYearLabels.map((label, index) => (
                                  <th
                                    key={`${label}-${index}`}
                                    scope="col"
                                    style={{
                                      padding: '10px 12px',
                                      textAlign: 'left',
                                      borderBottom: '2px solid #e5e7eb',
                                      fontWeight: 600,
                                    }}
                                  >
                                    {label}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {table.rows.map((row, rowIndex) => {
                                const bgColor = rowIndex % 2 === 0 ? '#f8fafc' : 'white';
                                const label =
                                  estimateMetricLabels[row.metric] ??
                                  row.metric ??
                                  `Metric ${rowIndex + 1}`;
                                const values = Array.isArray(row.values)
                                  ? row.values
                                  : estimateYearLabels.map(
                                      (year) => row.year_values?.[year]
                                    );
                                return (
                                  <tr key={label} style={{ backgroundColor: bgColor }}>
                                    <td
                                      style={{
                                        padding: '8px 12px',
                                        borderBottom: '1px solid #f3f4f6',
                                      }}
                                    >
                                      {label}
                                    </td>
                                    {values.map((value, index) => (
                                      <td
                                        key={`${label}-${index}`}
                                        style={{
                                          padding: '8px 12px',
                                          borderBottom: '1px solid #f3f4f6',
                                          fontFamily: 'monospace',
                                        }}
                                      >
                                        {formatValue(value)}
                                      </td>
                                    ))}
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )
                )}

                {(!estimatePerform.output2.length || !estimateYearLabels.length) &&
                  (!estimatePerform.output3.length || !estimateYearLabels.length) && (
                    <div
                      style={{ padding: '24px', textAlign: 'center', color: '#6b7280' }}
                    >
                      No estimate performance table data available.
                    </div>
                  )}
              </div>
            </StaleOverlay>
          ) : (
            <div
              style={{
                padding: '24px',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                backgroundColor: '#f9fafb',
                textAlign: 'center',
              }}
            >
              <p style={{ color: '#6b7280', margin: 0 }}>
                No estimate performance data available for this symbol.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
