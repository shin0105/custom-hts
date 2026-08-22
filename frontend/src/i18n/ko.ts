/**
 * Korean labels for the domestic market surfaces.
 *
 * The Korean pages render Korean data (DART returns 매출액, KDevelopers returns
 * 종목명) and should not wrap it in English chrome. A flat dictionary is enough
 * at this size — no i18n framework.
 */

export const ko = {
  nav: {
    brand: 'Custom HTS',
    home: '홈',
    korean: '국내주식',
    bonds: '장내채권',
    futuresOptions: '선물옵션',
    us: '해외주식',
    account: '계좌조회',
    colorConvention: '등락 색상',
  },

  common: {
    search: '조회',
    searching: '조회 중...',
    refresh: '새로고침',
    retry: '다시 시도',
    reset: '초기화',
    apply: '적용',
    loading: '불러오는 중...',
    noData: '데이터가 없습니다.',
    all: '전체',
    unitKrw: '단위: 원',
    unitEokKrw: '단위: 억원',
  },

  quote: {
    price: '현재가',
    change: '전일대비',
    changePercent: '등락률',
    open: '시가',
    high: '고가',
    low: '저가',
    previousClose: '전일종가',
    volume: '거래량',
    tradingValue: '거래대금',
    upperLimit: '상한가',
    lowerLimit: '하한가',
  },

  chart: {
    title: '차트',
    type: '차트 종류',
    daily: '일봉',
    minute: '분봉',
    weekly: '주봉',
    monthly: '월봉',
    period: '주기',
    interval: '간격',
    startDate: '시작일',
    endDate: '종료일',
    date: '기준일',
    time: '기준시각',
    minuteTimeHint: '분봉 기준시각 기본값은 15:30 (KST)입니다.',
    up: '상승',
    down: '하락',
    noData: '차트 데이터가 없습니다.',
    volume: '거래량',
  },

  valuation: {
    title: '투자지표',
    requested: '요청 기준',
    used: '적용 기준',
    fallback: '대체 적용',
    ttm: 'TTM',
    forward12m: '12개월 선행',
    actual: '확정 실적 기준',
    annual: '연간',
    quarter: '분기',
    marketCap: '시가총액',
    sharesOutstanding: '상장주식수',
  },

  financials: {
    title: '재무제표 (OpenDART)',
    incomeStatement: '손익계산서',
    balanceSheet: '재무상태표',
    cashFlow: '현금흐름표',
    consolidated: '연결',
    separate: '별도',
    account: '계정과목',
    filterPlaceholder: '계정과목 검색 (예: 매출)',
    filterNoMatch: '검색 조건에 맞는 계정과목이 없습니다.',
    amount: '금액',
    period: '기간',
    items: '항목 수',
    revenue: '매출액',
    operatingIncome: '영업이익',
    netIncome: '당기순이익',
    assets: '자산총계',
    liabilities: '부채총계',
    equity: '자본총계',
    operatingCashFlow: '영업활동현금흐름',
    investingCashFlow: '투자활동현금흐름',
    financingCashFlow: '재무활동현금흐름',
    empty: '선택한 기간의 재무 데이터가 없습니다. 다른 연도나 분기를 선택해 보세요.',
    loadFailed: '재무제표를 불러오지 못했습니다.',
  },

  estimate: {
    title: '추정실적 (KDevelopers)',
    summary: '종목 요약',
    incomeEstimates: '손익 추정',
    investmentIndicators: '투자지표 추정',
    empty: '이 종목의 추정실적 데이터가 없습니다.',
    loadFailed: '추정실적을 불러오지 못했습니다.',
  },

  stock: {
    title: '국내주식',
    searchPlaceholder: '종목명 또는 코드 검색 (예: 삼성전자, 005930)',
    loadFailed: '종목 데이터를 불러오지 못했습니다. 종목코드를 확인해 주세요.',
    valuationFailed: '투자지표를 불러오지 못했습니다.',
    popular: '자주 찾는 종목',
    recent: '최근 조회',
    searchNoResults: '검색 결과가 없습니다.',
    searchFailed: '종목 검색에 실패했습니다.',
    searchInProgress: '검색 중...',
  },

  metric: {
    revenue: '매출액',
    revenue_growth_rate: '매출액 증가율',
    operating_income: '영업이익',
    operating_income_growth_rate: '영업이익 증가율',
    net_income: '당기순이익',
    net_income_growth_rate: '순이익 증가율',
    ebitda: 'EBITDA',
    eps: 'EPS',
    eps_growth_rate: 'EPS 증가율',
    per: 'PER',
    ev_ebitda: 'EV/EBITDA',
    roe: 'ROE',
    debt_ratio: '부채비율',
    interest_coverage_ratio: '이자보상배율',
  },

  /**
   * KDevelopers returns the estimate summary under ELW-prefixed field names
   * even for ordinary stocks. These are the labels a user should see.
   */
  estimateSummary: {
    elw_short_code: '종목코드',
    hts_korean_name: '종목명',
    elw_current_price: '현재가',
    change_vs_prev_close: '전일대비',
    change_sign: '등락구분',
    change_rate: '등락률',
    cumulative_volume: '누적거래량',
    strike_price: '기준가',
  },
} as const;
