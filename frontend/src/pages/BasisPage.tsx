/**
 * Basis between listed futures and their underlying stock or index.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { SignedBarChart, TwoLineChart } from '../components/AnalyticsCharts';
import { Notes, Stat } from '../components/BasisParts';
import {
  card,
  formatCount,
  formatPrice,
  formatSigned,
  formatSignedPercent,
  isNumber,
  priceDigits,
  td,
  th,
} from '../components/basisFormat';
import { chartTheme, isoDate } from '../components/chartTheme';
import { OptionParityPanel } from '../components/OptionParityPanel';
import {
  apiErrorMessage,
  koreanAnalyticsService,
} from '../services/koreanAnalytics';
import type {
  KoreanBasisContract,
  KoreanBasisHistory,
  KoreanBasisSnapshot,
  KoreanBasisUnderlying,
} from '../types/koreanAnalytics';

const HISTORY_RANGES = [
  { value: 30, label: '1개월' },
  { value: 90, label: '3개월' },
  { value: 180, label: '6개월' },
] as const;

const QUICK_PICKS = ['2001', '3003', '005930', '000660'];
const MAX_SUGGESTIONS = 8;

const inputStyle: React.CSSProperties = {
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  padding: '10px 12px',
  fontSize: '14px',
  width: '100%',
};

const valuationLabel =(discrepancy?: number | null) => {
  if (!isNumber(discrepancy) || Math.abs(discrepancy) < 0.005) return '';
  return discrepancy > 0 ? '선물 고평가' : '선물 저평가';
};

export const BasisPage: React.FC = () => {
  const [underlyings, setUnderlyings] = useState<KoreanBasisUnderlying[]>([]);
  const [listError, setListError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selected, setSelected] = useState<KoreanBasisUnderlying | null>(null);
  const [rateInput, setRateInput] = useState('');
  const [dividendInput, setDividendInput] = useState('');
  const [snapshot, setSnapshot] = useState<KoreanBasisSnapshot | null>(null);
  const [snapshotLoading, setSnapshotLoading] = useState(false);
  const [snapshotError, setSnapshotError] = useState<string | null>(null);
  const [historySymbol, setHistorySymbol] = useState<string | null>(null);
  const [historyDays, setHistoryDays] = useState<number>(90);
  const [history, setHistory] = useState<KoreanBasisHistory | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const snapshotRequest = useRef(0);
  const historyRequest = useRef(0);

  useEffect(() => {
    koreanAnalyticsService
      .getBasisUnderlyings()
      .then(setUnderlyings)
      .catch((err: unknown) =>
        setListError(apiErrorMessage(err, '기초자산 목록을 불러오지 못했습니다.'))
      );
  }, []);

  const suggestions = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return [];
    return underlyings
      .filter(
        (item) =>
          item.code.toLowerCase().includes(needle) ||
          item.name.toLowerCase().includes(needle)
      )
      .slice(0, MAX_SUGGESTIONS);
  }, [search, underlyings]);

  const quickPicks = useMemo(
    () =>
      QUICK_PICKS.map((code) => underlyings.find((item) => item.code === code)).filter(
        (item): item is KoreanBasisUnderlying => Boolean(item)
      ),
    [underlyings]
  );

  const loadSnapshot = useCallback(
    async (underlying: KoreanBasisUnderlying, rateText: string, dividendText: string) => {
      const requestId = ++snapshotRequest.current;
      const rate = rateText.trim() === '' ? undefined : Number(rateText);
      const dividend = dividendText.trim() === '' ? undefined : Number(dividendText);
      if (rate !== undefined && !Number.isFinite(rate)) {
        setSnapshotError('금리는 숫자로 입력하세요.');
        return;
      }
      if (dividend !== undefined && (!Number.isFinite(dividend) || dividend < 0)) {
        setSnapshotError('예상 배당은 0 이상의 숫자로 입력하세요.');
        return;
      }
      setSnapshotLoading(true);
      setSnapshotError(null);
      try {
        const result = await koreanAnalyticsService.getBasisSnapshot(underlying.code, {
          rate,
          dividend: rate !== undefined ? dividend : undefined,
        });
        if (requestId === snapshotRequest.current) setSnapshot(result);
      } catch (err: unknown) {
        if (requestId === snapshotRequest.current) {
          setSnapshot(null);
          setSnapshotError(apiErrorMessage(err, '베이시스를 불러오지 못했습니다.'));
        }
      } finally {
        if (requestId === snapshotRequest.current) setSnapshotLoading(false);
      }
    },
    []
  );

  const loadHistory = useCallback(
    async (underlying: KoreanBasisUnderlying, symbol: string | null, days: number) => {
      const requestId = ++historyRequest.current;
      setHistoryLoading(true);
      setHistoryError(null);
      try {
        const result = await koreanAnalyticsService.getBasisHistory(underlying.code, {
          symbol: symbol ?? undefined,
          days,
        });
        if (requestId === historyRequest.current) setHistory(result);
      } catch (err: unknown) {
        if (requestId === historyRequest.current) {
          setHistory(null);
          setHistoryError(apiErrorMessage(err, '베이시스 추이를 불러오지 못했습니다.'));
        }
      } finally {
        if (requestId === historyRequest.current) setHistoryLoading(false);
      }
    },
    []
  );

  const selectUnderlying = (underlying: KoreanBasisUnderlying) => {
    setSelected(underlying);
    setSearch(underlying.name);
    setShowSuggestions(false);
    setSnapshot(null);
    setHistory(null);
    setHistorySymbol(null);
    loadSnapshot(underlying, rateInput, dividendInput);
    loadHistory(underlying, null, historyDays);
  };

  const selectContract = (contract: KoreanBasisContract) => {
    if (!selected) return;
    setHistorySymbol(contract.symbol);
    loadHistory(selected, contract.symbol, historyDays);
  };

  const changeRange = (days: number) => {
    setHistoryDays(days);
    if (selected) loadHistory(selected, historySymbol, days);
  };

  const digits = priceDigits(snapshot?.kind ?? selected?.kind);
  const front = snapshot?.contracts[0];
  const activeSymbol = historySymbol ?? history?.symbol ?? front?.symbol;
  const hasRate = rateInput.trim() !== '';

  const priceLines = useMemo(
    () =>
      (history?.points ?? []).map((point) => ({
        date: point.date,
        first: point.spot,
        second: point.futures,
      })),
    [history]
  );
  const basisBars = useMemo(
    () =>
      (history?.points ?? []).map((point) => ({
        date: point.date,
        value: point.basis_percent,
      })),
    [history]
  );

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <h1 style={{ marginBottom: '8px' }}>선물·현물 베이시스</h1>
      <p style={{ marginTop: 0, color: '#6b7280' }}>
        종목이나 지수를 고르면 상장된 선물 월물과 현물을 비교해 베이시스, 이론가 대비
        괴리율, 선물 가격에 내재된 금리를 보여줍니다. 옵션이 상장된 기초자산은 콜·풋으로
        만든 합성선물도 함께 비교합니다.
      </p>

      <div style={{ ...card, marginTop: '12px' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(260px, 2fr) minmax(140px, 1fr) minmax(140px, 1fr) auto',
            gap: '12px',
            alignItems: 'end',
          }}
        >
          <label style={{ fontSize: '12px', color: '#6b7280', position: 'relative' }}>
            기초자산 (종목명·종목코드·지수)
            <input
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setShowSuggestions(true);
              }}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => window.setTimeout(() => setShowSuggestions(false), 150)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && suggestions[0]) selectUnderlying(suggestions[0]);
              }}
              placeholder="예: 삼성전자, 005930, KOSPI200"
              style={{ ...inputStyle, marginTop: '4px' }}
            />
            {showSuggestions && suggestions.length > 0 && (
              <ul
                style={{
                  position: 'absolute',
                  zIndex: 10,
                  top: '100%',
                  left: 0,
                  right: 0,
                  margin: '4px 0 0',
                  padding: 0,
                  listStyle: 'none',
                  backgroundColor: 'white',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                  maxHeight: '280px',
                  overflowY: 'auto',
                }}
              >
                {suggestions.map((item) => (
                  <li key={item.code}>
                    <button
                      type="button"
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => selectUnderlying(item)}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        gap: '12px',
                        width: '100%',
                        padding: '8px 12px',
                        border: 'none',
                        background: 'none',
                        cursor: 'pointer',
                        fontSize: '14px',
                        color: '#111827',
                        textAlign: 'left',
                      }}
                    >
                      <span>{item.name}</span>
                      <span style={{ color: '#6b7280' }}>
                        {item.code} · {item.kind === 'index' ? '지수' : '주식'} ·{' '}
                        {item.contract_count}개 월물
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </label>
          <label style={{ fontSize: '12px', color: '#6b7280' }}>
            조달금리 (연 %)
            <input
              value={rateInput}
              onChange={(e) => setRateInput(e.target.value)}
              inputMode="decimal"
              placeholder="비우면 증권사 이론가"
              style={{ ...inputStyle, marginTop: '4px' }}
            />
          </label>
          <label style={{ fontSize: '12px', color: '#6b7280' }}>
            만기 전 예상 배당
            <input
              value={dividendInput}
              onChange={(e) => setDividendInput(e.target.value)}
              inputMode="decimal"
              disabled={!hasRate}
              placeholder={hasRate ? '0' : '금리 입력 시 사용'}
              style={{
                ...inputStyle,
                marginTop: '4px',
                backgroundColor: hasRate ? 'white' : '#f3f4f6',
              }}
            />
          </label>
          <button
            onClick={() => selected && loadSnapshot(selected, rateInput, dividendInput)}
            disabled={!selected || snapshotLoading}
            style={{
              border: 'none',
              borderRadius: '6px',
              padding: '10px 18px',
              backgroundColor: '#1d4ed8',
              color: 'white',
              cursor: !selected || snapshotLoading ? 'not-allowed' : 'pointer',
              minWidth: '110px',
              fontSize: '14px',
            }}
          >
            {snapshotLoading ? '조회중' : '새로고침'}
          </button>
        </div>

        {quickPicks.length > 0 && (
          <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
            {quickPicks.map((item) => (
              <button
                key={item.code}
                onClick={() => selectUnderlying(item)}
                style={{
                  border: '1px solid #d1d5db',
                  borderRadius: '999px',
                  padding: '4px 12px',
                  backgroundColor: selected?.code === item.code ? '#eff6ff' : 'white',
                  color: '#111827',
                  cursor: 'pointer',
                  fontSize: '13px',
                }}
              >
                {item.name}
              </button>
            ))}
          </div>
        )}
        {listError && <p style={{ color: '#dc2626', marginTop: '12px' }}>{listError}</p>}
      </div>

      {snapshotError && (
        <p style={{ color: '#dc2626', marginTop: '16px' }}>{snapshotError}</p>
      )}
      {!selected && !snapshotError && (
        <div
          style={{
            ...card,
            textAlign: 'center',
            color: '#6b7280',
            borderStyle: 'dashed',
            padding: '40px',
          }}
        >
          기초자산을 검색해 선택하세요.
          {underlyings.length > 0 &&
            ` 선물이 상장된 주식 ${
              underlyings.filter((item) => item.kind === 'stock').length
            }종목과 지수 ${
              underlyings.filter((item) => item.kind === 'index').length
            }개를 조회할 수 있습니다.`}
        </div>
      )}
      {selected && !snapshot && snapshotLoading && (
        <div style={{ ...card, color: '#6b7280' }}>시세를 불러오는 중입니다…</div>
      )}

      {snapshot && (
        <section style={card}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              flexWrap: 'wrap',
              gap: '8px',
            }}
          >
            <h2 style={{ margin: 0, fontSize: '18px' }}>
              {snapshot.underlying_name}{' '}
              <span style={{ color: '#6b7280', fontWeight: 400, fontSize: '14px' }}>
                {snapshot.underlying_code}
              </span>
            </h2>
            <span style={{ color: '#6b7280', fontSize: '13px' }}>
              {new Date(snapshot.as_of).toLocaleString('ko-KR')} 기준 ·{' '}
              {snapshot.rate_source === 'user'
                ? `이론가: 금리 ${snapshot.rate}% 적용`
                : '이론가: 증권사 제공값'}
            </span>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
              gap: '12px',
              marginTop: '12px',
            }}
          >
            <Stat
              label="현물"
              value={formatPrice(snapshot.spot, digits)}
              hint={
                snapshot.spot_source === 'futures_synced'
                  ? '선물 시세와 같은 시점'
                  : '현물 현재가'
              }
            />
            <Stat
              label={`최근월물 ${front?.expiry_month ?? ''}`}
              value={formatPrice(front?.price, digits)}
              hint={
                isNumber(front?.days_to_expiry) ? `잔존 ${front?.days_to_expiry}일` : undefined
              }
            />
            <Stat
              label="베이시스 (선물 − 현물)"
              value={formatSigned(front?.basis, digits)}
              hint={formatSignedPercent(front?.basis_percent)}
            />
            <Stat
              label="괴리율 (이론가 대비)"
              value={formatSignedPercent(front?.discrepancy_percent)}
              hint={valuationLabel(front?.discrepancy_percent) || undefined}
            />
            <Stat
              label="내재금리 (연)"
              value={formatSignedPercent(front?.implied_rate)}
              hint={
                isNumber(front?.carry_rate)
                  ? `이론가 기준 ${front.carry_rate.toFixed(2)}%`
                  : undefined
              }
            />
          </div>

          <Notes notes={snapshot.notes} />

          <div style={{ overflowX: 'auto', marginTop: '16px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ backgroundColor: '#f9fafb' }}>
                  <th style={{ ...th, textAlign: 'left' }}>월물</th>
                  <th style={th}>잔존일</th>
                  <th style={th}>현재가</th>
                  <th style={th}>매수 / 매도</th>
                  <th style={th}>베이시스</th>
                  <th style={th}>베이시스 %</th>
                  <th style={th}>호가중간 베이시스</th>
                  <th style={th}>이론가</th>
                  <th style={th}>괴리율</th>
                  <th style={th}>내재금리</th>
                  <th style={th}>거래량</th>
                  <th style={th}>미결제</th>
                </tr>
              </thead>
              <tbody>
                {snapshot.contracts.map((contract) => {
                  const active = contract.symbol === activeSymbol;
                  return (
                    <tr
                      key={contract.symbol}
                      onClick={() => selectContract(contract)}
                      title="클릭하면 이 월물의 베이시스 추이를 봅니다"
                      style={{
                        cursor: 'pointer',
                        backgroundColor: active ? '#eff6ff' : undefined,
                      }}
                    >
                      <td style={{ ...td, textAlign: 'left' }}>
                        <strong>{contract.expiry_month}</strong>{' '}
                        <span style={{ color: '#6b7280' }}>{contract.symbol}</span>
                      </td>
                      <td style={td}>{formatCount(contract.days_to_expiry)}</td>
                      <td style={td}>{formatPrice(contract.price, digits)}</td>
                      <td style={td}>
                        {formatPrice(contract.bid, digits)} / {formatPrice(contract.ask, digits)}
                      </td>
                      <td style={td}>{formatSigned(contract.basis, digits)}</td>
                      <td style={td}>{formatSignedPercent(contract.basis_percent)}</td>
                      <td style={td}>{formatSigned(contract.mid_basis, digits)}</td>
                      <td style={td}>{formatPrice(contract.theoretical_price, digits)}</td>
                      <td style={td}>
                        {formatSignedPercent(contract.discrepancy_percent)}{' '}
                        <span style={{ color: '#6b7280' }}>
                          {valuationLabel(contract.discrepancy_percent)}
                        </span>
                      </td>
                      <td style={td}>{formatSignedPercent(contract.implied_rate)}</td>
                      <td style={td}>{formatCount(contract.volume)}</td>
                      <td style={td}>{formatCount(contract.open_interest)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p style={{ color: '#6b7280', fontSize: '12px', margin: '8px 0 0' }}>
            내재금리는 현물을 사서 만기까지 보유하는 대신 선물을 살 때 시장 가격에
            반영된 연환산 비용입니다. 거래가 드문 원월물은 현재가가 오래된 체결가일
            수 있어 호가중간 베이시스를 함께 보세요.
          </p>
        </section>
      )}

      {snapshot && (
        <OptionParityPanel
          key={snapshot.underlying_code}
          underlying={snapshot.underlying_code}
          kind={snapshot.kind}
          rate={snapshot.rate_source === 'user' ? snapshot.rate ?? undefined : undefined}
          refreshToken={snapshot.as_of}
        />
      )}

      {selected && (history || historyLoading || historyError) && (
        <section style={card}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '8px',
            }}
          >
            <h2 style={{ margin: 0, fontSize: '18px' }}>
              베이시스 추이{' '}
              <span style={{ color: '#6b7280', fontWeight: 400, fontSize: '14px' }}>
                {history?.contract_name ?? ''}
              </span>
            </h2>
            <div style={{ display: 'flex', gap: '6px' }}>
              {HISTORY_RANGES.map((range) => (
                <button
                  key={range.value}
                  onClick={() => changeRange(range.value)}
                  style={{
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '13px',
                    cursor: 'pointer',
                    backgroundColor: historyDays === range.value ? '#1d4ed8' : 'white',
                    color: historyDays === range.value ? 'white' : '#111827',
                  }}
                >
                  {range.label}
                </button>
              ))}
            </div>
          </div>

          {historyError && <p style={{ color: '#dc2626' }}>{historyError}</p>}
          {historyLoading && !history && (
            <p style={{ color: '#6b7280' }}>추이를 불러오는 중입니다…</p>
          )}
          {history && history.points.length === 0 && (
            <p style={{ color: '#6b7280' }}>조회 기간에 비교할 일별 데이터가 없습니다.</p>
          )}

          {history && history.points.length > 0 && (
            <>
              {history.stats && (
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '12px',
                    marginTop: '12px',
                  }}
                >
                  <Stat
                    label="최근 베이시스"
                    value={formatSignedPercent(history.stats.latest)}
                  />
                  <Stat
                    label={`평균 (${history.stats.count}일)`}
                    value={formatSignedPercent(history.stats.mean)}
                    hint={`표준편차 ${history.stats.std.toFixed(2)}%p`}
                  />
                  <Stat
                    label="범위"
                    value={`${formatSignedPercent(history.stats.min)} ~ ${formatSignedPercent(
                      history.stats.max
                    )}`}
                  />
                  <Stat
                    label="Z-점수"
                    value={
                      isNumber(history.stats.zscore)
                        ? `${history.stats.zscore > 0 ? '+' : ''}${history.stats.zscore.toFixed(2)}`
                        : '-'
                    }
                    hint={`기간 내 하위 ${history.stats.percentile.toFixed(0)}% 위치`}
                  />
                </div>
              )}

              <h3 style={{ fontSize: '14px', margin: '16px 0 0', color: '#374151' }}>
                현물과 선물 종가
              </h3>
              <TwoLineChart
                data={priceLines}
                firstName="현물"
                secondName="선물"
                format={(value) => formatPrice(value, digits)}
              />
              <h3 style={{ fontSize: '14px', margin: '12px 0 0', color: '#374151' }}>
                베이시스 (현물 대비 %)
              </h3>
              <SignedBarChart
                data={basisBars}
                name="베이시스"
                positiveLabel="선물이 현물보다 높음 (콘탱고)"
                negativeLabel="선물이 현물보다 낮음 (백워데이션)"
                positiveColor={chartTheme.series2}
                negativeColor={chartTheme.series1}
                format={(value) => `${value.toFixed(2)}%`}
              />

              <details style={{ marginTop: '12px' }}>
                <summary style={{ cursor: 'pointer', color: '#374151', fontSize: '13px' }}>
                  표로 보기 ({history.points.length}일)
                </summary>
                <div style={{ maxHeight: '320px', overflowY: 'auto', marginTop: '8px' }}>
                  <table
                    style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}
                  >
                    <thead>
                      <tr style={{ backgroundColor: '#f9fafb' }}>
                        <th style={{ ...th, textAlign: 'left' }}>일자</th>
                        <th style={th}>현물</th>
                        <th style={th}>선물</th>
                        <th style={th}>베이시스</th>
                        <th style={th}>베이시스 %</th>
                        <th style={th}>내재금리</th>
                        <th style={th}>선물 거래량</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...history.points].reverse().map((point) => (
                        <tr key={point.date}>
                          <td style={{ ...td, textAlign: 'left' }}>{isoDate(point.date)}</td>
                          <td style={td}>{formatPrice(point.spot, digits)}</td>
                          <td style={td}>{formatPrice(point.futures, digits)}</td>
                          <td style={td}>{formatSigned(point.basis, digits)}</td>
                          <td style={td}>{formatSignedPercent(point.basis_percent)}</td>
                          <td style={td}>{formatSignedPercent(point.implied_rate)}</td>
                          <td style={td}>{formatCount(point.volume)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </details>
              <Notes notes={history.notes} />
            </>
          )}
        </section>
      )}
    </div>
  );
};
