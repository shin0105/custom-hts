import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { BondYieldPanel } from '../components/BondYieldPanel';
import { CandleChart } from '../components/CandleChart';
import { koreanMarketService } from '../services/koreanMarket';
import {
  Badge,
  Button,
  DefinitionTable,
  EmptyState,
  Field,
  Notice,
  Panel,
  SectionHeader,
  Select,
  SkeletonPanel,
  StatGrid,
  StatTile,
  Table,
  TableScroll,
  TextInput,
} from '../components/ui';
import { color, fontSize, space } from '../theme/tokens';
import { useMarketColors } from '../theme/marketColorContext';
import { toUserMessage } from '../utils/apiError';
import type {
  KoreanBondInfo,
  KoreanBondMasterItem,
  KoreanBondQuote,
  KoreanCandleData,
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
  const [analyticsPdno, setAnalyticsPdno] = useState<string | null>(null);
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

  const { colorFor, directionOf, glyphFor } = useMarketColors();

  const searchInfo = async () => {
    const code = pdno.trim();
    if (!code) return;
    setLoadingInfo(true);
    setInfoError(null);
    setData(null);
    setQuote(null);
    setAnalyticsPdno(null);
    setDailyPrices([]);
    setDailyError(null);
    try {
      const [infoResult, quoteResult, dailyResult] = await Promise.allSettled([
        koreanMarketService.getBondInfo(code),
        koreanMarketService.getBondPrice(code),
        koreanMarketService.getBondDailyPrice(code, 100),
      ]);

      if (infoResult.status === 'fulfilled') {
        setData(infoResult.value);
        setAnalyticsPdno(code.toUpperCase());
      } else {
        throw infoResult.reason;
      }

      if (quoteResult.status === 'fulfilled') {
        setQuote(quoteResult.value);
      }
      if (dailyResult.status === 'fulfilled') {
        setDailyPrices(dailyResult.value);
      } else {
        setDailyError('일별 시세를 불러오지 못했습니다.');
      }
    } catch (err: unknown) {
      setInfoError(toUserMessage(err, '채권 정보를 불러오지 못했습니다.'));
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
      setMasterError(toUserMessage(err, '장내채권 마스터를 불러오지 못했습니다.'));
      if (reset) {
        setItems([]);
        setTotalLoaded(0);
      }
    } finally {
      setLoadingMaster(false);
    }
  };

  useEffect(() => {
    // Initial load only; later loads go through applyFilters/resetFilters.
    loadBondMaster(0, '', true, { bondType: 'F9' });
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const applyFilters = useCallback(() => {
    const trimmed = query.trim();
    setSubmittedQuery(trimmed);
    loadBondMaster(0, trimmed, true, activeFilters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, activeFilters]);

  const resetFilters = useCallback(() => {
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /** Applied filters read as chips rather than a concatenated sentence of codes. */
  const appliedFilterChips = useMemo(() => {
    const chips: string[] = [];
    if (submittedQuery) chips.push(`검색어: ${submittedQuery}`);
    if (bondTypeFilter) {
      const label = BOND_TYPE_OPTIONS.find((o) => o.value === bondTypeFilter)?.label;
      chips.push(`유형: ${label ?? bondTypeFilter}`);
    }
    if (bondClassCodeFilter) {
      const label = (BOND_CLASS_OPTIONS_BY_TYPE[bondTypeFilter] ?? []).find(
        (o) => o.value === bondClassCodeFilter
      )?.label;
      chips.push(`분류: ${label ?? bondClassCodeFilter}`);
    }
    if (bondInterestClassCodeFilter) {
      const label = (BOND_INTEREST_CLASS_OPTIONS_BY_TYPE[bondTypeFilter] ?? []).find(
        (o) => o.value === bondInterestClassCodeFilter
      )?.label;
      chips.push(`이자유형: ${label ?? bondInterestClassCodeFilter}`);
    }
    if (listedDateFrom) {
      chips.push(`상장일 시작: ${yyyymmddToDateInput(dateInputToYyyymmdd(listedDateFrom))}`);
    }
    if (listedDateTo) {
      chips.push(`상장일 종료: ${yyyymmddToDateInput(dateInputToYyyymmdd(listedDateTo))}`);
    }
    if (issueDateFrom) {
      chips.push(`발행일 시작: ${yyyymmddToDateInput(dateInputToYyyymmdd(issueDateFrom))}`);
    }
    if (issueDateTo) {
      chips.push(`발행일 종료: ${yyyymmddToDateInput(dateInputToYyyymmdd(issueDateTo))}`);
    }
    if (maturityDate) {
      chips.push(`상환일: ${yyyymmddToDateInput(dateInputToYyyymmdd(maturityDate))}`);
    }
    return chips;
  }, [
    submittedQuery,
    bondTypeFilter,
    bondClassCodeFilter,
    bondInterestClassCodeFilter,
    listedDateFrom,
    listedDateTo,
    issueDateFrom,
    issueDateTo,
    maturityDate,
  ]);

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
    <div className="hts-page">
      <SectionHeader
        title="장내채권"
        description="채권 종목코드(PDNO)로 시세와 수익률 분석(호가별 수익률, 민평 대비, 듀레이션, 수익률 추이), 채권 기본정보를 조회합니다."
      />

      <div style={{ display: 'flex', gap: space.md, marginBottom: space.lg }}>
        <TextInput
          value={pdno}
          onChange={(e) => setPdno(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && searchInfo()}
          placeholder="채권코드 입력 (예: KR2033022D33)"
          aria-label="채권코드"
        />
        <Button onClick={searchInfo} disabled={loadingInfo || !pdno.trim()}>
          {loadingInfo ? '조회 중...' : '조회'}
        </Button>
      </div>

      {infoError && (
        <div style={{ marginBottom: space.lg }}>
          <Notice onRetry={searchInfo}>{infoError}</Notice>
        </div>
      )}

      {loadingInfo && !data && (
        <Panel title="채권 정보">
          <SkeletonPanel rows={5} height={20} />
        </Panel>
      )}

      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: space.lg }}>
          <Panel
            title={data.ksd_bond_item_name || data.pdno}
            note={
              <span className="hts-mono">
                {data.pdno}
                {data.bond_clsf_kor_name ? ` · ${data.bond_clsf_kor_name}` : ''}
              </span>
            }
          >
            {quote ? (
              <StatGrid minWidth={150}>
                <StatTile
                  label="현재가"
                  value={formatNumber(quote.current_price)}
                  valueColor={colorFor(quote.change ?? 0)}
                  emphasis
                />
                <StatTile
                  label="전일대비"
                  value={`${glyphFor(directionOf(undefined, quote.change))} ${formatNumber(
                    quote.change === null || quote.change === undefined
                      ? null
                      : Math.abs(quote.change)
                  )}`}
                  sub={formatPct(quote.change_percent)}
                  valueColor={colorFor(quote.change ?? 0)}
                />
                <StatTile label="중간가" value={formatNumber(quote.middle_price)} />
                <StatTile
                  label="최우선 매도/매수"
                  value={`${formatNumber(quote.best_ask)} / ${formatNumber(quote.best_bid)}`}
                />
                <StatTile label="수익률" value={formatPct(quote.earning_rate)} />
                <StatTile
                  label="시가/고가/저가"
                  value={`${formatNumber(quote.open)} / ${formatNumber(quote.high)} / ${formatNumber(quote.low)}`}
                />
                <StatTile label="거래량" value={formatNumber(quote.volume)} />
              </StatGrid>
            ) : (
              <EmptyState>현재가 정보를 불러오지 못했습니다.</EmptyState>
            )}
          </Panel>

          {analyticsPdno && <BondYieldPanel pdno={analyticsPdno} />}

          <Panel title="장내채권 현재가 (일별)">
            {dailyError && (
              <div style={{ marginBottom: space.md }}>
                <Notice>{dailyError}</Notice>
              </div>
            )}
            <CandleChart data={dailyPrices} currency="KRW" height={320} volumeHeight={80} />
          </Panel>

          <Panel title="채권 기본정보" flush>
            <DefinitionTable
              rows={summaryRows.map((row) => ({
                key: row.label,
                label: row.label,
                value: row.value,
              }))}
            />
          </Panel>

          <Panel title={`원본 필드 전체 (${allFields.length}개)`} note="CTPF1114R 응답" flush>
            <TableScroll maxHeight={360} bordered={false}>
              <Table>
                <tbody>
                  {allFields.map((field) => (
                    <tr key={field.key}>
                      <th
                        scope="row"
                        style={{
                          position: 'static',
                          width: '28%',
                          backgroundColor: color.surfaceMuted,
                          color: color.inkMid,
                          fontWeight: 500,
                          verticalAlign: 'top',
                        }}
                      >
                        {field.label}
                        <div
                          className="hts-mono"
                          style={{ fontSize: fontSize.xs, color: color.inkDim }}
                        >
                          {field.key}
                        </div>
                      </th>
                      <td style={{ wordBreak: 'break-all' }}>{field.value}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </TableScroll>
          </Panel>
        </div>
      )}

      {!loadingInfo && !data && !infoError && (
        <EmptyState>채권코드를 입력하고 조회 버튼을 클릭하세요.</EmptyState>
      )}

      <div style={{ marginTop: space.xxl }}>
        <SectionHeader
          title="채권 마스터 코드"
          description={`마스터 목록은 ${PAGE_SIZE}건씩 지연 로딩됩니다.`}
        />

        <div style={{ display: 'flex', gap: space.md, marginBottom: space.md }}>
          <TextInput
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                applyFilters();
              }
            }}
            placeholder="채권코드 또는 채권명 검색"
            aria-label="채권 검색"
          />
          <Button onClick={applyFilters} disabled={loadingMaster}>
            검색
          </Button>
          <Button variant="secondary" onClick={resetFilters} disabled={loadingMaster}>
            필터 초기화
          </Button>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
            gap: space.md,
            marginBottom: space.md,
          }}
        >
          <Field label="채권 유형">
            <Select
              value={bondTypeFilter}
              onChange={(e) => setBondTypeFilter(e.target.value)}
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
            </Select>
          </Field>
          <Field label="분류코드">
            <Select
              value={bondClassCodeFilter}
              onChange={(e) => setBondClassCodeFilter(e.target.value)}
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
            </Select>
          </Field>
          <Field label="이자유형">
            <Select
              value={bondInterestClassCodeFilter}
              onChange={(e) => setBondInterestClassCodeFilter(e.target.value)}
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
            </Select>
          </Field>
          <Field label="상장일 시작">
            <TextInput
              type="date"
              value={listedDateFrom}
              onChange={(e) => setListedDateFrom(e.target.value)}
            />
          </Field>
          <Field label="상장일 종료">
            <TextInput
              type="date"
              value={listedDateTo}
              onChange={(e) => setListedDateTo(e.target.value)}
            />
          </Field>
          <Field label="발행일 시작">
            <TextInput
              type="date"
              value={issueDateFrom}
              onChange={(e) => setIssueDateFrom(e.target.value)}
            />
          </Field>
          <Field label="발행일 종료">
            <TextInput
              type="date"
              value={issueDateTo}
              onChange={(e) => setIssueDateTo(e.target.value)}
            />
          </Field>
          <Field label="상환일 (만기일)">
            <TextInput
              type="date"
              value={maturityDate}
              onChange={(e) => setMaturityDate(e.target.value)}
            />
          </Field>
        </div>

        <div
          style={{
            display: 'flex',
            justifyContent: 'flex-end',
            marginBottom: space.sm,
          }}
        >
          <Button size="sm" onClick={applyFilters} disabled={loadingMaster}>
            필터 적용
          </Button>
        </div>

        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: space.sm,
            marginBottom: space.sm,
            fontSize: fontSize.md,
            color: color.inkMid,
          }}
        >
          <span>총 {formatNumber(totalLoaded)}건</span>
          {appliedFilterChips.map((chip) => (
            <Badge key={chip}>{chip}</Badge>
          ))}
          {sourceFile && (
            <span
              className="hts-mono"
              style={{ fontSize: fontSize.sm, color: color.inkDim }}
            >
              {sourceFile}
            </span>
          )}
        </div>

        {masterError && (
          <div style={{ marginBottom: space.md }}>
            <Notice onRetry={applyFilters}>{masterError}</Notice>
          </div>
        )}

        <TableScroll>
          <Table minWidth={1120}>
            <thead>
              <tr>
                <th>코드</th>
                <th>채권명</th>
                <th>유형</th>
                <th>분류코드</th>
                <th>이자유형코드</th>
                <th>분류</th>
                <th>상장일</th>
                <th>발행일</th>
                <th>만기일</th>
                <th className="hts-num">표면금리</th>
                <th className="hts-num">등락률</th>
              </tr>
            </thead>
            <tbody>
              {masterRows.map((item) => (
                <tr key={item.pdno}>
                  <td className="hts-mono">{item.pdno}</td>
                  <td>{item.name || '-'}</td>
                  <td>{item.bond_type || '-'}</td>
                  <td>{item.bond_class_code || '-'}</td>
                  <td>{item.bond_interest_class_code || '-'}</td>
                  <td>{item.bond_class_name || '-'}</td>
                  <td>{formatDate(item.listed_date)}</td>
                  <td>{formatDate(item.issue_date)}</td>
                  <td>{formatDate(item.maturity_date)}</td>
                  <td className="hts-num">
                    {item.surface_interest_rate === null ||
                    item.surface_interest_rate === undefined
                      ? '-'
                      : `${item.surface_interest_rate.toFixed(4)}%`}
                  </td>
                  <td
                    className="hts-num"
                    style={{ color: colorFor(item.change_percent ?? 0) }}
                  >
                    {formatPct(item.change_percent)}
                  </td>
                </tr>
              ))}
              {!loadingMaster && masterRows.length === 0 && (
                <tr>
                  <td colSpan={11} style={{ textAlign: 'center', color: color.inkDim }}>
                    표시할 채권 데이터가 없습니다.
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </TableScroll>

        <div
          style={{
            marginTop: space.md,
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <Button
            variant="secondary"
            onClick={() =>
              loadBondMaster(offset + PAGE_SIZE, submittedQuery, false, activeFilters)
            }
            disabled={loadingMaster || !hasMore}
          >
            {loadingMaster
              ? '불러오는 중...'
              : hasMore
              ? `${PAGE_SIZE}건 더 불러오기`
              : '마지막 페이지'}
          </Button>
        </div>
      </div>
    </div>
  );
};
