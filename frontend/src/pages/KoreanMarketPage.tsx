/**
 * Korean Market page component.
 */

import React, { useState, useEffect } from 'react';
import { StockCard } from '../components/StockCard';
import { CandleChart } from '../components/CandleChart';
import { koreanMarketService } from '../services/koreanMarket';
import type {
  KoreanStockQuote,
  KoreanFinancialStatement,
  KoreanCandleData,
  ChartInterval,
  MinuteInterval,
  PeriodType,
} from '../types/korean';

export const KoreanMarketPage: React.FC = () => {
  const [symbol, setSymbol] = useState('005930'); // Samsung Electronics
  const [quote, setQuote] = useState<KoreanStockQuote | null>(null);
  const [financials, setFinancials] = useState<KoreanFinancialStatement | null>(null);
  const [candleData, setCandleData] = useState<KoreanCandleData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Chart controls
  const [chartInterval, setChartInterval] = useState<ChartInterval>('daily');
  const [period, setPeriod] = useState<PeriodType>('D');
  const [minuteInterval, setMinuteInterval] = useState<MinuteInterval>(1);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [candleLimit, setCandleLimit] = useState(100);

  // Financial statement controls
  const [finYear, setFinYear] = useState<number>(new Date().getFullYear());
  const [finQuarter, setFinQuarter] = useState<number | undefined>(undefined);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get quote
      const quoteData = await koreanMarketService.getQuote(symbol);
      setQuote(quoteData);

      // Get candles
      await loadCandleData();

      // Try to get financials
      try {
        const finData = await koreanMarketService.getFinancials(
          symbol,
          finYear,
          finQuarter
        );
        setFinancials(finData);
      } catch (finError) {
        console.error('Failed to load financials:', finError);
        setFinancials(null);
      }
    } catch (err) {
      setError('Failed to load stock data. Please check the symbol and try again.');
      setQuote(null);
      setFinancials(null);
      setCandleData([]);
    } finally {
      setLoading(false);
    }
  };

  const loadCandleData = async () => {
    try {
      if (chartInterval === 'daily') {
        const candles = await koreanMarketService.getDailyCandle(
          symbol,
          period,
          true,
          candleLimit
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
            candleLimit,
            dateStr
          );
          setCandleData(candles);
        } else {
          const candles = await koreanMarketService.getMinuteCandle(
            symbol,
            minuteInterval,
            candleLimit,
            selectedDate
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
  }, [chartInterval, period, minuteInterval, selectedDate, candleLimit]);

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
              </>
            )}

            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Candles:</span>
              <select
                value={candleLimit}
                onChange={(e) => setCandleLimit(Number(e.target.value))}
                style={selectStyle}
              >
                <option value={50}>50</option>
                <option value={100}>100</option>
                <option value={200}>200</option>
                <option value={500}>500</option>
              </select>
            </label>
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
              Financial Statements
            </h2>
            <div style={{ display: 'flex', gap: '8px' }}>
              <select
                value={finYear}
                onChange={(e) => setFinYear(Number(e.target.value))}
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
                value={finQuarter || ''}
                onChange={(e) =>
                  setFinQuarter(e.target.value ? Number(e.target.value) : undefined)
                }
                style={selectStyle}
              >
                <option value="">Annual</option>
                <option value={1}>Q1</option>
                <option value={2}>Q2</option>
                <option value={3}>Q3</option>
                <option value={4}>Q4</option>
              </select>
              <button
                onClick={() => {
                  koreanMarketService
                    .getFinancials(symbol, finYear, finQuarter)
                    .then(setFinancials)
                    .catch(() => setFinancials(null));
                }}
                style={{ ...buttonStyle, padding: '8px 16px', fontSize: '14px' }}
              >
                Reload
              </button>
            </div>
          </div>

          {financials ? (
            <div
              style={{
                padding: '24px',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                backgroundColor: 'white',
              }}
            >
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <p style={{ color: '#6b7280' }}>Company</p>
                  <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                    {financials.company_name}
                  </p>
                </div>
                <div>
                  <p style={{ color: '#6b7280' }}>Period</p>
                  <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                    {financials.year}
                    {financials.quarter && ` Q${financials.quarter}`}
                  </p>
                </div>
                {financials.revenue && (
                  <div>
                    <p style={{ color: '#6b7280' }}>Revenue</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      ₩{(financials.revenue / 1e8).toFixed(2)}억
                    </p>
                  </div>
                )}
                {financials.operating_income && (
                  <div>
                    <p style={{ color: '#6b7280' }}>Operating Income</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      ₩{(financials.operating_income / 1e8).toFixed(2)}억
                    </p>
                  </div>
                )}
                {financials.net_income && (
                  <div>
                    <p style={{ color: '#6b7280' }}>Net Income</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      ₩{(financials.net_income / 1e8).toFixed(2)}억
                    </p>
                  </div>
                )}
                {financials.total_assets && (
                  <div>
                    <p style={{ color: '#6b7280' }}>Total Assets</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      ₩{(financials.total_assets / 1e8).toFixed(2)}억
                    </p>
                  </div>
                )}
                {financials.total_liabilities && (
                  <div>
                    <p style={{ color: '#6b7280' }}>Total Liabilities</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      ₩{(financials.total_liabilities / 1e8).toFixed(2)}억
                    </p>
                  </div>
                )}
                {financials.total_equity && (
                  <div>
                    <p style={{ color: '#6b7280' }}>Total Equity</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      ₩{(financials.total_equity / 1e8).toFixed(2)}억
                    </p>
                  </div>
                )}
              </div>
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
              <p style={{ color: '#6b7280' }}>
                No financial data available for the selected period
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
