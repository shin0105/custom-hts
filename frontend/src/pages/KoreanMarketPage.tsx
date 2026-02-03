/**
 * Korean Market page component.
 */

import React, { useState } from 'react';
import { StockCard } from '../components/StockCard';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanStockQuote, KoreanFinancialStatement } from '../types/korean';

export const KoreanMarketPage: React.FC = () => {
  const [symbol, setSymbol] = useState('005930'); // Samsung Electronics
  const [quote, setQuote] = useState<KoreanStockQuote | null>(null);
  const [financials, setFinancials] = useState<KoreanFinancialStatement | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const quoteData = await koreanMarketService.getQuote(symbol);
      setQuote(quoteData);

      // Try to get financials
      try {
        const finData = await koreanMarketService.getFinancials(symbol);
        setFinancials(finData);
      } catch (finError) {
        console.error('Failed to load financials:', finError);
        setFinancials(null);
      }
    } catch (err) {
      setError('Failed to load stock data. Please check the symbol and try again.');
      setQuote(null);
      setFinancials(null);
    } finally {
      setLoading(false);
    }
  };

  const containerStyle: React.CSSProperties = {
    maxWidth: '1200px',
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

      {financials && (
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
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <p style={{ color: '#6b7280' }}>Company</p>
              <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                {financials.company_name}
              </p>
            </div>
            <div>
              <p style={{ color: '#6b7280' }}>Year</p>
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
          <strong>Popular Korean stocks:</strong> Samsung Electronics (005930),
          SK Hynix (000660), Hyundai Motor (005380), Naver (035420), Kakao (035720)
        </p>
      </div>
    </div>
  );
};
