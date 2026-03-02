import React, { useEffect, useMemo, useState } from 'react';
import { CandleChart } from '../components/CandleChart';
import { koreanMarketService } from '../services/koreanMarket';
import type {
  KoreanBondInfo,
  KoreanBondMasterItem,
  KoreanBondQuote,
  KoreanCandleData,
  KoreanBondValuation,
} from '../types/korean';

const PAGE_SIZE = 10;

const formatDate = (value?: string | null) => {
  if (!value || value.length !== 8) return '-';
  return `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;
};

const dateInputToYyyymmdd = (value: string) => value.split('-').join('');
const yyyymmddToDateInput = (value: string) => {
  if (!value || value.length !== 8) return '';
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

const formatMarketPriceSource = (source?: string | null) => {
  if (!source) return '-';
  if (source === 'middle_price') return '중간가';
  if (source === 'current_price') return '현재가';
  if (source === 'daily_close') return '일별 종가';
  return source;
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

const INTEREST_DAY_TYPE: Record<string, string> = {
  '01': '발행일',
  '02': '만기일',
  '03': '특정일',
};

const BOND_TYPE_OPTIONS: Array<{ value: string; label: string }> = [
  { value: 'A0', label: 'A0: 장내소매채권' },
  { value: 'F9', label: 'F9: 주식관련사채/소액채권' },
  { value: 'C0', label: 'C0: 국고채권' },
];

const BOND_CLASS_OPTIONS_BY_TYPE: Record<string, Array<{ value: string; label: string }>> = {
  A0: [
    { value: 'GA', label: 'GA: 국고채' },
    { value: 'MA', label: 'MA: 통안채' },
    { value: 'BA', label: 'BA: 금융채' },
    { value: 'SA', label: 'SA: 비금융특수채' },
    { value: 'CA', label: 'CA: 회사채' },
  ],
  F9: [
    { value: '03', label: '03: 장내소액채권' },
    { value: '02', label: '02: 기타채권' },
    { value: '04', label: '04: 장내주식관련사채' },
    { value: 'MM', label: 'MM: 매매종류별' },
  ],
  C0: [
    { value: 'GA', label: 'GA: 국고채' },
    { value: 'MA', label: 'MA: 통안채' },
    { value: 'BA', label: 'BA: 금융채' },
    { value: 'SA', label: 'SA: 비금융특수채' },
    { value: 'MB', label: 'MB: 지방채' },
    { value: '99', label: '99: 기타' },
  ],
};

const BOND_INTEREST_CLASS_OPTIONS_BY_TYPE: Record<
  string,
  Array<{ value: string; label: string }>
> = {
  A0: [
    { value: '11', label: '11: 할인채(고정)' },
    { value: '12', label: '12: 복리채(고정)' },
    { value: '13', label: '13: 이표채(고정)' },
    { value: '14', label: '14: 단리채(고정)' },
    { value: '15', label: '15: 복5단2(고정)' },
    { value: '19', label: '19: 기타(고정)' },
    { value: '21', label: '21: 이표채(변동)' },
    { value: '22', label: '22: 복리채(변동)' },
    { value: '23', label: '23: 단리채(변동)' },
    { value: '29', label: '29: 기타(변동)' },
  ],
  F9: [
    { value: '01', label: '01: 할인' },
    { value: '02', label: '02: 복리' },
    { value: '03', label: '03: 이표' },
    { value: '04', label: '04: 금리연동' },
    { value: '05', label: '05: 분할상환(거치복리)' },
    { value: '06', label: '06: 분할(거치단리)' },
    { value: '07', label: '07: 단리' },
    { value: '08', label: '08: FRN' },
    { value: '09', label: '09: 복5단2' },
    { value: '11', label: '11: 할인채' },
    { value: '12', label: '12: 복리채' },
    { value: '13', label: '13: 이표채' },
    { value: '14', label: '14: 단리채' },
    { value: '15', label: '15: 복5단2' },
    { value: '21', label: '21: 이표채(변동)' },
    { value: '23', label: '23: 단리채(변동)' },
  ],
  C0: [
    { value: '01', label: '01: 할인' },
    { value: '02', label: '02: 복리' },
    { value: '03', label: '03: 이표' },
    { value: '04', label: '04: 금리연동' },
    { value: '05', label: '05: 분할상환(거치복리)' },
    { value: '06', label: '06: 분할(거치단리)' },
    { value: '07', label: '07: 단리' },
    { value: '08', label: '08: FRN' },
    { value: '09', label: '09: 복5단2' },
  ],
};

const YES_NO_MAP: Record<string, string> = {
  Y: '예',
  N: '아니오',
};

const FIELD_LABELS: Record<string, string> = {
  pdno: '상품번호',
  prdt_type_cd: '상품유형코드',
  ksd_bond_item_name: '채권명',
  ksd_bond_item_eng_name: '채권영문명',
  bond_clsf_cd: '채권분류코드',
  bond_clsf_kor_name: '채권분류명',
  iso_crcy_cd: '통화코드',
  issu_dt: '발행일',
  rvnu_dt: '매출일',
  rdpt_dt: '상환일(만기)',
  mdwy_rdpt_dt: '중도상환일',
  lstg_dt: '상장일',
  lstg_abol_dt: '상장폐지일',
  frst_int_dfrm_dt: '최초이자지급일',
  rgbf_int_dfrm_dt: '직전이자지급일',
  nxtm_int_dfrm_dt: '차기이자지급일',
  int_caltm_mcnt: '이자계산기간(개월)',
  ksd_indf_frqc_uder_calc_dcnt: '이자지급주기미만(일수)',
  bond_int_dfrm_mthd_cd: '채권이자지급방법',
  int_dfrm_day_type_cd: '이자지급일유형',
  ksd_rcvg_bond_srfc_inrt: '표면이율',
  ksd_rcvg_bond_dsct_rt: '할인율',
  frn_intr: 'FRN금리',
  bond_expd_rdpt_rt: '채권만기상환율',
  expd_rdpt_rt: '만기상환율',
  bond_expd_asrc_erng_rt: '채권만기보장수익률',
  expd_asrc_erng_rt: '만기보장수익률',
  ksd_tot_issu_amt: '총발행금액',
  pnia_int_calc_unpr: '원리금이자계산단가',
  dshn_occr_yn: '부도발생여부',
  expd_exts_yn: '만기연장여부',
  dpsi_psbl_yn: '예탁가능여부',
  sprx_psbl_yn: '분리과세가능여부',
  qib_yn: 'QIB여부',
  csbd_yn: '영구채여부',
  elec_scty_yn: '전자증권여부',
  pclr_ptcr_text: '특이사항',
  tlg_rcvg_dtl_dtime: '전문수신상세일시',
};

const looksLikeDate = (value: string) =>
  value.length === 8 && /^\d{8}$/.test(value) && value !== '00000000';

const formatBondValue = (key: string, raw: unknown): string => {
  if (raw === null || raw === undefined) return '-';
  const value = String(raw).trim();
  if (!value || value === '00000000') return '-';
  if (looksLikeDate(value)) return formatDate(value);
  if (key.endsWith('_yn')) return YES_NO_MAP[value] ?? value;
  if (key === 'bond_int_dfrm_mthd_cd') return INTEREST_METHOD[value] ?? value;
  if (key === 'int_dfrm_day_type_cd') return INTEREST_DAY_TYPE[value] ?? value;

  const asNumber = Number(value.replace(/,/g, ''));
  if (Number.isFinite(asNumber) && /(_amt|_unpr|_vol)$/.test(key)) {
    return new Intl.NumberFormat('ko-KR').format(asNumber);
  }
  if (Number.isFinite(asNumber) && /(_rt|_inrt|_intr)$/.test(key)) {
    return `${asNumber.toFixed(6)}%`;
  }
  return value;
};

export const BondMarketPage: React.FC = () => {
  type BondMasterFilters = {
    bondType?: string;
    bondClassCode?: string;
    bondInterestClassCode?: string;
    listedDateFrom?: string;
    listedDateTo?: string;
    issueDateFrom?: string;
    issueDateTo?: string;
    maturityDateFrom?: string;
    maturityDateTo?: string;
  };

  const [pdno, setPdno] = useState('');
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [infoError, setInfoError] = useState<string | null>(null);
  const [data, setData] = useState<KoreanBondInfo | null>(null);
  const [quote, setQuote] = useState<KoreanBondQuote | null>(null);
  const [valuation, setValuation] = useState<KoreanBondValuation | null>(null);
  const [dailyPrices, setDailyPrices] = useState<KoreanCandleData[]>([]);
  const [dailyError, setDailyError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [bondTypeFilter, setBondTypeFilter] = useState('F9');
  const [bondClassCodeFilter, setBondClassCodeFilter] = useState('');
  const [bondInterestClassCodeFilter, setBondInterestClassCodeFilter] = useState('');
  const [listedDateFrom, setListedDateFrom] = useState('');
  const [listedDateTo, setListedDateTo] = useState('');
  const [issueDateFrom, setIssueDateFrom] = useState('');
  const [issueDateTo, setIssueDateTo] = useState('');
  const [maturityDate, setMaturityDate] = useState('');
  const [items, setItems] = useState<KoreanBondMasterItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [totalLoaded, setTotalLoaded] = useState(0);
  const [sourceFile, setSourceFile] = useState<string | null>(null);
  const [availableBondTypes, setAvailableBondTypes] = useState<Record<string, number>>({});
  const [availableBondClassCodesByType, setAvailableBondClassCodesByType] = useState<
    Record<string, Record<string, number>>
  >({});
  const [availableBondInterestCodesByType, setAvailableBondInterestCodesByType] = useState<
    Record<string, Record<string, number>>
  >({});
  const [loadingMaster, setLoadingMaster] = useState(false);
  const [masterError, setMasterError] = useState<string | null>(null);

  const searchInfo = async () => {
    const code = pdno.trim();
    if (!code) return;
    setLoadingInfo(true);
    setInfoError(null);
    setData(null);
    setQuote(null);
    setValuation(null);
    setDailyPrices([]);
    setDailyError(null);
    try {
      const [infoResult, quoteResult, valuationResult, dailyResult] =
        await Promise.allSettled([
        koreanMarketService.getBondInfo(code),
        koreanMarketService.getBondPrice(code),
        koreanMarketService.getBondValuation(code),
        koreanMarketService.getBondDailyPrice(code, 100),
      ]);

      if (infoResult.status === 'fulfilled') {
        setData(infoResult.value);
      } else {
        throw infoResult.reason;
      }

      if (quoteResult.status === 'fulfilled') {
        setQuote(quoteResult.value);
      }
      if (valuationResult.status === 'fulfilled') {
        setValuation(valuationResult.value);
      }
      if (dailyResult.status === 'fulfilled') {
        setDailyPrices(dailyResult.value);
      } else {
        setDailyError('일별 시세를 불러오지 못했습니다.');
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : '채권 정보를 불러오지 못했습니다.';
      setInfoError(`조회 실패: ${msg}`);
    } finally {
      setLoadingInfo(false);
    }
  };

  const hasMore = items.length < totalLoaded;

  const activeFilters: BondMasterFilters = useMemo(
    () => ({
      bondType: bondTypeFilter || undefined,
      bondClassCode: bondClassCodeFilter || undefined,
      bondInterestClassCode: bondInterestClassCodeFilter || undefined,
      listedDateFrom: listedDateFrom ? dateInputToYyyymmdd(listedDateFrom) : undefined,
      listedDateTo: listedDateTo ? dateInputToYyyymmdd(listedDateTo) : undefined,
      issueDateFrom: issueDateFrom ? dateInputToYyyymmdd(issueDateFrom) : undefined,
      issueDateTo: issueDateTo ? dateInputToYyyymmdd(issueDateTo) : undefined,
      maturityDateFrom: maturityDate ? dateInputToYyyymmdd(maturityDate) : undefined,
      maturityDateTo: maturityDate ? dateInputToYyyymmdd(maturityDate) : undefined,
    }),
    [
      bondTypeFilter,
      bondClassCodeFilter,
      bondInterestClassCodeFilter,
      listedDateFrom,
      listedDateTo,
      issueDateFrom,
      issueDateTo,
      maturityDate,
    ]
  );

  const loadBondMaster = async (
    nextOffset: number,
    q: string,
    reset: boolean,
    filters: BondMasterFilters = activeFilters
  ) => {
    setLoadingMaster(true);
    setMasterError(null);
    try {
      const response = await koreanMarketService.getBondMaster({
        query: q || undefined,
        ...filters,
        offset: nextOffset,
        limit: PAGE_SIZE,
        enrich: false,
        includeQuotes: false,
      });

      setTotalLoaded(response.total_loaded);
      setSourceFile(response.source_file ?? null);
      setAvailableBondTypes(response.available_bond_types ?? {});
      setAvailableBondClassCodesByType(response.available_bond_class_codes_by_type ?? {});
      setAvailableBondInterestCodesByType(
        response.available_bond_interest_class_codes_by_type ?? {}
      );
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
    loadBondMaster(0, '', true, { bondType: 'F9' });
  }, []);

  useEffect(() => {
    const validClassSet = new Set(
      (BOND_CLASS_OPTIONS_BY_TYPE[bondTypeFilter] ?? []).map((it) => it.value)
    );
    if (bondClassCodeFilter && !validClassSet.has(bondClassCodeFilter)) {
      setBondClassCodeFilter('');
    }
    const validInterestSet = new Set(
      (BOND_INTEREST_CLASS_OPTIONS_BY_TYPE[bondTypeFilter] ?? []).map((it) => it.value)
    );
    if (
      bondInterestClassCodeFilter &&
      !validInterestSet.has(bondInterestClassCodeFilter)
    ) {
      setBondInterestClassCodeFilter('');
    }
  }, [bondTypeFilter, bondClassCodeFilter, bondInterestClassCodeFilter]);

  const masterRows = useMemo(() => items, [items]);
  const classOptions = useMemo(
    () => BOND_CLASS_OPTIONS_BY_TYPE[bondTypeFilter] ?? [],
    [bondTypeFilter]
  );
  const interestOptions = useMemo(
    () => BOND_INTEREST_CLASS_OPTIONS_BY_TYPE[bondTypeFilter] ?? [],
    [bondTypeFilter]
  );

  const summaryRows: { label: string; value: React.ReactNode }[] = data
    ? [
        { label: '채권코드 (PDNO)', value: data.pdno },
        { label: '채권명', value: data.ksd_bond_item_name || '-' },
        { label: '채권영문명', value: data.ksd_bond_item_eng_name || '-' },
        { label: '채권분류', value: data.bond_clsf_kor_name || '-' },
        { label: '채권분류코드', value: data.bond_clsf_cd || '-' },
        { label: '상품유형코드', value: data.prdt_type_cd || '-' },
        { label: '통화', value: data.iso_crcy_cd || '-' },
        { label: '발행일', value: formatDate(data.issu_dt) },
        { label: '매출일', value: formatDate(data.rvnu_dt as string | null | undefined) },
        { label: '상환일 (만기)', value: formatDate(data.rdpt_dt) },
        { label: '중도상환일', value: formatDate(data.mdwy_rdpt_dt as string | null | undefined) },
        { label: '상장일', value: formatDate(data.lstg_dt) },
        { label: '상장폐지일', value: formatDate(data.lstg_abol_dt) },
        { label: '표면이율', value: formatRate(data.ksd_rcvg_bond_srfc_inrt) },
        { label: '할인율', value: formatRate(data.ksd_rcvg_bond_dsct_rt as string | null | undefined) },
        { label: '총 발행금액', value: formatAmt(data.ksd_tot_issu_amt) },
        {
          label: '이자지급주기',
          value:
            data.int_caltm_mcnt && data.int_caltm_mcnt !== '0'
              ? `${data.int_caltm_mcnt}개월`
              : '-',
        },
        {
          label: '이자지급방법',
          value: data.bond_int_dfrm_mthd_cd
            ? INTEREST_METHOD[data.bond_int_dfrm_mthd_cd] ?? data.bond_int_dfrm_mthd_cd
            : '-',
        },
        {
          label: '이자지급일유형',
          value: data.int_dfrm_day_type_cd
            ? INTEREST_DAY_TYPE[data.int_dfrm_day_type_cd] ?? data.int_dfrm_day_type_cd
            : '-',
        },
        { label: '최초이자지급일', value: formatDate(data.frst_int_dfrm_dt as string | null | undefined) },
        { label: '직전이자지급일', value: formatDate(data.rgbf_int_dfrm_dt as string | null | undefined) },
        { label: '차기이자지급일', value: formatDate(data.nxtm_int_dfrm_dt as string | null | undefined) },
        { label: '부도발생여부', value: data.dshn_occr_yn || '-' },
        { label: '만기연장여부', value: data.expd_exts_yn || '-' },
        { label: '예탁가능여부', value: data.dpsi_psbl_yn || '-' },
        { label: '분리과세가능여부', value: data.sprx_psbl_yn || '-' },
        { label: 'QIB여부', value: data.qib_yn || '-' },
        { label: '영구채여부', value: data.csbd_yn || '-' },
        { label: '전자증권여부', value: data.elec_scty_yn || '-' },
        { label: '특이사항', value: (data.pclr_ptcr_text as string | null) || '-' },
      ]
    : [];

  const allFields = useMemo(() => {
    if (!data) return [];
    return Object.entries(data)
      .filter(([, value]) => value !== null && value !== undefined && String(value).trim() !== '')
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => ({
        key,
        label: FIELD_LABELS[key] ?? key,
        value: formatBondValue(key, value),
      }));
  }, [data]);

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
          {quote && (
            <div
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid #e5e7eb',
                backgroundColor: '#f8fafc',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                gap: '8px',
                fontSize: '13px',
              }}
            >
              <div>현재가: <strong>{formatNumber(quote.current_price)}</strong></div>
              <div>전일대비: <strong>{formatNumber(quote.change)}</strong></div>
              <div>등락률: <strong>{formatPct(quote.change_percent)}</strong></div>
              <div>중간가: <strong>{formatNumber(quote.middle_price)}</strong></div>
              <div>최우선 매도/매수: <strong>{formatNumber(quote.best_ask)} / {formatNumber(quote.best_bid)}</strong></div>
              <div>수익률: <strong>{formatPct(quote.earning_rate)}</strong></div>
              <div>시가/고가/저가: <strong>{formatNumber(quote.open)} / {formatNumber(quote.high)} / {formatNumber(quote.low)}</strong></div>
              <div>거래량: <strong>{formatNumber(quote.volume)}</strong></div>
            </div>
          )}
          {valuation && (
            <div
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid #e5e7eb',
                backgroundColor: '#ecfeff',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '8px',
                fontSize: '13px',
              }}
            >
              <div>시장가격: <strong>{formatNumber(valuation.market_price)}</strong></div>
              <div>시장가격 Raw: <strong>{formatNumber(valuation.raw_market_price)}</strong></div>
              <div>시장가격 소스: <strong>{formatMarketPriceSource(valuation.market_price_source)}</strong></div>
              <div>이론 Dirty Price: <strong>{formatNumber(valuation.theoretical_dirty_price)}</strong></div>
              <div>경과이자: <strong>{formatNumber(valuation.accrued_interest)}</strong></div>
              <div>이론 Clean Price: <strong>{formatNumber(valuation.theoretical_clean_price)}</strong></div>
              <div>괴리(시장-이론): <strong>{formatNumber(valuation.mispricing)}</strong></div>
              <div>괴리율: <strong>{formatPct(valuation.mispricing_percent)}</strong></div>
              <div>표면금리/할인율: <strong>{formatPct(valuation.annual_coupon_rate)} / {formatPct(valuation.annual_yield_rate)}</strong></div>
              <div>이자주기/잔여회차: <strong>{valuation.payment_interval_months ?? '-'}개월 / {valuation.remaining_periods ?? '-'}</strong></div>
              <div>차기이자지급일: <strong>{formatDate(valuation.next_coupon_date ?? undefined)}</strong></div>
              <div>만기일: <strong>{formatDate(valuation.maturity_date ?? undefined)}</strong></div>
              <div style={{ gridColumn: '1 / -1' }}>
                계산 메모: <strong>{valuation.notes.length ? valuation.notes.join(' | ') : '-'}</strong>
              </div>
            </div>
          )}
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid #e5e7eb',
              backgroundColor: '#ffffff',
            }}
          >
            <div
              style={{
                fontSize: '13px',
                color: '#374151',
                marginBottom: '8px',
                fontWeight: 600,
              }}
            >
              장내채권현재가(일별) 바 차트
            </div>
            {dailyError && (
              <div
                style={{
                  color: '#b91c1c',
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '6px',
                  padding: '8px 10px',
                  marginBottom: '8px',
                  fontSize: '12px',
                }}
              >
                {dailyError}
              </div>
            )}
            <CandleChart data={dailyPrices} currency="KRW" height={320} />
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              {summaryRows.map(({ label, value }) => (
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
          <div
            style={{
              padding: '12px 16px',
              borderTop: '1px solid #e5e7eb',
              backgroundColor: '#f9fafb',
              fontSize: '13px',
              color: '#374151',
              fontWeight: 600,
            }}
          >
            CTPF1114R 원본 필드 전체 ({allFields.length}개)
          </div>
          <div style={{ maxHeight: '360px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {allFields.map((field) => (
                  <tr key={field.key} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td
                      style={{
                        padding: '8px 16px',
                        width: '28%',
                        color: '#6b7280',
                        fontSize: '12px',
                        backgroundColor: '#f9fafb',
                        verticalAlign: 'top',
                      }}
                    >
                      {field.label}
                      <div style={{ fontFamily: 'monospace', fontSize: '11px' }}>{field.key}</div>
                    </td>
                    <td style={{ padding: '8px 16px', fontSize: '13px', wordBreak: 'break-all' }}>
                      {field.value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
                loadBondMaster(0, q, true, activeFilters);
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
              loadBondMaster(0, q, true, activeFilters);
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
          <button
            onClick={() => {
              setQuery('');
              setSubmittedQuery('');
              setBondTypeFilter('F9');
              setBondClassCodeFilter('');
              setBondInterestClassCodeFilter('');
              setListedDateFrom('');
              setListedDateTo('');
              setIssueDateFrom('');
              setIssueDateTo('');
              setMaturityDate('');
              loadBondMaster(0, '', true, { bondType: 'F9' });
            }}
            disabled={loadingMaster}
            style={{
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              padding: '10px 16px',
              backgroundColor: 'white',
              color: '#111827',
              cursor: loadingMaster ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              whiteSpace: 'nowrap',
            }}
          >
            필터 초기화
          </button>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '10px',
            marginBottom: '12px',
          }}
        >
          <select
            value={bondTypeFilter}
            onChange={(e) => setBondTypeFilter(e.target.value)}
            style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
          >
            <option value="">유형 전체</option>
            {BOND_TYPE_OPTIONS.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={(availableBondTypes[option.value] ?? 0) === 0}
              >
                {option.label} ({formatNumber(availableBondTypes[option.value] ?? 0)}건)
              </option>
            ))}
          </select>
          <select
            value={bondClassCodeFilter}
            onChange={(e) => setBondClassCodeFilter(e.target.value)}
            style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
          >
            <option value="">분류코드 전체</option>
            {classOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label} (
                {formatNumber(
                  (availableBondClassCodesByType[bondTypeFilter] ?? {})[option.value] ?? 0
                )}
                건)
              </option>
            ))}
          </select>
          <select
            value={bondInterestClassCodeFilter}
            onChange={(e) => setBondInterestClassCodeFilter(e.target.value)}
            style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
          >
            <option value="">이자유형 전체</option>
            {interestOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label} (
                {formatNumber(
                  (availableBondInterestCodesByType[bondTypeFilter] ?? {})[option.value] ?? 0
                )}
                건)
              </option>
            ))}
          </select>
          <div>
            <div style={{ fontSize: '12px', color: '#4b5563', marginBottom: '4px' }}>상장일 시작</div>
            <input
              type="date"
              value={listedDateFrom}
              onChange={(e) => setListedDateFrom(e.target.value)}
              style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
            />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#4b5563', marginBottom: '4px' }}>상장일 종료</div>
            <input
              type="date"
              value={listedDateTo}
              onChange={(e) => setListedDateTo(e.target.value)}
              style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
            />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#4b5563', marginBottom: '4px' }}>발행일 시작</div>
            <input
              type="date"
              value={issueDateFrom}
              onChange={(e) => setIssueDateFrom(e.target.value)}
              style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
            />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#4b5563', marginBottom: '4px' }}>발행일 종료</div>
            <input
              type="date"
              value={issueDateTo}
              onChange={(e) => setIssueDateTo(e.target.value)}
              style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
            />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#4b5563', marginBottom: '4px' }}>상환일(만기일)</div>
            <input
              type="date"
              value={maturityDate}
              onChange={(e) => setMaturityDate(e.target.value)}
              style={{ width: '100%', border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px', fontSize: '13px' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '8px' }}>
          <button
            onClick={() => {
              const q = query.trim();
              setSubmittedQuery(q);
              loadBondMaster(0, q, true, activeFilters);
            }}
            disabled={loadingMaster}
            style={{
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              backgroundColor: loadingMaster ? '#9ca3af' : '#0f766e',
              color: 'white',
              cursor: loadingMaster ? 'not-allowed' : 'pointer',
              fontSize: '13px',
            }}
          >
            필터 적용
          </button>
        </div>

        <div style={{ color: '#374151', fontSize: '14px', marginBottom: '8px' }}>
          총 {formatNumber(totalLoaded)}건
          {submittedQuery ? ` | 검색어: ${submittedQuery}` : ''}
          {bondTypeFilter ? ` | 유형: ${bondTypeFilter}` : ''}
          {bondClassCodeFilter ? ` | 분류코드: ${bondClassCodeFilter}` : ''}
          {bondInterestClassCodeFilter ? ` | 이자유형: ${bondInterestClassCodeFilter}` : ''}
          {listedDateFrom ? ` | 상장일 시작: ${yyyymmddToDateInput(dateInputToYyyymmdd(listedDateFrom))}` : ''}
          {listedDateTo ? ` | 상장일 종료: ${yyyymmddToDateInput(dateInputToYyyymmdd(listedDateTo))}` : ''}
          {issueDateFrom ? ` | 발행일 시작: ${yyyymmddToDateInput(dateInputToYyyymmdd(issueDateFrom))}` : ''}
          {issueDateTo ? ` | 발행일 종료: ${yyyymmddToDateInput(dateInputToYyyymmdd(issueDateTo))}` : ''}
          {maturityDate ? ` | 상환일: ${yyyymmddToDateInput(dateInputToYyyymmdd(maturityDate))}` : ''}
          {sourceFile ? ` | source: ${sourceFile}` : ''}
        </div>
        <div style={{ color: '#6b7280', fontSize: '12px', marginBottom: '10px' }}>
          소스 유형 현황:
          {' '}
          {Object.keys(availableBondTypes).length === 0
            ? '-'
            : Object.entries(availableBondTypes)
                .map(([code, count]) => `${code} ${formatNumber(count)}건`)
                .join(' / ')}
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
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '1120px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb' }}>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>코드</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>채권명</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>유형</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>분류코드</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>이자유형코드</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>분류</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>상장일</th>
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
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.bond_type || '-'}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.bond_class_code || '-'}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.bond_interest_class_code || '-'}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{item.bond_class_name || '-'}</td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{formatDate(item.listed_date)}</td>
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
                    colSpan={11}
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
            onClick={() =>
              loadBondMaster(offset + PAGE_SIZE, submittedQuery, false, activeFilters)
            }
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
