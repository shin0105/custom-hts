import React, { useEffect, useMemo, useState } from 'react';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanBondInfo, KoreanBondMasterItem } from '../types/korean';

const PAGE_SIZE = 10;

const formatDate = (value?: string | null) => {
  if (!value || value.length !== 8) return '-';
  return `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;
};

const formatRate = (value?: string | null) => {
  if (!value) return '-';
  const n = parseFloat(value);
  if (isNaN(n)) return '-';
  return `${n.toFixed(4)}%`;
};

const formatAmt = (value?: string | null) => {
  if (!value) return '-';
  const n = parseFloat(value);
  if (isNaN(n)) return '-';
  return new Intl.NumberFormat('ko-KR').format(n);
};

const formatNumber = (value?: number | null) => {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('ko-KR').format(value);
};

const formatPct = (value?: number | null) => {
  if (value === null || value === undefined) return '-';
  return `${value.toFixed(2)}%`;
};

const INTEREST_METHOD: Record<string, string> = {
  '01': '할인채',
  '02': '복리채',
  '03': '이표채(확정금리)',
  '04': '이표채(금리연동)',
  '05': '이표채(변동금리)',
  '06': '단리채',
  '07': '분할채',
  '09': '복5단2',
  '19': '기타(고정금리)',
  '29': '기타(변동금리)',
};

export const BondMarketPage: React.FC = () => {
  const [pdno, setPdno] = useState('');
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [infoError, setInfoError] = useState<string | null>(null);
  const [data, setData] = useState<KoreanBondInfo | null>(null);
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [items, setItems] = useState<KoreanBondMasterItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [totalLoaded, setTotalLoaded] = useState(0);
  const [sourceFile, setSourceFile] = useState<string | null>(null);
  const [loadingMaster, setLoadingMaster] = useState(false);
  const [masterError, setMasterError] = useState<string | null>(null);

  const searchInfo = async () => {
    const code = pdno.trim();
    if (!code) return;
    setLoadingInfo(true);
    setInfoError(null);
    setData(null);
    try {
      const result = await koreanMarketService.getBondInfo(code);
      setData(result);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : '채권 정보를 불러오지 못했습니다.';
      setInfoError(`조회 실패: ${msg}`);
    } finally {
      setLoadingInfo(false);
    }
  };

  const hasMore = items.length < totalLoaded;

  const loadBondMaster = async (nextOffset: number, q: string, reset: boolean) => {
    setLoadingMaster(true);
    setMasterError(null);
    try {
      const response = await koreanMarketService.getBondMaster({
        query: q || undefined,
        offset: nextOffset,
        limit: PAGE_SIZE,
        enrich: false,
        includeQuotes: false,
      });

      setTotalLoaded(response.total_loaded);
      setSourceFile(response.source_file ?? null);
      setOffset(nextOffset);

      if (reset) {
        setItems(response.items);
      } else {
        setItems((prev) => {
          const merged = [...prev];
          for (const row of response.items) {
            if (!merged.some((it) => it.pdno === row.pdno)) {
              merged.push(row);
            }
          }
          return merged;
        });
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : '장내채권 마스터를 불러오지 못했습니다.';
      setMasterError(msg);
      if (reset) {
        setItems([]);
        setTotalLoaded(0);
      }
    } finally {
      setLoadingMaster(false);
    }
  };

  useEffect(() => {
    loadBondMaster(0, '', true);
  }, []);

  const masterRows = useMemo(() => items, [items]);

  const rows: { label: string; value: React.ReactNode }[] = data
    ? [
        { label: '채권코드 (PDNO)', value: data.pdno },
        { label: '채권명', value: data.ksd_bond_item_name || '-' },
        { label: '채권영문명', value: data.ksd_bond_item_eng_name || '-' },
        { label: '채권분류', value: data.bond_clsf_kor_name || '-' },
        { label: '통화', value: data.iso_crcy_cd || '-' },
        { label: '발행일', value: formatDate(data.issu_dt) },
        { label: '상환일 (만기)', value: formatDate(data.rdpt_dt) },
        { label: '상장일', value: formatDate(data.lstg_dt) },
        { label: '상장폐지일', value: formatDate(data.lstg_abol_dt) },
        { label: '표면이율', value: formatRate(data.ksd_rcvg_bond_srfc_inrt) },
        { label: '총 발행금액', value: formatAmt(data.ksd_tot_issu_amt) },
        {
          label: '이자지급방법',
          value: data.bond_int_dfrm_mthd_cd
            ? INTEREST_METHOD[data.bond_int_dfrm_mthd_cd] ?? data.bond_int_dfrm_mthd_cd
            : '-',
        },
        { label: '부도발생여부', value: data.dshn_occr_yn || '-' },
        { label: '만기연장여부', value: data.expd_exts_yn || '-' },
      ]
    : [];

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '24px' }}>
      <h1 style={{ marginBottom: '8px' }}>장내채권 기본조회</h1>
      <p style={{ marginTop: 0, color: '#6b7280' }}>
        채권 종목코드(PDNO)를 입력하면 KDevelopers 장내채권 기본조회 API(CTPF1114R)로
        채권 정보를 조회합니다.
      </p>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input
          value={pdno}
          onChange={(e) => setPdno(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && searchInfo()}
          placeholder="채권코드 입력 (예: KR2033022D33)"
          style={{
            flex: 1,
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            padding: '10px 12px',
            fontSize: '14px',
          }}
        />
        <button
          onClick={searchInfo}
          disabled={loadingInfo || !pdno.trim()}
          style={{
            border: 'none',
            borderRadius: '6px',
            padding: '10px 20px',
            backgroundColor: loadingInfo || !pdno.trim() ? '#9ca3af' : '#0f766e',
            color: 'white',
            cursor: loadingInfo || !pdno.trim() ? 'not-allowed' : 'pointer',
            fontSize: '14px',
          }}
        >
          {loadingInfo ? '조회 중...' : '조회'}
        </button>
      </div>

      {infoError && (
        <div
          style={{
            color: '#dc2626',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            padding: '12px',
            marginBottom: '16px',
          }}
        >
          {infoError}
        </div>
      )}

      {data && (
        <div
          style={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              backgroundColor: '#f0fdfa',
              padding: '12px 16px',
              borderBottom: '1px solid #e5e7eb',
              fontWeight: 600,
              color: '#0f766e',
            }}
          >
            {data.ksd_bond_item_name || data.pdno}
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              {rows.map(({ label, value }) => (
                <tr
                  key={label}
                  style={{ borderBottom: '1px solid #f3f4f6' }}
                >
                  <td
                    style={{
                      padding: '10px 16px',
                      width: '40%',
                      color: '#6b7280',
                      fontSize: '14px',
                      backgroundColor: '#f9fafb',
                    }}
                  >
                    {label}
                  </td>
                  <td
                    style={{
                      padding: '10px 16px',
                      fontSize: '14px',
                      fontWeight: 500,
                    }}
                  >
                    {value}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loadingInfo && !data && !infoError && (
        <div
          style={{
            textAlign: 'center',
            color: '#9ca3af',
            padding: '48px',
            border: '1px dashed #d1d5db',
            borderRadius: '8px',
          }}
        >
          채권코드를 입력하고 조회 버튼을 클릭하세요.
        </div>
      )}

      <div style={{ marginTop: '28px' }}>
        <h2 style={{ marginBottom: '8px' }}>채권 마스터 코드</h2>
        <p style={{ marginTop: 0, color: '#6b7280' }}>
          마스터 목록은 10건씩 지연 로딩됩니다.
        </p>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                const q = query.trim();
                setSubmittedQuery(q);
                loadBondMaster(0, q, true);
              }
            }}
            placeholder="채권코드 또는 채권명 검색"
            style={{
              flex: 1,
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              padding: '10px 12px',
              fontSize: '14px',
            }}
          />
          <button
            onClick={() => {
              const q = query.trim();
              setSubmittedQuery(q);
              loadBondMaster(0, q, true);
            }}
            disabled={loadingMaster}
            style={{
              border: 'none',
              borderRadius: '6px',
              padding: '10px 20px',
              backgroundColor: loadingMaster ? '#9ca3af' : '#0f766e',
              color: 'white',
              cursor: loadingMaster ? 'not-allowed' : 'pointer',
              fontSize: '14px',
            }}
          >
            검색
          </button>
        </div>

        <div style={{ color: '#374151', fontSize: '14px', marginBottom: '8px' }}>
          총 {formatNumber(totalLoaded)}건
          {submittedQuery ? ` | 검색어: ${submittedQuery}` : ''}
          {sourceFile ? ` | source: ${sourceFile}` : ''}
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
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '860px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb' }}>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>코드</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>채권명</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>분류</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>발행일</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>만기일</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>표면금리</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>등락률</th>
              </tr>
            </thead>
            <tbody>
              {masterRows.map((item) => (
                <tr key={item.pdno}>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.pdno}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.name || '-'}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.bond_class_name || '-'}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{formatDate(item.issue_date)}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{formatDate(item.maturity_date)}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                    {item.surface_interest_rate === null || item.surface_interest_rate === undefined
                      ? '-'
                      : `${item.surface_interest_rate.toFixed(4)}%`}
                  </td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{formatPct(item.change_percent)}</td>
                </tr>
              ))}
              {!loadingMaster && masterRows.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    style={{
                      padding: '16px',
                      textAlign: 'center',
                      color: '#6b7280',
                    }}
                  >
                    표시할 채권 데이터가 없습니다.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'center' }}>
          <button
            onClick={() => loadBondMaster(offset + PAGE_SIZE, submittedQuery, false)}
            disabled={loadingMaster || !hasMore}
            style={{
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              padding: '8px 16px',
              backgroundColor: loadingMaster || !hasMore ? '#f3f4f6' : 'white',
              color: '#111827',
              cursor: loadingMaster || !hasMore ? 'not-allowed' : 'pointer',
              fontSize: '14px',
            }}
          >
            {loadingMaster ? '불러오는 중...' : hasMore ? '10건 더 불러오기' : '마지막 페이지'}
          </button>
        </div>
      </div>
    </div>
  );
};
