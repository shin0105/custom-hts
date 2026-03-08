import React, { useEffect, useMemo, useState } from 'react';
import { CandleChart } from '../components/CandleChart';
import { koreanMarketService } from '../services/koreanMarket';
import type {
  KoreanCandleData,
  KoreanFuturesChartInterval,
  KoreanFuturesOptionsMasterItem,
} from '../types/korean';

type FuturesMarketDivCode = 'F' | 'O' | 'JF' | 'JO' | 'CF' | 'CM' | 'EU';
type FuturesMasterMarket = 'index' | 'stock' | 'commodity';

type ResolvedInstrument = {
  symbol: string;
  marketDivCode: FuturesMarketDivCode;
  market: FuturesMasterMarket;
  standardCode: string | null;
  name: string | null;
};

const CHART_INTERVAL_OPTIONS: Array<{
  value: KoreanFuturesChartInterval;
  label: string;
}> = [
  { value: 'daily', label: '일봉' },
  { value: 'minute', label: '분봉' },
];

const MINUTE_RANGE_OPTIONS = [
  { value: 30, label: '30분' },
  { value: 60, label: '1시간' },
  { value: 120, label: '2시간' },
  { value: 240, label: '4시간' },
  { value: 390, label: '장 전체' },
] as const;

const toIsoDate = (value: Date) => {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const addDays = (value: Date, days: number) => {
  const next = new Date(value);
  next.setDate(next.getDate() + days);
  return next;
};

const isoDateToYyyymmdd = (value: string) => {
  const normalized = value.replace(/-/g, '');
  return /^\d{8}$/.test(normalized) ? normalized : undefined;
};

const padTime = (value: number) => String(value).padStart(2, '0');

const toHhmmss = (value: string) =>
  /^\d{2}:\d{2}$/.test(value) ? `${value.replace(':', '')}00` : undefined;

const parseDateTime = (value: string) => {
  if (!/^\d{14}$/.test(value)) return null;
  const year = Number(value.slice(0, 4));
  const month = Number(value.slice(4, 6)) - 1;
  const day = Number(value.slice(6, 8));
  const hour = Number(value.slice(8, 10));
  const minute = Number(value.slice(10, 12));
  const second = Number(value.slice(12, 14));
  return new Date(year, month, day, hour, minute, second);
};

const subtractMinutes = (value: string, minutes: number) => {
  const parsed = parseDateTime(value);
  if (!parsed) return null;
  return new Date(parsed.getTime() - minutes * 60 * 1000);
};

const resolveMarketDivCode = (
  item: KoreanFuturesOptionsMasterItem
): FuturesMarketDivCode => {
  if (item.market === 'stock') {
    return item.info_type === '5' || item.info_type === '6' ? 'JO' : 'JF';
  }
  if (item.market === 'commodity') {
    return 'CF';
  }
  const optionInfoTypes = new Set(['5', '6', 'D', 'E', 'J', 'K', 'L', 'M']);
  return optionInfoTypes.has(String(item.info_type ?? '').toUpperCase()) ? 'O' : 'F';
};

const getCandidateMarketDivCodes = (
  instrument: ResolvedInstrument
): FuturesMarketDivCode[] => {
  if (instrument.market === 'index') {
    return instrument.marketDivCode === 'O' ? ['O', 'F'] : ['F', 'O'];
  }
  if (instrument.market === 'stock') {
    return instrument.marketDivCode === 'JO' ? ['JO', 'JF'] : ['JF', 'JO'];
  }
  if (instrument.marketDivCode === 'CM') {
    return ['CM', 'CF', 'EU'];
  }
  return ['CF', 'CM', 'EU'];
};

const getCandidateSymbols = (instrument: ResolvedInstrument): string[] => {
  const candidates = [instrument.symbol];
  const normalizedStandardCode = instrument.standardCode?.trim().toUpperCase();
  if (
    normalizedStandardCode &&
    normalizedStandardCode !== instrument.symbol
  ) {
    candidates.push(normalizedStandardCode);
  }
  return candidates;
};

const isHttp404Error = (err: unknown) => {
  if (!err || typeof err !== 'object') return false;
  const maybeResponse = (err as { response?: { status?: number } }).response;
  return maybeResponse?.status === 404;
};

const normalizeMasterMarket = (
  market: KoreanFuturesOptionsMasterItem['market']
): FuturesMasterMarket => {
  if (market === 'stock' || market === 'commodity') return market;
  return 'index';
};

export const DomesticFuturesOptionsPage: React.FC = () => {
  const today = new Date();
  const [standardCode, setStandardCode] = useState('');
  const [dailyStartDate, setDailyStartDate] = useState(toIsoDate(addDays(today, -3)));
  const [dailyEndDate, setDailyEndDate] = useState(toIsoDate(today));
  const [minuteDate, setMinuteDate] = useState(toIsoDate(today));
  const [minuteTime, setMinuteTime] = useState('15:30');
  const [minuteRangeMinutes, setMinuteRangeMinutes] = useState<number>(30);
  const [chartInterval, setChartInterval] =
    useState<KoreanFuturesChartInterval>('daily');
  const [resolved, setResolved] = useState<ResolvedInstrument | null>(null);
  const [dailyCandles, setDailyCandles] = useState<KoreanCandleData[]>([]);
  const [minuteCandles, setMinuteCandles] = useState<KoreanCandleData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [masterQuery, setMasterQuery] = useState('');
  const [masterItems, setMasterItems] = useState<KoreanFuturesOptionsMasterItem[]>([]);
  const [masterLoading, setMasterLoading] = useState(false);
  const [masterError, setMasterError] = useState<string | null>(null);

  const chartData = useMemo(() => {
    const rows = chartInterval === 'daily' ? dailyCandles : minuteCandles;
    return rows
      .filter(
        (row) =>
          row.date &&
          row.open !== null &&
          row.high !== null &&
          row.low !== null &&
          row.close !== null
      )
      .map((row) => ({
        date: row.date,
        open: Number(row.open),
        high: Number(row.high),
        low: Number(row.low),
        close: Number(row.close),
        volume: Number(row.volume ?? 0),
      }))
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [chartInterval, dailyCandles, minuteCandles]);

  const resolveInstrument = async (): Promise<ResolvedInstrument> => {
    const rawCode = standardCode.trim().toUpperCase();
    if (!rawCode) {
      throw new Error('표준코드를 입력하세요.');
    }

    const response = await koreanMarketService.getFuturesOptionsMaster({
      market: 'all',
      query: rawCode,
      limit: 50,
    });

    const exactMatch =
      response.items.find(
        (item) => String(item.standard_code ?? '').trim().toUpperCase() === rawCode
      ) ??
      response.items.find(
        (item) => String(item.short_code ?? '').trim().toUpperCase() === rawCode
      );

    if (!exactMatch?.short_code) {
      throw new Error('입력한 표준코드에 해당하는 선물옵션 종목을 찾지 못했습니다.');
    }

    return {
      symbol: exactMatch.short_code,
      marketDivCode: resolveMarketDivCode(exactMatch),
      market: normalizeMasterMarket(exactMatch.market),
      standardCode: exactMatch.standard_code ?? null,
      name: exactMatch.name_kr ?? null,
    };
  };

  const loadMaster = async (query?: string) => {
    setMasterLoading(true);
    setMasterError(null);
    try {
      const response = await koreanMarketService.getFuturesOptionsMaster({
        market: 'all',
        query: query?.trim() || undefined,
        limit: 100,
      });
      setMasterItems(response.items);
    } catch (err: unknown) {
      setMasterItems([]);
      setMasterError(
        err instanceof Error ? err.message : '마스터 코드 조회에 실패했습니다.'
      );
    } finally {
      setMasterLoading(false);
    }
  };

  const loadChart = async () => {
    setLoading(true);
    setError(null);

    try {
      const instrument = await resolveInstrument();
      setResolved(instrument);

      if (chartInterval === 'daily') {
        const marketDivCodes = getCandidateMarketDivCodes(instrument);
        const symbols = getCandidateSymbols(instrument);
        let candles: KoreanCandleData[] | null = null;
        let lastError: unknown = null;
        let saw404 = false;

        for (const symbol of symbols) {
          for (const marketDivCode of marketDivCodes) {
            try {
              candles = await koreanMarketService.getFuturesOptionDailyCandles({
                symbol,
                marketDivCode,
                period: 'D',
                limit: 180,
                startDate: isoDateToYyyymmdd(dailyStartDate),
                endDate: isoDateToYyyymmdd(dailyEndDate),
              });
              break;
            } catch (err) {
              lastError = err;
              if (isHttp404Error(err)) {
                saw404 = true;
                continue;
              }
              throw err;
            }
          }
          if (candles) break;
        }

        if (!candles) {
          if (saw404) {
            setDailyCandles([]);
            setMinuteCandles([]);
            return;
          }
          throw lastError instanceof Error ? lastError : new Error('일봉 데이터가 없습니다.');
        }

        const start = isoDateToYyyymmdd(dailyStartDate);
        const end = isoDateToYyyymmdd(dailyEndDate);
        setDailyCandles(
          candles.filter((candle) => {
            if (!candle.date) return false;
            if (start && candle.date < start) return false;
            if (end && candle.date > end) return false;
            return true;
          })
        );
        setMinuteCandles([]);
        return;
      }

      const marketDivCodes = getCandidateMarketDivCodes(instrument);
      const symbols = getCandidateSymbols(instrument);
      let response: Awaited<
        ReturnType<typeof koreanMarketService.getFuturesOptionMinuteCandles>
      > | null = null;
      let lastError: unknown = null;
      let saw404 = false;
      for (const symbol of symbols) {
        for (const marketDivCode of marketDivCodes) {
          try {
            response = await koreanMarketService.getFuturesOptionMinuteCandles({
              symbol,
              marketDivCode,
              timeframeSec: 60,
              date: isoDateToYyyymmdd(minuteDate),
              time: toHhmmss(minuteTime),
              includePrevious: true,
              includeFakeTick: false,
              limit: 200,
            });
            break;
          } catch (err) {
            lastError = err;
            if (isHttp404Error(err)) {
              saw404 = true;
              continue;
            }
            throw err;
          }
        }
        if (response) break;
      }
      if (!response) {
        if (saw404) {
          setMinuteCandles([]);
          setDailyCandles([]);
          return;
        }
        throw lastError instanceof Error ? lastError : new Error('분봉 데이터가 없습니다.');
      }

      const selectedDateValue = isoDateToYyyymmdd(minuteDate);
      const rangeStart = selectedDateValue
        ? subtractMinutes(
            `${selectedDateValue}${toHhmmss(minuteTime) ?? '153000'}`,
            minuteRangeMinutes
          )
        : null;

      const rows = response.candles
        .map((candle) => ({
          symbol: instrument.symbol,
          date: candle.timestamp ?? '',
          open: Number(candle.open ?? 0),
          high: Number(candle.high ?? 0),
          low: Number(candle.low ?? 0),
          close: Number(candle.close ?? 0),
          volume: Number(candle.volume ?? 0),
        }))
        .filter((candle) => {
          if (!candle.date || !selectedDateValue) return false;
          if (!candle.date.startsWith(selectedDateValue)) return false;
          if (!rangeStart) return true;
          const parsed = parseDateTime(candle.date);
          if (!parsed) return false;
          return parsed >= rangeStart;
        });

      setMinuteCandles(rows);
      setDailyCandles([]);
    } catch (err: unknown) {
      setDailyCandles([]);
      setMinuteCandles([]);
      setResolved(null);
      setError(err instanceof Error ? err.message : '차트 조회에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMaster();
  }, []);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <h1 style={{ marginBottom: '8px' }}>국내 선물옵션 차트</h1>
      <p style={{ marginTop: 0, color: '#6b7280' }}>
        표준코드로 종목을 찾은 뒤 일봉 또는 분봉 차트를 조회합니다.
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            chartInterval === 'daily'
              ? 'minmax(320px, 1.6fr) minmax(180px, 1fr) minmax(180px, 1fr) minmax(180px, 1fr) auto'
              : 'minmax(320px, 1.6fr) minmax(180px, 1fr) minmax(140px, 1fr) minmax(140px, 1fr) minmax(160px, 1fr) auto',
          gap: '12px',
          marginBottom: '12px',
        }}
      >
        <input
          value={standardCode}
          onChange={(e) => setStandardCode(e.target.value.toUpperCase())}
          placeholder="표준코드 입력"
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
        />
        <select
          value={chartInterval}
          onChange={(e) => setChartInterval(e.target.value as KoreanFuturesChartInterval)}
          style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
        >
          {CHART_INTERVAL_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {chartInterval === 'daily' ? (
          <>
            <input
              type="date"
              value={dailyStartDate}
              onChange={(e) => setDailyStartDate(e.target.value)}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '10px 12px',
              }}
            />
            <input
              type="date"
              value={dailyEndDate}
              onChange={(e) => setDailyEndDate(e.target.value)}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '10px 12px',
              }}
            />
          </>
        ) : (
          <>
            <input
              type="date"
              value={minuteDate}
              onChange={(e) => setMinuteDate(e.target.value)}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '10px 12px',
              }}
            />
            <input
              type="time"
              value={minuteTime}
              onChange={(e) => setMinuteTime(e.target.value)}
              step={60}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '10px 12px',
              }}
            />
            <select
              value={minuteRangeMinutes}
              onChange={(e) => setMinuteRangeMinutes(Number(e.target.value))}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '10px 12px',
              }}
            >
              {MINUTE_RANGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </>
        )}
        <button
          onClick={loadChart}
          disabled={loading}
          style={{
            border: 'none',
            borderRadius: '6px',
            padding: '10px 16px',
            backgroundColor: '#1d4ed8',
            color: 'white',
            cursor: loading ? 'not-allowed' : 'pointer',
            minWidth: '120px',
          }}
        >
          {loading ? '조회중' : '조회'}
        </button>
      </div>

      {resolved && (
        <div style={{ marginBottom: '12px', fontSize: '14px', color: '#374151' }}>
          단축코드: {resolved.symbol}
          {resolved.standardCode ? ` | 표준코드: ${resolved.standardCode}` : ''}
          {resolved.name ? ` | 종목명: ${resolved.name}` : ''}
        </div>
      )}

      <section
        style={{
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '12px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>
            {chartInterval === 'daily' ? '일봉 차트' : '분봉 차트'}
          </h3>
          <span style={{ color: '#6b7280', fontSize: '13px' }}>
            {chartInterval === 'daily'
              ? `조회 범위: ${dailyStartDate} ~ ${dailyEndDate}`
              : `기준: ${minuteDate} ${minuteTime} | 범위: ${padTime(
                  Math.floor(minuteRangeMinutes / 60)
                )}:${padTime(minuteRangeMinutes % 60)}`}
          </span>
        </div>
        {error && <p style={{ color: '#dc2626' }}>{error}</p>}
        {!error && chartData.length === 0 && (
          <p style={{ color: '#6b7280' }}>조회된 차트 데이터가 없습니다.</p>
        )}
        <div style={{ marginTop: '10px' }}>
          <CandleChart
            data={chartData}
            currency="KRW"
            height={420}
            primaryTimeZone="Asia/Seoul"
          />
        </div>
      </section>

      <section
        style={{
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '12px',
          marginTop: '16px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ margin: 0 }}>선물옵션 마스터 코드</h3>
            <p style={{ margin: '6px 0 0', color: '#6b7280', fontSize: '14px' }}>
              표준코드, 단축코드, 종목명으로 검색합니다.
            </p>
          </div>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(320px, 1fr) auto auto',
            gap: '12px',
            marginTop: '12px',
            marginBottom: '12px',
          }}
        >
          <input
            value={masterQuery}
            onChange={(e) => setMasterQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                loadMaster(masterQuery);
              }
            }}
            placeholder="표준코드 / 단축코드 / 종목명 검색"
            style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px 12px' }}
          />
          <button
            onClick={() => loadMaster(masterQuery)}
            disabled={masterLoading}
            style={{
              border: 'none',
              borderRadius: '6px',
              padding: '10px 16px',
              backgroundColor: '#1d4ed8',
              color: 'white',
              cursor: masterLoading ? 'not-allowed' : 'pointer',
            }}
          >
            {masterLoading ? '조회중' : '검색'}
          </button>
          <button
            onClick={() => {
              setMasterQuery('');
              loadMaster();
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

        {masterError && <p style={{ color: '#dc2626' }}>{masterError}</p>}

        <div style={{ overflowX: 'auto', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '820px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb' }}>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>시장</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>단축코드</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>표준코드</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>종목명</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>기초자산명</th>
              </tr>
            </thead>
            <tbody>
              {masterItems.map((item) => (
                <tr key={`${item.market}-${item.short_code}-${item.standard_code}`}>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                    {item.market}
                  </td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                    {item.short_code || '-'}
                  </td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                    {item.standard_code || '-'}
                  </td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                    {item.name_kr || '-'}
                  </td>
                  <td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>
                    {item.underlying_name_kr || '-'}
                  </td>
                </tr>
              ))}
              {!masterLoading && masterItems.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    style={{ padding: '16px', textAlign: 'center', color: '#6b7280' }}
                  >
                    표시할 마스터 코드가 없습니다.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
