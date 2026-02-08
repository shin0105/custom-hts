/**
 * Korean Market page component.
 */

import React, { useState, useEffect } from 'react';
import { StockCard } from '../components/StockCard';
import { CandleChart } from '../components/CandleChart';
import { koreanMarketService } from '../services/koreanMarket';
import type {
  KoreanStockQuote,
  KoreanCandleData,
  ChartInterval,
  MinuteInterval,
  PeriodType,
  KoreanValuationMetrics,
} from '../types/korean';

type FinancialItem = {
  sj_nm?: string;
  sj_div?: string;
  account_nm?: string;
  thstrm_amount?: string;
};

type FinancialsResponse = {
  symbol: string;
  year: number;
  requested_year?: number;
  quarter?: number;
  fs_div: 'CFS' | 'OFS';
  count: number;
  data: FinancialItem[];
  note?: string;
};

export const KoreanMarketPage: React.FC = () => {
  const [symbol, setSymbol] = useState('005930'); // Samsung Electronics
  const [quote, setQuote] = useState<KoreanStockQuote | null>(null);
  const [valuation, setValuation] = useState<KoreanValuationMetrics | null>(null);
  const [comprehensiveFinancials, setComprehensiveFinancials] =
    useState<FinancialsResponse | null>(null);
  const [candleData, setCandleData] = useState<KoreanCandleData[]>([]);
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

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get quote
      const quoteData = await koreanMarketService.getQuote(symbol);
      setQuote(quoteData);

      // Get valuation metrics
      try {
        const valuationData = await koreanMarketService.getValuation(
          symbol,
          finYear,
          finPeriod === 'quarterly' ? finQuarter : undefined,
          fsDivision
        );
        setValuation(valuationData);
      } catch (valError) {
        console.error('Failed to load valuation metrics:', valError);
        setValuation(null);
      }

      // Get candles
      await loadCandleData();

      // Get financials
      await loadFinancials();
    } catch (err) {
      setError('Failed to load stock data. Please check the symbol and try again.');
      setQuote(null);
      setValuation(null);
      setComprehensiveFinancials(null);
      setCandleData([]);
    } finally {
      setLoading(false);
    }
  };

  const loadFinancials = async () => {
    try {
      const finData = await koreanMarketService.getAllFinancials(
        symbol,
        finYear,
        finPeriod === 'quarterly' ? finQuarter : undefined,
        fsDivision
      );
      setComprehensiveFinancials(finData);
    } catch (finError) {
      console.error('Failed to load financials:', finError);
      setComprehensiveFinancials(null);
    }
  };

  const loadCandleData = async () => {
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
        // For minute candles, require a date
        if (!selectedDate) {
          // Default to today in KST
          const today = new Date();
          const kstDate = new Date(today.getTime() + 9 * 60 * 60 * 1000); // UTC+9
          const dateStr = kstDate.toISOString().split('T')[0].replace(/-/g, '');
          setSelectedDate(dateStr);
          
          const candles = await koreanMarketService.getMinuteCandle(
            symbol,
            minuteInterval,
            undefined,
            dateStr,
            minuteTime ? `${minuteTime.replace(':', '')}00` : undefined
          );
          setCandleData(candles);
        } else {
          const candles = await koreanMarketService.getMinuteCandle(
            symbol,
            minuteInterval,
            undefined,
            selectedDate,
            minuteTime ? `${minuteTime.replace(':', '')}00` : undefined
          );
          setCandleData(candles);
        }
      }
    } catch (err) {
      console.error('Failed to load candle data:', err);
      setCandleData([]);
    }
  };

  // Reload candles when chart settings change
  useEffect(() => {
    if (symbol && quote) {
      loadCandleData();
    }
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
      loadFinancials();
    }
  }, [finYear, finQuarter, finPeriod, fsDivision, symbol, quote]);

  useEffect(() => {
    if (symbol && quote) {
      const loadValuation = async () => {
        try {
          const valuationData = await koreanMarketService.getValuation(
            symbol,
            finYear,
            finPeriod === 'quarterly' ? finQuarter : undefined,
            fsDivision
          );
          setValuation(valuationData);
        } catch (valError) {
          console.error('Failed to load valuation metrics:', valError);
          setValuation(null);
        }
      };
      loadValuation();
    }
  }, [finYear, finQuarter, finPeriod, fsDivision, symbol, quote]);

  const containerStyle: React.CSSProperties = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '24px',
  };

  const searchBoxStyle: React.CSSProperties = {
    display: 'flex',
    gap: '12px',
    marginBottom: '24px',
  };

  const inputStyle: React.CSSProperties = {
    flex: 1,
    padding: '12px',
    fontSize: '16px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
  };

  const buttonStyle: React.CSSProperties = {
    padding: '12px 24px',
    fontSize: '16px',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
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

  const matchesStatement = (item: FinancialItem) => {
    const sjDiv = (item.sj_div || '').toUpperCase();
    if (sjDiv) return sjDiv === finStatement;
    const sjName = item.sj_nm || '';
    if (finStatement === 'BS') return sjName.includes('재무상태표');
    if (finStatement === 'IS') return sjName.includes('손익계산서');
    if (finStatement === 'CF') return sjName.includes('현금흐름');
    return false;
  };

  const selectedStatementItems = (comprehensiveFinancials?.data || []).filter(
    matchesStatement
  );

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
    if (!selectedStatementItems.length) return [];
    if (finStatement === 'BS') {
      const assets = pickValue(selectedStatementItems, ['자산총계']);
      const liabilities = pickValue(selectedStatementItems, ['부채총계']);
      const equity = pickValue(selectedStatementItems, ['자본총계']);
      return [
        assets && { label: 'Assets', key: assets.key, value: assets.value },
        liabilities && { label: 'Liabilities', key: liabilities.key, value: liabilities.value },
        equity && { label: 'Equity', key: equity.key, value: equity.value },
      ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
    }
    if (finStatement === 'IS') {
      const revenue = pickValue(selectedStatementItems, ['매출액']);
      const opIncome = pickValue(selectedStatementItems, ['영업이익']);
      const netIncome = pickValue(selectedStatementItems, ['당기순이익', '분기순이익(손실)']);
      return [
        revenue && { label: 'Revenue', key: revenue.key, value: revenue.value },
        opIncome && { label: 'Operating Income', key: opIncome.key, value: opIncome.value },
        netIncome && { label: 'Net Income', key: netIncome.key, value: netIncome.value },
      ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
    }
    const opCF = pickValue(selectedStatementItems, ['영업활동현금흐름']);
    const invCF = pickValue(selectedStatementItems, ['투자활동현금흐름']);
    const finCF = pickValue(selectedStatementItems, ['재무활동현금흐름']);
    return [
      opCF && { label: 'Operating CF', key: opCF.key, value: opCF.value },
      invCF && { label: 'Investing CF', key: invCF.key, value: invCF.value },
      finCF && { label: 'Financing CF', key: finCF.key, value: finCF.value },
    ].filter(Boolean) as Array<{ label: string; key: string; value: number }>;
  };

  const highlights = buildHighlights();

  return (
    <div style={containerStyle}>
      <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>
        🇰🇷 Korean Market
      </h1>

      <div style={searchBoxStyle}>
        <input
          type="text"
          placeholder="Enter stock code (e.g., 005930 for Samsung)"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          style={inputStyle}
        />
        <button onClick={handleSearch} disabled={loading} style={buttonStyle}>
          {loading ? 'Loading...' : 'Search'}
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: '12px',
            backgroundColor: '#fee2e2',
            color: '#991b1b',
            borderRadius: '6px',
            marginBottom: '24px',
          }}
        >
          {error}
        </div>
      )}

      {quote && (
        <div style={{ marginBottom: '24px' }}>
          <StockCard
            symbol={quote.symbol}
            name={quote.name}
            currentPrice={quote.current_price}
            change={quote.change}
            changePercent={quote.change_percent}
            currency="KRW"
          />
          {valuation && (
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
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>PER</div>
                <div style={{ fontSize: '18px', fontWeight: 700 }}>
                  {valuation.per !== undefined && valuation.per !== null
                    ? valuation.per.toFixed(2)
                    : 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>PBR</div>
                <div style={{ fontSize: '18px', fontWeight: 700 }}>
                  {valuation.pbr !== undefined && valuation.pbr !== null
                    ? valuation.pbr.toFixed(2)
                    : 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>EPS</div>
                <div style={{ fontSize: '18px', fontWeight: 700 }}>
                  {valuation.eps !== undefined && valuation.eps !== null
                    ? `₩${valuation.eps.toFixed(2)}`
                    : 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>BPS</div>
                <div style={{ fontSize: '18px', fontWeight: 700 }}>
                  {valuation.bps !== undefined && valuation.bps !== null
                    ? `₩${valuation.bps.toFixed(2)}`
                    : 'N/A'}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chart Section */}
      {quote && (
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>
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
                    onChange={(e) => {
                      const dateStr = e.target.value.replace(/-/g, '');
                      setStartDate(dateStr);
                    }}
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
                    onChange={(e) => {
                      const dateStr = e.target.value.replace(/-/g, '');
                      setEndDate(dateStr);
                    }}
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
                    onChange={(e) => setMinuteInterval(Number(e.target.value) as MinuteInterval)}
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
                    onChange={(e) => {
                      const dateStr = e.target.value.replace(/-/g, '');
                      setSelectedDate(dateStr);
                    }}
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
              </>
            )}

            <div style={{ fontSize: '12px', color: '#6b7280' }}>
              Minute time defaults to 15:30 KST.
            </div>
          </div>

          {/* Chart Display */}
          <CandleChart data={candleData} currency="KRW" height={500} />
        </div>
      )}

      {/* Financial Statements Section */}
      {quote && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
              Financial Statements (OpenDart)
            </h2>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              <select
                value={finYear}
                onChange={(e) => setFinYear(Number(e.target.value))}
                style={selectStyle}
              >
                {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
              <select
                value={finPeriod}
                onChange={(e) => setFinPeriod(e.target.value as 'annual' | 'quarterly')}
                style={selectStyle}
              >
                <option value="annual">Annual</option>
                <option value="quarterly">Quarterly</option>
              </select>
              <select
                value={finQuarter}
                onChange={(e) => setFinQuarter(Number(e.target.value))}
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
                style={selectStyle}
              >
                <option value="CFS">Consolidated</option>
                <option value="OFS">Separate</option>
              </select>
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                <button
                  onClick={() => setFinStatement('IS')}
                  style={statementBadgeStyle(finStatement === 'IS')}
                >
                  IS
                </button>
                <button
                  onClick={() => setFinStatement('BS')}
                  style={statementBadgeStyle(finStatement === 'BS')}
                >
                  BS
                </button>
                <button
                  onClick={() => setFinStatement('CF')}
                  style={statementBadgeStyle(finStatement === 'CF')}
                >
                  CF
                </button>
              </div>
            </div>
          </div>

          {comprehensiveFinancials && comprehensiveFinancials.count > 0 ? (
            <div
              style={{
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                backgroundColor: 'white',
                overflow: 'hidden',
              }}
            >
              <div style={{ padding: '16px', backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
                  <strong>Symbol:</strong> {comprehensiveFinancials.symbol} | 
                  <strong> Year:</strong> {comprehensiveFinancials.year} | 
                  <strong> Period:</strong> {comprehensiveFinancials.quarter ? `Q${comprehensiveFinancials.quarter}` : 'Annual'} | 
                  <strong> Statement:</strong> {statementMap[finStatement].label} | 
                  <strong> Items:</strong> {selectedStatementItems.length}
                </p>
                {comprehensiveFinancials.note && (
                  <p style={{ margin: '6px 0 0', fontSize: '12px', color: '#9ca3af' }}>
                    {comprehensiveFinancials.note}
                  </p>
                )}
              </div>

              {highlights.length > 0 && (
                <div style={{ display: 'grid', gap: '12px', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', padding: '16px', borderBottom: '1px solid #e5e7eb' }}>
                  {highlights.map((item) => (
                    <div key={item.key} style={{ backgroundColor: '#f8fafc', borderRadius: '8px', padding: '12px', border: '1px solid #e2e8f0' }}>
                      <div style={{ fontSize: '12px', fontWeight: 600, color: '#475569' }}>{item.label}</div>
                      <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', marginTop: '4px' }}>
                        {formatValue(item.value)}
                      </div>
                      <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>{item.key}</div>
                    </div>
                  ))}
                </div>
              )}

              {selectedStatementItems.length > 0 ? (
                <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                    <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f9fafb', zIndex: 1 }}>
                      <tr>
                        <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb', fontWeight: '600' }}>
                          Account
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb', fontWeight: '600' }}>
                          Value
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedStatementItems.map((item, index) => {
                        const bgColor = index % 2 === 0 ? '#f8fafc' : 'white';
                        return (
                          <tr key={index} style={{ backgroundColor: bgColor }}>
                            <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6' }}>
                              {item.account_nm || '-'}
                            </td>
                            <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6', textAlign: 'right', fontFamily: 'monospace' }}>
                              {formatValue(parseAmount(item.thstrm_amount) ?? item.thstrm_amount ?? '-')}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ padding: '24px', textAlign: 'center', color: '#6b7280' }}>
                  No items for this statement in the selected period.
                </div>
              )}
            </div>
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
                No financial data available for the selected period. Try a different year or quarter.
              </p>
            </div>
          )}
        </div>
      )}

      <div
        style={{
          marginTop: '24px',
          padding: '16px',
          backgroundColor: '#f9fafb',
          borderRadius: '6px',
        }}
      >
        <p style={{ fontSize: '14px', color: '#6b7280' }}>
          <strong>Popular Korean stocks:</strong> Samsung Electronics (005930),
          SK Hynix (000660), Hyundai Motor (005380), Naver (035420), Kakao (035720)
        </p>
      </div>
    </div>
  );
};
