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
} from '../types/korean';

export const KoreanMarketPage: React.FC = () => {
  const [symbol, setSymbol] = useState('005930'); // Samsung Electronics
  const [quote, setQuote] = useState<KoreanStockQuote | null>(null);
  const [comprehensiveFinancials, setComprehensiveFinancials] = useState<any>(null);
  const [candleData, setCandleData] = useState<KoreanCandleData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Chart controls
  const [chartInterval, setChartInterval] = useState<ChartInterval>('daily');
  const [period, setPeriod] = useState<PeriodType>('D');
  const [minuteInterval, setMinuteInterval] = useState<MinuteInterval>(1);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [minuteTime, setMinuteTime] = useState<string>('09:00');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Financial statement controls
  const [finYear, setFinYear] = useState<number>(new Date().getFullYear() - 1);
  const [finQuarter, setFinQuarter] = useState<number | undefined>(undefined);
  const [fsDivision, setFsDivision] = useState<'CFS' | 'OFS'>('CFS');

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get quote
      const quoteData = await koreanMarketService.getQuote(symbol);
      setQuote(quoteData);

      // Get candles
      await loadCandleData();

      // Try to get comprehensive financials from DART
      await loadFinancials();
    } catch (err) {
      setError('Failed to load stock data. Please check the symbol and try again.');
      setQuote(null);
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
        finQuarter,
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
              Minute time defaults to 09:00 KST.
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
              <select
                value={fsDivision}
                onChange={(e) => setFsDivision(e.target.value as 'CFS' | 'OFS')}
                style={selectStyle}
              >
                <option value="CFS">Consolidated</option>
                <option value="OFS">Separate</option>
              </select>
              <button
                onClick={loadFinancials}
                style={{ ...buttonStyle, padding: '8px 16px', fontSize: '14px' }}
              >
                Reload
              </button>
            </div>
          </div>

          {comprehensiveFinancials && comprehensiveFinancials.data ? (
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
                  <strong> Quarter:</strong> {comprehensiveFinancials.quarter || 'Annual'} | 
                  <strong> Division:</strong> {comprehensiveFinancials.fs_div} | 
                  <strong> Items:</strong> {comprehensiveFinancials.count}
                </p>
              </div>
              
              <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                  <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f9fafb', zIndex: 1 }}>
                    <tr>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb', fontWeight: '600' }}>
                        Statement
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb', fontWeight: '600' }}>
                        Account Name
                      </th>
                      <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb', fontWeight: '600' }}>
                        Amount (백만원)
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {comprehensiveFinancials.data.map((item: any, index: number) => {
                      const statementType = item.sj_nm || item.sj_div || '-';
                      const accountName = item.account_nm || '-';
                      const amount = item.thstrm_amount || '-';
                      
                      // Parse amount and format it
                      let formattedAmount = amount;
                      if (amount !== '-' && amount !== '' && !isNaN(Number(amount))) {
                        const numAmount = Number(amount);
                        formattedAmount = numAmount.toLocaleString();
                      }
                      
                      // Color coding for different statement types
                      let bgColor = 'white';
                      if (statementType.includes('재무상태표') || item.sj_div === 'BS') {
                        bgColor = index % 2 === 0 ? '#f0f9ff' : 'white';
                      } else if (statementType.includes('손익계산서') || item.sj_div === 'IS') {
                        bgColor = index % 2 === 0 ? '#f0fdf4' : 'white';
                      } else if (statementType.includes('현금흐름') || item.sj_div === 'CF') {
                        bgColor = index % 2 === 0 ? '#fef3c7' : 'white';
                      }
                      
                      return (
                        <tr key={index} style={{ backgroundColor: bgColor }}>
                          <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6', fontSize: '13px' }}>
                            {statementType}
                          </td>
                          <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6' }}>
                            {accountName}
                          </td>
                          <td style={{ padding: '8px 12px', borderBottom: '1px solid #f3f4f6', textAlign: 'right', fontFamily: 'monospace' }}>
                            {formattedAmount}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              
              <div style={{ padding: '12px', backgroundColor: '#f9fafb', borderTop: '1px solid #e5e7eb', fontSize: '12px', color: '#6b7280' }}>
                <p style={{ margin: 0 }}>
                  <strong>Legend:</strong> 
                  <span style={{ marginLeft: '12px', padding: '2px 8px', backgroundColor: '#f0f9ff', borderRadius: '4px' }}>BS: Balance Sheet (재무상태표)</span>
                  <span style={{ marginLeft: '8px', padding: '2px 8px', backgroundColor: '#f0fdf4', borderRadius: '4px' }}>IS: Income Statement (손익계산서)</span>
                  <span style={{ marginLeft: '8px', padding: '2px 8px', backgroundColor: '#fef3c7', borderRadius: '4px' }}>CF: Cash Flow (현금흐름표)</span>
                </p>
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
              <p style={{ color: '#6b7280', margin: 0 }}>
                No financial data available for the selected period. Try different year/quarter.
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
