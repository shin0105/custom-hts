import React, { useEffect, useMemo, useState } from 'react';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanFuturesOptionsMasterItem } from '../types/korean';

const PAGE_SIZE = 20;

const MARKET_OPTIONS: Array<{ value: 'index' | 'stock' | 'commodity'; label: string }> = [
  { value: 'stock', label: '주식' },
  { value: 'index', label: '지수' },
  { value: 'commodity', label: '상품' },
];

const formatNumber = (value?: number | null) => {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('ko-KR').format(value);
};

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

const MARKET_LABELS: Record<'index' | 'stock' | 'commodity', string> = {
  index: '지수',
  stock: '주식',
  commodity: '상품',
};

export const DomesticFuturesOptionsPage: React.FC = () => {
  const [market, setMarket] = useState<'index' | 'stock' | 'commodity'>('index');
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [infoType, setInfoType] = useState('');
  const [underlyingShortCode, setUnderlyingShortCode] = useState('');
  const [items, setItems] = useState<KoreanFuturesOptionsMasterItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [totalLoaded, setTotalLoaded] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
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

  const loadMaster = async (nextOffset: number, reset: boolean) => {
    setLoading(true);
    setError(null);
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
      setError(msg);
      if (reset) {
        setItems([]);
        setTotalLoaded(0);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMaster(0, true);
  }, [market]);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <h1 style={{ marginBottom: '8px' }}>국내 선물옵션 마스터</h1>
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
          disabled={loading}
          style={{
            border: 'none',
            borderRadius: '6px',
            padding: '10px 16px',
            backgroundColor: loading ? '#9ca3af' : '#1d4ed8',
            color: 'white',
            cursor: loading ? 'not-allowed' : 'pointer',
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
          disabled={loading}
          style={{
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '10px 16px',
            backgroundColor: 'white',
            color: '#111827',
            cursor: loading ? 'not-allowed' : 'pointer',
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

      {error && (
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
          {error}
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
            {!loading && items.length === 0 && (
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
          disabled={loading || !hasMore}
          style={{
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '8px 16px',
            backgroundColor: loading || !hasMore ? '#f3f4f6' : 'white',
            color: '#111827',
            cursor: loading || !hasMore ? 'not-allowed' : 'pointer',
            fontSize: '14px',
          }}
        >
          {loading ? '불러오는 중...' : hasMore ? '20건 더 불러오기' : '마지막 페이지'}
        </button>
      </div>
    </div>
  );
};
