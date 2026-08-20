/**
 * Korean Market page component.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { StockCard } from '../components/StockCard';
import { CandleChart } from '../components/CandleChart';
import { koreanMarketService } from '../services/koreanMarket';
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
import type {
  KoreanStockQuote,
  KoreanCandleData,
  ChartInterval,
  MinuteInterval,
  PeriodType,
  KoreanValuationMetrics,
  KoreanEstimatePerform,
  KoreanAllFinancialsResponse,
  KoreanFinancialItem,
} from '../types/korean';

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
  const [symbol, setSymbol] = useState('005930'); // Samsung Electronics
  const [quote, setQuote] = useState<KoreanStockQuote | null>(null);
  const [valuation, setValuation] = useState<KoreanValuationMetrics | null>(null);
  const [valuationError, setValuationError] = useState<string | null>(null);
  const [valuationLoading, setValuationLoading] = useState(false);
  const [comprehensiveFinancials, setComprehensiveFinancials] =
    useState<KoreanAllFinancialsResponse | null>(null);
  const [financialsError, setFinancialsError] = useState<string | null>(null);
  const [financialsLoading, setFinancialsLoading] = useState(false);
  const [estimatePerform, setEstimatePerform] =
    useState<KoreanEstimatePerform | null>(null);
  const [estimateError, setEstimateError] = useState<string | null>(null);
  const [estimateLoading, setEstimateLoading] = useState(false);
  const [candleData, setCandleData] = useState<KoreanCandleData[]>([]);
  const [candleError, setCandleError] = useState<string | null>(null);
  const [candleLoading, setCandleLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const loadValuation = useCallback(async () => {
    setValuationLoading(true);
    try {
      const valuationData = await koreanMarketService.getValuation(
        symbol,
        finYear,
        finPeriod === 'quarterly' ? finQuarter : undefined,
        fsDivision
      );
      setValuation(valuationData);
      setValuationError(null);
    } catch (valError) {
      console.error('Failed to load valuation metrics:', valError);
      setValuation(null);
      setValuationError(
        toUserMessage(valError, ko.stock.valuationFailed)
      );
    } finally {
      setValuationLoading(false);
    }
  }, [symbol, finYear, finPeriod, finQuarter, fsDivision]);

  const loadFinancials = useCallback(async () => {
    setFinancialsLoading(true);
    try {
      const finData = await koreanMarketService.getAllFinancials(
        symbol,
        finYear,
        finPeriod === 'quarterly' ? finQuarter : undefined,
        fsDivision
      );
      setComprehensiveFinancials(finData);
      setFinancialsError(null);
    } catch (finError) {
      console.error('Failed to load financials:', finError);
      setComprehensiveFinancials(null);
      setFinancialsError(
        toUserMessage(finError, ko.financials.loadFailed)
      );
    } finally {
      setFinancialsLoading(false);
    }
  }, [symbol, finYear, finPeriod, finQuarter, fsDivision]);

  const loadCandleData = useCallback(async () => {
    setCandleLoading(true);
    try {
      if (chartInterval === 'daily') {
        const candles = await koreanMarketService.getDailyCandle(
          symbol,
          period,
          true,
          undefined,
          startDate || undefined,
          endDate || undefined
        );
        setCandleData(candles);
      } else {
        // For minute candles, require a date; default to today in KST.
        let dateStr = selectedDate;
        if (!dateStr) {
          const today = new Date();
          const kstDate = new Date(today.getTime() + 9 * 60 * 60 * 1000); // UTC+9
          dateStr = kstDate.toISOString().split('T')[0].replace(/-/g, '');
          setSelectedDate(dateStr);
        }
        const candles = await koreanMarketService.getMinuteCandle(
          symbol,
          minuteInterval,
          undefined,
          dateStr,
          minuteTime ? `${minuteTime.replace(':', '')}00` : undefined
        );
        setCandleData(candles);
      }
      setCandleError(null);
    } catch (err) {
      console.error('Failed to load candle data:', err);
      setCandleData([]);
      setCandleError(toUserMessage(err, ko.chart.noData));
    } finally {
      setCandleLoading(false);
    }
  }, [
    symbol,
    chartInterval,
    period,
    minuteInterval,
    selectedDate,
    minuteTime,
    startDate,
    endDate,
  ]);

  const loadEstimatePerform = useCallback(async () => {
    setEstimateLoading(true);
    try {
      const estimate = await koreanMarketService.getEstimatePerform(symbol);
      setEstimatePerform(estimate);
      setEstimateError(null);
    } catch (err) {
      console.error('Failed to load estimate performance:', err);
      setEstimatePerform(null);
      setEstimateError(toUserMessage(err, ko.estimate.loadFailed));
    } finally {
      setEstimateLoading(false);
    }
  }, [symbol]);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      // The quote gates the rest of the page, so it is awaited first and
      // rendered as soon as it lands.
      const quoteData = await koreanMarketService.getQuote(symbol);
      setQuote(quoteData);
    } catch (err) {
      console.error('Failed to load quote:', err);
      setError(toUserMessage(err, ko.stock.loadFailed));
      setQuote(null);
      setValuation(null);
      setComprehensiveFinancials(null);
      setEstimatePerform(null);
      setCandleData([]);
      setLoading(false);
      return;
    }
    setLoading(false);

    // Each panel then loads independently: one failure leaves the others intact.
    void Promise.allSettled([
      loadValuation(),
      loadCandleData(),
      loadFinancials(),
      loadEstimatePerform(),
    ]);
  };

  // Reload candles when chart settings change
  useEffect(() => {
    if (symbol && quote) {
      void loadCandleData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    chartInterval,
    period,
    minuteInterval,
    selectedDate,
    minuteTime,
    startDate,
    endDate,
  ]);

  useEffect(() => {
    if (symbol && quote) {
      void loadFinancials();
      void loadValuation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finYear, finQuarter, finPeriod, fsDivision, symbol, quote]);

  useEffect(() => {
    if (symbol && quote) {
      void loadEstimatePerform();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol, quote]);

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

  const selectedStatementItems = (comprehensiveFinancials?.data || []).filter(
    matchesStatement
  );

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
    if (!selectedStatementItems.length) return [];
    if (finStatement === 'BS') {
      const assets = pickValue(selectedStatementItems, ['자산총계']);
      const liabilities = pickValue(selectedStatementItems, ['부채총계']);
      const equity = pickValue(selectedStatementItems, ['자본총계']);
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
      const revenue = pickValue(selectedStatementItems, ['매출액']);
      const opIncome = pickValue(selectedStatementItems, ['영업이익']);
      const netIncome = pickValue(selectedStatementItems, [
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
    const opCF = pickValue(selectedStatementItems, ['영업활동현금흐름']);
    const invCF = pickValue(selectedStatementItems, ['투자활동현금흐름']);
    const finCF = pickValue(selectedStatementItems, ['재무활동현금흐름']);
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
        <TextInput
          type="text"
          placeholder={ko.stock.searchPlaceholder}
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          aria-label={ko.stock.searchPlaceholder}
        />
        <Button onClick={handleSearch} disabled={loading}>
          {loading ? ko.common.searching : ko.common.search}
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
            onClick={() => setSymbol(item.code)}
          >
            {item.name}{' '}
            <span className="hts-mono" style={{ color: color.inkDim }}>
              {item.code}
            </span>
          </Chip>
        ))}
      </div>

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
              <Notice onRetry={loadValuation}>{valuationError}</Notice>
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
                <Notice onRetry={loadCandleData}>{candleError}</Notice>
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
                <Notice onRetry={loadFinancials}>{financialsError}</Notice>
              </div>
            ) : financialsLoading && !comprehensiveFinancials ? (
              <div style={{ padding: space.lg }}>
                <SkeletonPanel rows={6} />
              </div>
            ) : comprehensiveFinancials && selectedStatementItems.length > 0 ? (
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
                <Notice onRetry={loadEstimatePerform}>{estimateError}</Notice>
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
