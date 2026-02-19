import React, { useEffect, useMemo, useState } from 'react';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanBondMasterItem, KoreanBondMasterResponse } from '../types/korean';

const PAGE_LIMIT = 20;

const formatNumber = (value?: number | null) => {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('ko-KR').format(value);
};

const formatPct = (value?: number | null) => {
  if (value === null || value === undefined) return '-';
  return `${value.toFixed(2)}%`;
};

const formatDate = (value?: string | null) => {
  if (!value || value.length !== 8) return '-';
  return `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;
};

export const BondMarketPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<KoreanBondMasterResponse | null>(null);

  const loadBondMaster = async (nextOffset: number, q: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await koreanMarketService.getBondMaster({
        query: q || undefined,
        offset: nextOffset,
        limit: PAGE_LIMIT,
        enrich: false,
        includeQuotes: false,
      });
      setData(response);
      setOffset(nextOffset);
    } catch (err) {
      console.error(err);
      setError('장내채권 마스터를 불러오지 못했습니다. master 파일과 API 키를 확인해주세요.');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBondMaster(0, '');
  }, []);

  const total = data?.total_loaded ?? 0;
  const canPrev = offset > 0;
  const canNext = offset + PAGE_LIMIT < total;

  const rows = useMemo<KoreanBondMasterItem[]>(() => data?.items ?? [], [data]);

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
      <h1 style={{ marginBottom: '8px' }}>장내채권 Master</h1>
      <p style={{ marginTop: 0, color: '#6b7280' }}>
        상장 채권 목록과 핵심 정보를 조회합니다.
      </p>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="채권코드 또는 채권명 검색"
          style={{
            flex: 1,
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '10px 12px',
          }}
        />
        <button
          onClick={() => {
            setSubmittedQuery(query.trim());
            loadBondMaster(0, query.trim());
          }}
          style={{
            border: 'none',
            borderRadius: '6px',
            padding: '10px 14px',
            backgroundColor: '#0f766e',
            color: 'white',
            cursor: 'pointer',
          }}
        >
          검색
        </button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ color: '#374151', fontSize: '14px' }}>
          총 {formatNumber(total)}건
          {data?.source_file ? ` | source: ${data.source_file}` : ''}
          {submittedQuery ? ` | 검색어: ${submittedQuery}` : ''}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            disabled={!canPrev || loading}
            onClick={() => loadBondMaster(Math.max(0, offset - PAGE_LIMIT), submittedQuery)}
            style={{ padding: '6px 10px' }}
          >
            이전
          </button>
          <button
            disabled={!canNext || loading}
            onClick={() => loadBondMaster(offset + PAGE_LIMIT, submittedQuery)}
            style={{ padding: '6px 10px' }}
          >
            다음
          </button>
        </div>
      </div>

      {error && <div style={{ color: '#dc2626', marginBottom: '8px' }}>{error}</div>}
      {loading && <div style={{ color: '#4b5563', marginBottom: '8px' }}>로딩 중...</div>}

      <div style={{ overflowX: 'auto', backgroundColor: 'white', border: '1px solid #e5e7eb' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '1200px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb', textAlign: 'left' }}>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>채권코드</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>채권명</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>분류</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>발행일</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>만기일</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>표면금리</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>통화</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>현재가</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>등락률</th>
              <th style={{ padding: '10px', borderBottom: '1px solid #e5e7eb' }}>거래량</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((item) => (
              <tr key={item.pdno}>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.pdno}</td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.name || '-'}</td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {item.bond_class_name || '-'}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {formatDate(item.issue_date)}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {formatDate(item.maturity_date)}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {item.surface_interest_rate === null || item.surface_interest_rate === undefined
                    ? '-'
                    : `${item.surface_interest_rate.toFixed(4)}%`}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.currency || '-'}</td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {formatNumber(item.current_price)}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {formatPct(item.change_percent)}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                  {formatNumber(item.volume)}
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={10} style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}>
                  데이터가 없습니다.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
