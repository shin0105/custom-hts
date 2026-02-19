import React, { useState } from 'react';
import { koreanMarketService } from '../services/koreanMarket';
import type { KoreanBondInfo } from '../types/korean';

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<KoreanBondInfo | null>(null);

  const search = async () => {
    const code = pdno.trim();
    if (!code) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await koreanMarketService.getBondInfo(code);
      setData(result);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : '채권 정보를 불러오지 못했습니다.';
      setError(`조회 실패: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

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
          onKeyDown={(e) => e.key === 'Enter' && search()}
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
          onClick={search}
          disabled={loading || !pdno.trim()}
          style={{
            border: 'none',
            borderRadius: '6px',
            padding: '10px 20px',
            backgroundColor: loading || !pdno.trim() ? '#9ca3af' : '#0f766e',
            color: 'white',
            cursor: loading || !pdno.trim() ? 'not-allowed' : 'pointer',
            fontSize: '14px',
          }}
        >
          {loading ? '조회 중...' : '조회'}
        </button>
      </div>

      {error && (
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
          {error}
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

      {!loading && !data && !error && (
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
    </div>
  );
};

