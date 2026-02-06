/**
 * US Market page component.
 */

import React, { useState, useEffect } from 'react';
import { StockCard } from '../components/StockCard';
import { CandleChart } from '../components/CandleChart';
import { usMarketService } from '../services/usMarket';
import type { USStockQuote, USFinancialStatement, USCandleData, USPeriod, USInterval } from '../types/us';
import { formatCurrency, formatLargeNumber } from '../utils/format';

export const USMarketPage: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL'); // Apple
  const [quote, setQuote] = useState<USStockQuote | null>(null);
  const [financials, setFinancials] = useState<USFinancialStatement[] | null>(null);
  const [candleData, setCandleData] = useState<USCandleData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Chart controls
  const [period, setPeriod] = useState<USPeriod>('1mo');
  const [interval, setInterval] = useState<USInterval>('1d');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const quoteData = await usMarketService.getQuote(symbol);
      setQuote(quoteData);

      // Get candle data
      await loadCandleData();

      // Try to get financials
      try {
        const finData = await usMarketService.getFinancials(symbol);
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
      const candles = await usMarketService.getHistoricalData(
        symbol,
        period,
        interval,
        startDate || undefined,
        endDate || undefined
      );
      setCandleData(candles);
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
  }, [period, interval, startDate, endDate]);

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
        🇺🇸 US Market
      </h1>

      <div style={searchBoxStyle}>
        <input
          type="text"
          placeholder="Enter ticker symbol (e.g., AAPL, MSFT, GOOGL)"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
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
            currency="USD"
          />
          {quote.market_cap && (
            <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '6px' }}>
              <p style={{ color: '#6b7280', margin: 0 }}>
                Market Cap: <strong>${formatLargeNumber(quote.market_cap)}</strong>
              </p>
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
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Period:</span>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value as USPeriod)}
                style={selectStyle}
              >
                <option value="1d">1 Day</option>
                <option value="5d">5 Days</option>
                <option value="1mo">1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
                <option value="5y">5 Years</option>
                <option value="ytd">Year to Date</option>
                <option value="max">Max</option>
              </select>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Interval:</span>
              <select
                value={interval}
                onChange={(e) => setInterval(e.target.value as USInterval)}
                style={selectStyle}
              >
                <option value="1m">1 Minute</option>
                <option value="5m">5 Minutes</option>
                <option value="15m">15 Minutes</option>
                <option value="30m">30 Minutes</option>
                <option value="60m">60 Minutes</option>
                <option value="1d">Daily</option>
                <option value="1wk">Weekly</option>
                <option value="1mo">Monthly</option>
              </select>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '500' }}>Start Date:</span>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={selectStyle}
                placeholder="Optional"
              />
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', fontWeight: '500' }}>End Date:</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={selectStyle}
                placeholder="Optional"
              />
            </label>
          </div>

          {/* Chart Display */}
          <CandleChart data={candleData} currency="USD" height={500} />
        </div>
      )}

      {financials && financials.length > 0 && (
        <div
          style={{
            padding: '24px',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            backgroundColor: 'white',
          }}
        >
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>
            Financial Statements
          </h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                  <th style={{ textAlign: 'left', padding: '12px' }}>Year</th>
                  <th style={{ textAlign: 'right', padding: '12px' }}>Revenue</th>
                  <th style={{ textAlign: 'right', padding: '12px' }}>Operating Income</th>
                  <th style={{ textAlign: 'right', padding: '12px' }}>Net Income</th>
                  <th style={{ textAlign: 'right', padding: '12px' }}>EPS</th>
                </tr>
              </thead>
              <tbody>
                {financials.slice(0, 5).map((fin, idx) => (
                  <tr
                    key={idx}
                    style={{
                      borderBottom: '1px solid #e5e7eb',
                      backgroundColor: idx % 2 === 0 ? 'white' : '#f9fafb',
                    }}
                  >
                    <td style={{ padding: '12px' }}>{fin.year}</td>
                    <td style={{ textAlign: 'right', padding: '12px' }}>
                      {fin.revenue ? formatCurrency(fin.revenue, 'USD', 0) : 'N/A'}
                    </td>
                    <td style={{ textAlign: 'right', padding: '12px' }}>
                      {fin.operating_income ? formatCurrency(fin.operating_income, 'USD', 0) : 'N/A'}
                    </td>
                    <td style={{ textAlign: 'right', padding: '12px' }}>
                      {fin.net_income ? formatCurrency(fin.net_income, 'USD', 0) : 'N/A'}
                    </td>
                    <td style={{ textAlign: 'right', padding: '12px' }}>
                      {fin.eps ? `$${fin.eps.toFixed(2)}` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
          <strong>Popular US stocks:</strong> Apple (AAPL), Microsoft (MSFT),
          Google (GOOGL), Amazon (AMZN), Tesla (TSLA), NVIDIA (NVDA)
        </p>
      </div>
    </div>
  );
};
