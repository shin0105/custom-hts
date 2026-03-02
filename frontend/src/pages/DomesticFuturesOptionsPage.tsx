import React, { useEffect, useMemo, useRef, useState } from 'react';
import { CandleChart } from '../components/CandleChart';
import { koreanMarketService } from '../services/koreanMarket';
import type {
  KoreanFuturesOptionsMasterItem,
  KoreanFuturesOptionQuote,
  KoreanFuturesOptionOrderbook,
  KoreanFuturesOptionMinuteCandleResponse,
  KoreanFuturesOptionChainResponse,
} from '../types/korean';

const PAGE_SIZE = 20;

const MARKET_OPTIONS: Array<{ value: 'index' | 'stock' | 'commodity'; label: string }> = [
  { value: 'stock', label: '주식' },
  { value: 'index', label: '지수' },
  { value: 'commodity', label: '상품' },
];

const INFO_TYPE_LABELS: Record<string, Record<string, string>> = {
  stock: {
    '1': '코스피 주식선물',
    '2': '코스피 주식선물 SP',
    '3': '코스닥 주식선물',
    '4': '코스닥 주식선물 SP',
    '5': '주식 콜옵션',
    '6': '주식 풋옵션',
  },
  index: {
    '1': '지수선물',
    '2': '지수 SP',
    '3': '스타선물',
    '4': '스타 SP',
    '5': '지수 콜옵션',
    '6': '지수 풋옵션',
    '7': '변동성선물',
    '8': '변동성 SP',
    '9': '섹터선물',
    A: '섹터 SP',
    B: '미니선물',
    C: '미니 SP',
    D: '미니 콜옵션',
    E: '미니 풋옵션',
    J: '코스닥150 콜옵션',
    K: '코스닥150 풋옵션',
    L: '위클리 콜옵션',
    M: '위클리 풋옵션',
  },
  commodity: {
    '1': '선물',
    '2': 'SP선물',
    '5': '콜옵션',
    '6': '풋옵션',
  },
};

const COMMODITY_TYPE_LABELS: Record<string, string> = {
  '1': '금리',
  '2': '통화',
  '3': '상품',
};

const ATM_CLASS_LABELS: Record<string, string> = {
  '1': 'ATM',
  '2': 'ITM',
  '3': 'OTM',
};

const MONTH_CLASS_LABELS: Record<string, string> = {
  '0': '연결선물',
  '1': '최근월물',
  '2': '차근월물',
  '3': '차차근월물',
  '4': '차차차근월물',
};

const COMMODITY_UNDERLYING_LABELS: Record<string, string> = {
  B03: '3년국채',
  B05: '5년국채',
  B10: '10년국채',
  MSB: '통안증권',
  USD: '미국달러',
  JPY: '엔',
  EUR: '유로',
  GLD: '금',
  LHG: '돈육',
  CMU: 'CME미국달러',
  RFR: '3개월무위험금리',
};

const MARKET_LABELS: Record<'index' | 'stock' | 'commodity', string> = {
  index: '지수',
  stock: '주식',
  commodity: '상품',
};

const MARKET_CLASS_OPTIONS = [
  { value: '', label: 'KOSPI200' },
  { value: 'MKI', label: '미니KOSPI200' },
  { value: 'KQI', label: 'KOSDAQ150' },
  { value: 'WKM', label: 'KOSPI200 위클리(월)' },
  { value: 'WKI', label: 'KOSPI200 위클리(목)' },
] as const;

const TIMEFRAME_OPTIONS: Array<{ value: 30 | 60 | 3600; label: string }> = [
  { value: 30, label: '30초' },
  { value: 60, label: '1분' },
  { value: 3600, label: '1시간' },
];

const formatNumber = (value?: number | null) => {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('ko-KR').format(value);
};

const formatDecimal = (value?: number | null, digits = 2) => {
  if (value === null || value === undefined) return '-';
  return Number(value).toLocaleString('ko-KR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
};

const formatSignedDecimal = (value?: number | null, digits = 2) => {
  if (value === null || value === undefined) return '-';
  const numeric = Number(value);
  const sign = numeric > 0 ? '+' : '';
  return `${sign}${numeric.toLocaleString('ko-KR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })}`;
};

const toExpiryDefault = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  return `${year}${month}`;
};

const toIsoDate = (value: Date) => {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const isoDateToYyyymmdd = (value: string) => {
  if (!value) return undefined;
  const normalized = value.replace(/-/g, '');
  if (/^\d{8}$/.test(normalized)) {
    return normalized;
  }
  return undefined;
};

const formatCodeLabel = (
  code: string | null | undefined,
  labels: Record<string, string>
) => {
  const normalizedCode = (code ?? '').trim();
  if (!normalizedCode) return '-';
  const label = labels[normalizedCode.toUpperCase()] ?? labels[normalizedCode];
  return label ? `${normalizedCode} (${label})` : normalizedCode;
};

const formatInfoType = (
  market: 'index' | 'stock' | 'commodity',
  code: string | null | undefined
) => {
  const normalizedCode = (code ?? '').trim();
  if (!normalizedCode) return '-';
  const label = INFO_TYPE_LABELS[market]?.[normalizedCode.toUpperCase()] ?? INFO_TYPE_LABELS[market]?.[normalizedCode];
  return label ? `${normalizedCode} (${label})` : normalizedCode;
};

export const DomesticFuturesOptionsPage: React.FC = () => {
  const [symbol, setSymbol] = useState('101V09');
  const [expiry, setExpiry] = useState(toExpiryDefault());
  const [marketClass, setMarketClass] = useState<'' | 'MKI' | 'KQI' | 'WKM' | 'WKI'>('');
  const [timeframeSec, setTimeframeSec] = useState<30 | 60 | 3600>(60);
  const [selectedCandleDate, setSelectedCandleDate] = useState(toIsoDate(new Date()));

  const [quote, setQuote] = useState<KoreanFuturesOptionQuote | null>(null);
  const [orderbook, setOrderbook] = useState<KoreanFuturesOptionOrderbook | null>(null);
  const [minuteCandles, setMinuteCandles] = useState<KoreanFuturesOptionMinuteCandleResponse | null>(null);
  const [optionChain, setOptionChain] = useState<KoreanFuturesOptionChainResponse | null>(null);

  const [quoteLoading, setQuoteLoading] = useState(false);
  const [orderbookLoading, setOrderbookLoading] = useState(false);
  const [candleLoading, setCandleLoading] = useState(false);
  const [chainLoading, setChainLoading] = useState(false);

  const [quoteError, setQuoteError] = useState<string | null>(null);
  const [orderbookError, setOrderbookError] = useState<string | null>(null);
  const [candleError, setCandleError] = useState<string | null>(null);
  const [chainError, setChainError] = useState<string | null>(null);

  const lastChainRequestAt = useRef<number>(0);

  const [market, setMarket] = useState<'index' | 'stock' | 'commodity'>('index');
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [infoType, setInfoType] = useState('');
  const [underlyingShortCode, setUnderlyingShortCode] = useState('');
  const [items, setItems] = useState<KoreanFuturesOptionsMasterItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [totalLoaded, setTotalLoaded] = useState(0);
  const [masterLoading, setMasterLoading] = useState(false);
  const [masterError, setMasterError] = useState<string | null>(null);
  const [sourceFiles, setSourceFiles] = useState<Record<string, string | null>>({});
  const [availableMarkets, setAvailableMarkets] = useState<Record<string, number>>({});
  const [availableInfoTypesByMarket, setAvailableInfoTypesByMarket] = useState<
    Record<string, Record<string, number>>
  >({});

  const hasMore = items.length < totalLoaded;

  const infoTypeOptions = useMemo(() => {
    const table = availableInfoTypesByMarket[market] ?? {};
    return Object.entries(table).sort(([a], [b]) => a.localeCompare(b));
  }, [availableInfoTypesByMarket, market]);

  const candleChartData = useMemo(() => {
    const rows = minuteCandles?.candles ?? [];
    const normalized = rows
      .filter((row) =>
        row.timestamp &&
        row.open !== null && row.open !== undefined &&
        row.high !== null && row.high !== undefined &&
        row.low !== null && row.low !== undefined &&
        row.close !== null && row.close !== undefined
      )
      .map((row) => ({
        date: row.timestamp as string,
        open: Number(row.open),
        high: Number(row.high),
        low: Number(row.low),
        close: Number(row.close),
        volume: Number(row.volume ?? 0),
      }))
      .sort((a, b) => a.date.localeCompare(b.date));
    return normalized;
  }, [minuteCandles]);

  const loadQuote = async () => {
    setQuoteLoading(true);
    setQuoteError(null);
    try {
      const response = await koreanMarketService.getFuturesOptionQuote({
        symbol: symbol.trim().toUpperCase(),
        marketDivCode: 'F',
      });
      setQuote(response);
    } catch (err: unknown) {
      setQuote(null);
      setQuoteError(err instanceof Error ? err.message : '시세 조회에 실패했습니다.');
    } finally {
      setQuoteLoading(false);
    }
  };

  const loadOrderbook = async () => {
    setOrderbookLoading(true);
    setOrderbookError(null);
    try {
      const response = await koreanMarketService.getFuturesOptionOrderbook({
        symbol: symbol.trim().toUpperCase(),
        marketDivCode: 'F',
      });
      setOrderbook(response);
    } catch (err: unknown) {
      setOrderbook(null);
      setOrderbookError(err instanceof Error ? err.message : '호가 조회에 실패했습니다.');
    } finally {
      setOrderbookLoading(false);
    }
  };

  const loadMinuteCandles = async () => {
    setCandleLoading(true);
    setCandleError(null);
    try {
      const response = await koreanMarketService.getFuturesOptionMinuteCandles({
        symbol: symbol.trim().toUpperCase(),
        marketDivCode: 'F',
        timeframeSec,
        date: isoDateToYyyymmdd(selectedCandleDate),
        includePrevious: true,
        includeFakeTick: false,
        limit: 120,
      });
      setMinuteCandles(response);
    } catch (err: unknown) {
      setMinuteCandles(null);
      setCandleError(err instanceof Error ? err.message : '분봉 조회에 실패했습니다.');
    } finally {
      setCandleLoading(false);
    }
  };

  const loadOptionChain = async () => {
    const now = Date.now();
    if (now - lastChainRequestAt.current < 1000) {
      return;
    }
    lastChainRequestAt.current = now;

    setChainLoading(true);
    setChainError(null);
    try {
      const response = await koreanMarketService.getFuturesOptionChain({
        expiry: expiry.trim(),
        marketClass,
      });
      setOptionChain(response);
    } catch (err: unknown) {
      setOptionChain(null);
      setChainError(err instanceof Error ? err.message : '옵션 체인 조회에 실패했습니다.');
    } finally {
      setChainLoading(false);
    }
  };

  const loadAllPanels = async () => {
    await Promise.all([
      loadQuote(),
      loadOrderbook(),
      loadMinuteCandles(),
      loadOptionChain(),
    ]);
  };

  const loadMaster = async (nextOffset: number, reset: boolean) => {
    setMasterLoading(true);
    setMasterError(null);
    try {
      const q = reset ? query.trim() : submittedQuery;
      const response = await koreanMarketService.getFuturesOptionsMaster({
        market,
        query: q || undefined,
        infoType: infoType || undefined,
        underlyingShortCode: underlyingShortCode.trim() || undefined,
        offset: nextOffset,
        limit: PAGE_SIZE,
      });

      setOffset(nextOffset);
      setTotalLoaded(response.total_loaded);
      setSourceFiles(response.source_files ?? {});
      setAvailableMarkets(response.available_markets ?? {});
      setAvailableInfoTypesByMarket(response.available_info_types_by_market ?? {});
      if (reset) {
        setSubmittedQuery(q);
        setItems(response.items);
      } else {
        setItems((prev) => {
          const merged = [...prev];
          for (const row of response.items) {
            const key = `${row.market}-${row.short_code}-${row.standard_code}`;
            const exists = merged.some(
              (it) =>
                `${it.market}-${it.short_code}-${it.standard_code}` === key
            );
            if (!exists) merged.push(row);
          }
          return merged;
        });
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : '선물옵션 마스터 목록을 불러오지 못했습니다.';
      setMasterError(msg);
      if (reset) {
        setItems([]);
        setTotalLoaded(0);
      }
    } finally {
      setMasterLoading(false);
    }
  };

  useEffect(() => {
    loadMaster(0, true);
  }, [market]);

  useEffect(() => {
    loadAllPanels();
  }, []);

  return (
    <div style={{ maxWidth: '1300px', margin: '0 auto', padding: '24px' }}>
      <h1 style={{ marginBottom: '8px' }}>국내 선물옵션 (KOSPI200)</h1>
      <p style={{ marginTop: 0, color: '#6b7280' }}>
        기본시세 Core 4 API(시세/호가/분봉/콜풋)를 수동 새로고침으로 조회합니다.
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '10px',
          marginBottom: '10px',
        }}
      >
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="선물 종목코드 (예: 101V09)"
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
        />
        <input
          value={expiry}
          onChange={(e) => setExpiry(e.target.value)}
          placeholder="옵션 만기 YYYYMM"
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
        />
        <select
          value={marketClass}
          onChange={(e) => setMarketClass(e.target.value as '' | 'MKI' | 'KQI' | 'WKM' | 'WKI')}
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
        >
          {MARKET_CLASS_OPTIONS.map((option) => (
            <option key={option.value || 'KOSPI200'} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <select
          value={timeframeSec}
          onChange={(e) => setTimeframeSec(Number(e.target.value) as 30 | 60 | 3600)}
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
        >
          {TIMEFRAME_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              분봉: {option.label}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={selectedCandleDate}
          onChange={(e) => setSelectedCandleDate(e.target.value)}
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
          aria-label="분봉 조회일"
          title="분봉 조회일"
        />
        <button
          onClick={loadAllPanels}
          disabled={quoteLoading || orderbookLoading || candleLoading || chainLoading}
          style={{
            border: 'none',
            borderRadius: '6px',
            padding: '10px 16px',
            backgroundColor: '#1d4ed8',
            color: 'white',
            cursor: 'pointer',
          }}
        >
          전체 새로고침
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '12px' }}>
        <section style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>선물옵션 시세</h3>
            <button onClick={loadQuote} disabled={quoteLoading} style={{ borderRadius: '6px', border: '1px solid #d1d5db', padding: '6px 10px', background: 'white' }}>
              {quoteLoading ? '조회중' : '새로고침'}
            </button>
          </div>
          {quoteError && <p style={{ color: '#dc2626' }}>{quoteError}</p>}
          {!quote && !quoteError && <p style={{ color: '#6b7280' }}>데이터 없음</p>}
          {quote && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '10px', fontSize: '14px' }}>
              <div>종목명: {quote.name ?? '-'}</div>
              <div>현재가: {formatDecimal(quote.current_price)}</div>
              <div>전일대비: {formatSignedDecimal(quote.change)}</div>
              <div>등락률: {formatSignedDecimal(quote.change_percent)}%</div>
              <div>거래량: {formatNumber(quote.volume)}</div>
              <div>거래대금: {formatNumber(quote.trading_value)}</div>
              <div>미결제약정: {formatNumber(quote.open_interest)}</div>
              <div>미결제증감: {formatSignedDecimal(quote.open_interest_change, 0)}</div>
              <div>고가/저가: {formatDecimal(quote.high)} / {formatDecimal(quote.low)}</div>
              <div>이론가: {formatDecimal(quote.theoretical_price)}</div>
              <div>베이시스: {formatSignedDecimal(quote.basis)}</div>
              <div>시장베이시스: {formatSignedDecimal(quote.market_basis)}</div>
            </div>
          )}
        </section>

        <section style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>시세호가 (5단계)</h3>
            <button onClick={loadOrderbook} disabled={orderbookLoading} style={{ borderRadius: '6px', border: '1px solid #d1d5db', padding: '6px 10px', background: 'white' }}>
              {orderbookLoading ? '조회중' : '새로고침'}
            </button>
          </div>
          {orderbookError && <p style={{ color: '#dc2626' }}>{orderbookError}</p>}
          {orderbook && (
            <div style={{ marginTop: '10px' }}>
              <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '8px' }}>
                접수시간: {orderbook.as_of_time ?? '-'} | 총매도잔량: {formatNumber(orderbook.total_ask_quantity)} | 총매수잔량: {formatNumber(orderbook.total_bid_quantity)}
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr>
                    <th style={{ borderBottom: '1px solid #e5e7eb', padding: '6px' }}>레벨</th>
                    <th style={{ borderBottom: '1px solid #e5e7eb', padding: '6px' }}>매도호가</th>
                    <th style={{ borderBottom: '1px solid #e5e7eb', padding: '6px' }}>매도잔량</th>
                    <th style={{ borderBottom: '1px solid #e5e7eb', padding: '6px' }}>매수호가</th>
                    <th style={{ borderBottom: '1px solid #e5e7eb', padding: '6px' }}>매수잔량</th>
                  </tr>
                </thead>
                <tbody>
                  {orderbook.levels.map((level) => (
                    <tr key={level.level}>
                      <td style={{ borderBottom: '1px solid #f3f4f6', padding: '6px', textAlign: 'center' }}>{level.level}</td>
                      <td style={{ borderBottom: '1px solid #f3f4f6', padding: '6px', textAlign: 'right' }}>{formatDecimal(level.ask_price)}</td>
                      <td style={{ borderBottom: '1px solid #f3f4f6', padding: '6px', textAlign: 'right' }}>{formatNumber(level.ask_quantity)}</td>
                      <td style={{ borderBottom: '1px solid #f3f4f6', padding: '6px', textAlign: 'right' }}>{formatDecimal(level.bid_price)}</td>
                      <td style={{ borderBottom: '1px solid #f3f4f6', padding: '6px', textAlign: 'right' }}>{formatNumber(level.bid_quantity)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {!orderbook && !orderbookError && <p style={{ color: '#6b7280' }}>데이터 없음</p>}
        </section>
      </div>

      <section style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px', marginTop: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>선물옵션 분봉조회</h3>
          <button onClick={loadMinuteCandles} disabled={candleLoading} style={{ borderRadius: '6px', border: '1px solid #d1d5db', padding: '6px 10px', background: 'white' }}>
            {candleLoading ? '조회중' : '새로고침'}
          </button>
        </div>
        <div style={{ marginTop: '6px', color: '#6b7280', fontSize: '13px' }}>
          조회일: {selectedCandleDate || '-'}
        </div>
        {candleError && <p style={{ color: '#dc2626' }}>{candleError}</p>}
        <div style={{ marginTop: '10px' }}>
          <CandleChart data={candleChartData} currency="KRW" height={360} primaryTimeZone="Asia/Seoul" />
        </div>
      </section>

      <section style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '12px', marginTop: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>국내옵션전광판 콜/풋</h3>
          <button onClick={loadOptionChain} disabled={chainLoading} style={{ borderRadius: '6px', border: '1px solid #d1d5db', padding: '6px 10px', background: 'white' }}>
            {chainLoading ? '조회중' : '새로고침'}
          </button>
        </div>
        {chainError && <p style={{ color: '#dc2626' }}>{chainError}</p>}
        {optionChain && (
          <div style={{ marginTop: '10px' }}>
            <div style={{ color: '#6b7280', fontSize: '13px', marginBottom: '8px' }}>
              만기: {optionChain.expiry} | 콜 {formatNumber(optionChain.total_calls)}건 | 풋 {formatNumber(optionChain.total_puts)}건
            </div>
            <div style={{ overflowX: 'auto', border: '1px solid #e5e7eb', borderRadius: '6px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '980px', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f9fafb' }}>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>행사가</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>콜 현재가</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>콜 등락률</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>콜 거래량</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>콜 OI</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>풋 현재가</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>풋 등락률</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>풋 거래량</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #e5e7eb' }}>풋 OI</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: Math.max(optionChain.calls.length, optionChain.puts.length) }).map((_, idx) => {
                    const call = optionChain.calls[idx];
                    const put = optionChain.puts[idx];
                    return (
                      <tr key={`${call?.option_code ?? 'c'}-${put?.option_code ?? 'p'}-${idx}`}>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatDecimal(call?.strike_price ?? put?.strike_price)}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatDecimal(call?.current_price)}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatSignedDecimal(call?.change_percent)}%</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatNumber(call?.volume)}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatNumber(call?.open_interest)}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatDecimal(put?.current_price)}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatSignedDecimal(put?.change_percent)}%</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatNumber(put?.volume)}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right' }}>{formatNumber(put?.open_interest)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
        {!optionChain && !chainError && <p style={{ color: '#6b7280' }}>데이터 없음</p>}
      </section>

      <hr style={{ border: 0, borderTop: '1px solid #e5e7eb', margin: '24px 0 16px' }} />

      <h2 style={{ marginBottom: '8px' }}>국내 선물옵션 마스터</h2>
      <p style={{ marginTop: 0, color: '#6b7280' }}>
        지수/주식/상품 선물옵션 마스터를 조회하고 필터링합니다.
      </p>

      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '12px' }}>
        <select
          value={market}
          onChange={(e) => setMarket(e.target.value as 'index' | 'stock' | 'commodity')}
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', minWidth: '180px' }}
        >
          {MARKET_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label} ({formatNumber(availableMarkets[option.value] ?? 0)}건)
            </option>
          ))}
        </select>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              loadMaster(0, true);
            }
          }}
          placeholder="코드/종목명 검색"
          style={{
            flex: 1,
            minWidth: '220px',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '10px 12px',
          }}
        />

        <select
          value={infoType}
          onChange={(e) => setInfoType(e.target.value)}
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', minWidth: '200px' }}
        >
          <option value="">상품종류 전체</option>
          {infoTypeOptions.map(([code, count]) => (
            <option key={code} value={code}>
              {formatInfoType(market, code)} ({formatNumber(count)}건)
            </option>
          ))}
        </select>

        <input
          value={underlyingShortCode}
          onChange={(e) => setUnderlyingShortCode(e.target.value)}
          placeholder="기초자산 단축코드"
          style={{
            minWidth: '180px',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '10px 12px',
          }}
        />

        <button
          onClick={() => loadMaster(0, true)}
          disabled={masterLoading}
          style={{
            border: 'none',
            borderRadius: '6px',
            padding: '10px 16px',
            backgroundColor: masterLoading ? '#9ca3af' : '#1d4ed8',
            color: 'white',
            cursor: masterLoading ? 'not-allowed' : 'pointer',
          }}
        >
          검색
        </button>
        <button
          onClick={() => {
            setQuery('');
            setSubmittedQuery('');
            setInfoType('');
            setUnderlyingShortCode('');
            loadMaster(0, true);
          }}
          disabled={masterLoading}
          style={{
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '10px 16px',
            backgroundColor: 'white',
            color: '#111827',
            cursor: masterLoading ? 'not-allowed' : 'pointer',
          }}
        >
          초기화
        </button>
      </div>

      <div style={{ color: '#374151', fontSize: '14px', marginBottom: '10px' }}>
        총 {formatNumber(totalLoaded)}건
        {submittedQuery ? ` | 검색어: ${submittedQuery}` : ''}
        {infoType ? ` | 상품종류: ${formatInfoType(market, infoType)}` : ''}
        {underlyingShortCode ? ` | 기초자산코드: ${underlyingShortCode}` : ''}
        {sourceFiles[market] ? ` | source: ${sourceFiles[market]}` : ''}
      </div>

      {masterError && (
        <div
          style={{
            color: '#dc2626',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            padding: '12px',
            marginBottom: '10px',
          }}
        >
          {masterError}
        </div>
      )}

      <div style={{ overflowX: 'auto', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '1180px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>시장</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>상품종류</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>단축코드</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>표준코드</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>한글종목명</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>ATM</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>행사가</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>월물코드</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>기초자산코드</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>기초자산명</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={`${item.market}-${item.short_code}-${item.standard_code}`}>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {MARKET_LABELS[item.market] ?? item.market}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {item.market === 'commodity' && item.commodity_type
                    ? `${formatCodeLabel(item.commodity_type, COMMODITY_TYPE_LABELS)} / ${formatInfoType(item.market, item.info_type)}`
                    : formatInfoType(item.market, item.info_type)}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.short_code || '-'}</td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.standard_code || '-'}</td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.name_kr || '-'}</td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {formatCodeLabel(item.atm_class_code, ATM_CLASS_LABELS)}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.strike_price || '-'}</td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {formatCodeLabel(item.month_class_code, MONTH_CLASS_LABELS)}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {item.market === 'commodity'
                    ? formatCodeLabel(item.underlying_short_code, COMMODITY_UNDERLYING_LABELS)
                    : item.underlying_short_code || '-'}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {item.underlying_name_kr || '-'}
                </td>
              </tr>
            ))}
            {!masterLoading && items.length === 0 && (
              <tr>
                <td colSpan={10} style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>
                  표시할 선물옵션 데이터가 없습니다.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'center' }}>
        <button
          onClick={() => loadMaster(offset + PAGE_SIZE, false)}
          disabled={masterLoading || !hasMore}
          style={{
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '8px 16px',
            backgroundColor: masterLoading || !hasMore ? '#f3f4f6' : 'white',
            color: '#111827',
            cursor: masterLoading || !hasMore ? 'not-allowed' : 'pointer',
            fontSize: '14px',
          }}
        >
          {masterLoading ? '불러오는 중...' : hasMore ? '20건 더 불러오기' : '마지막 페이지'}
        </button>
      </div>
    </div>
  );
};
