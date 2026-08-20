/**
 * CandleChart component for displaying candlestick charts with volume.
 */

import React from 'react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  Customized,
} from 'recharts';
import { color, fontSize, radius, shadow, space, tabularNums } from '../theme/tokens';
import { useMarketColors } from '../theme/marketColorContext';
import type { ColorConvention } from '../utils/marketColors';
import { ko } from '../i18n/ko';

export interface CandleData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/** A candle plus the presentation fields the chart derives from it. */
interface ChartRow extends CandleData {
  timestamp: number;
  hasTime: boolean;
  timeZone?: string;
  secondaryTimeZone?: string;
  locale: string;
}

interface CandleChartProps {
  data: CandleData[];
  currency?: 'USD' | 'KRW';
  height?: number;
  /** Height of the volume pane below the price pane. */
  volumeHeight?: number;
  primaryTimeZone?: string;
  secondaryTimeZone?: string;
  /**
   * Pins the up/down colors instead of following the user's preference.
   * The US market page pins `'global'`.
   */
  colorConvention?: ColorConvention;
}

const KST_TIMEZONE = 'Asia/Seoul';

const isKoreanDate = (dateStr: string) => /^\d{8}(\d{6})?$/.test(dateStr);

const parseTimestamp = (dateStr: string): number => {
  if (isKoreanDate(dateStr)) {
    const year = Number(dateStr.slice(0, 4));
    const month = Number(dateStr.slice(4, 6)) - 1;
    const day = Number(dateStr.slice(6, 8));
    const hour = dateStr.length >= 10 ? Number(dateStr.slice(8, 10)) : 0;
    const minute = dateStr.length >= 12 ? Number(dateStr.slice(10, 12)) : 0;
    const second = dateStr.length >= 14 ? Number(dateStr.slice(12, 14)) : 0;
    const utcMillis = Date.UTC(year, month, day, hour, minute, second);
    return utcMillis - 9 * 60 * 60 * 1000;
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day).getTime();
  }

  if (/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$/.test(dateStr)) {
    const normalized = dateStr.replace(' ', 'T');
    const parsed = new Date(normalized);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.getTime();
    }
  }

  return Date.now();
};

const formatDateLabel = (
  timestamp: number,
  withTime: boolean,
  timeZone: string | undefined,
  locale: string
) => {
  const options: Intl.DateTimeFormatOptions = withTime
    ? {
        timeZone,
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      }
    : { timeZone, month: '2-digit', day: '2-digit' };
  return new Intl.DateTimeFormat(locale, options).format(new Date(timestamp));
};

const formatTooltipLabel = (
  timestamp: number,
  withTime: boolean,
  timeZone: string | undefined,
  locale: string
) => {
  const options: Intl.DateTimeFormatOptions = withTime
    ? { timeZone, dateStyle: 'medium', timeStyle: 'short' }
    : { timeZone, dateStyle: 'medium' };
  return new Intl.DateTimeFormat(locale, options).format(new Date(timestamp));
};

const formatVolume = (value: number) => {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toLocaleString();
};

interface CandleTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: ChartRow }>;
  currency?: 'USD' | 'KRW';
  upColor: string;
  downColor: string;
  flatColor: string;
}

// Custom tooltip
const CustomTooltip: React.FC<CandleTooltipProps> = ({
  active,
  payload,
  currency = 'USD',
  upColor,
  downColor,
  flatColor,
}) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const hasTime = data.hasTime;
  const locale = data.locale ?? 'en-US';
  const dateLabel = formatTooltipLabel(
    data.timestamp,
    hasTime,
    data.timeZone,
    locale
  );
  const secondaryLabel = data.secondaryTimeZone
    ? formatTooltipLabel(data.timestamp, hasTime, data.secondaryTimeZone, locale)
    : null;
  const change = data.close - data.open;
  const changePercent =
    data.open !== 0 ? ((change / data.open) * 100).toFixed(2) : '0.00';
  const changeColor =
    change > 0 ? upColor : change < 0 ? downColor : flatColor;

  const formatPrice = (value: number) => {
    if (currency === 'KRW') {
      return `₩${value.toLocaleString('ko-KR')}`;
    }
    return `$${value.toFixed(2)}`;
  };

  const rows: Array<[string, string]> = [
    [ko.quote.open, formatPrice(data.open)],
    [ko.quote.high, formatPrice(data.high)],
    [ko.quote.low, formatPrice(data.low)],
    ['종가', formatPrice(data.close)],
  ];

  return (
    <div
      style={{
        backgroundColor: color.surface,
        border: `1px solid ${color.border}`,
        borderRadius: radius.md,
        padding: space.md,
        boxShadow: shadow.raised,
        fontSize: fontSize.md,
        ...tabularNums,
      }}
    >
      <p style={{ margin: 0, fontWeight: 600 }}>{dateLabel}</p>
      {secondaryLabel && (
        <p style={{ margin: '2px 0 0', fontSize: fontSize.sm, color: color.inkDim }}>
          {secondaryLabel}
        </p>
      )}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'auto auto',
          columnGap: space.md,
          rowGap: '2px',
          marginTop: space.sm,
        }}
      >
        {rows.map(([label, value]) => (
          <React.Fragment key={label}>
            <span style={{ color: color.inkDim }}>{label}</span>
            <span style={{ textAlign: 'right' }}>{value}</span>
          </React.Fragment>
        ))}
        <span style={{ color: color.inkDim }}>{ko.quote.changePercent}</span>
        <span style={{ textAlign: 'right', color: changeColor }}>
          {formatPrice(Math.abs(change))} ({change >= 0 ? '+' : '-'}
          {Math.abs(parseFloat(changePercent))}%)
        </span>
        <span style={{ color: color.inkDim }}>{ko.chart.volume}</span>
        <span style={{ textAlign: 'right' }}>{formatVolume(data.volume)}</span>
      </div>
    </div>
  );
};

/**
 * Draws the candle bodies and wicks over the chart's own scales.
 *
 * Defined at module scope on purpose: a component declared inside the parent's
 * render body gets a new identity on every render, which unmounts and remounts
 * the whole layer each time the parent's state changes.
 */
interface ChartAxis {
  scale?: (value: number) => number;
  bandSize?: number;
}

interface CandlesLayerProps {
  /** Injected by recharts' `Customized`. */
  xAxisMap?: Record<string, ChartAxis>;
  yAxisMap?: Record<string, ChartAxis>;
  data?: ChartRow[];
  offset?: { left?: number; top?: number; width?: number; height?: number };
  width?: number;
  height?: number;
  upColor: string;
  downColor: string;
}

const CandlesLayer: React.FC<CandlesLayerProps> = ({
  xAxisMap,
  yAxisMap,
  data: layerData,
  offset,
  width,
  height,
  upColor,
  downColor,
}) => {
  const clipId = React.useId();

  const xAxis = Object.values(xAxisMap || {})[0];
  const yAxis = Object.values(yAxisMap || {})[0];
  if (!xAxis || !yAxis) return null;

  const xScale = xAxis.scale;
  const yScale = yAxis.scale;
  if (!xScale || !yScale) return null;

  const clipX = offset?.left ?? 0;
  const clipY = offset?.top ?? 0;
  const clipWidth = offset?.width ?? width ?? 0;
  const clipHeight = offset?.height ?? height ?? 0;

  if (!layerData || layerData.length === 0) return null;

  let candleWidth = 6;
  if (layerData.length >= 2) {
    let minDiff = Number.POSITIVE_INFINITY;
    const maxSamples = Math.min(layerData.length - 1, 40);
    for (let i = 1; i <= maxSamples; i += 1) {
      const prev = xScale(layerData[i - 1].timestamp);
      const next = xScale(layerData[i].timestamp);
      const diff = Math.abs(next - prev);
      if (Number.isFinite(diff) && diff > 0) {
        minDiff = Math.min(minDiff, diff);
      }
    }
    if (Number.isFinite(minDiff) && minDiff > 0) {
      candleWidth = Math.min(18, Math.max(2, minDiff * 0.6));
    }
  } else if (xAxis.bandSize) {
    candleWidth = Math.min(18, Math.max(2, xAxis.bandSize * 0.6));
  }

  return (
    <g clipPath={`url(#${clipId})`}>
      <defs>
        <clipPath id={clipId}>
          <rect x={clipX} y={clipY} width={clipWidth} height={clipHeight} />
        </clipPath>
      </defs>
      {layerData.map((entry, index) => {
        const x = xScale(entry.timestamp);
        if (!Number.isFinite(x)) return null;

        const openY = yScale(entry.open);
        const closeY = yScale(entry.close);
        const highY = yScale(entry.high);
        const lowY = yScale(entry.low);

        const isUp = entry.close >= entry.open;
        const strokeColor = isUp ? upColor : downColor;
        const bodyY = Math.min(openY, closeY);
        const bodyHeight = Math.max(1, Math.abs(openY - closeY));

        return (
          <g key={`candle-${index}`}>
            <line
              x1={x}
              x2={x}
              y1={highY}
              y2={lowY}
              stroke={strokeColor}
              strokeWidth={1}
            />
            <rect
              x={x - candleWidth / 2}
              y={bodyY}
              width={candleWidth}
              height={bodyHeight}
              fill={strokeColor}
              stroke={strokeColor}
              rx={1}
              ry={1}
            />
          </g>
        );
      })}
    </g>
  );
};

export const CandleChart: React.FC<CandleChartProps> = ({
  data,
  currency = 'USD',
  height = 500,
  volumeHeight = 100,
  primaryTimeZone,
  secondaryTimeZone,
  colorConvention,
}) => {
  const { colorForDirection } = useMarketColors(colorConvention);
  const upColor = colorForDirection('up');
  const downColor = colorForDirection('down');
  const flatColor = colorForDirection('flat');

  if (!data || data.length === 0) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: color.surfaceMuted,
          borderRadius: radius.lg,
          border: `1px solid ${color.border}`,
        }}
      >
        <p style={{ color: color.inkDim }}>{ko.chart.noData}</p>
      </div>
    );
  }

  // Calculate price range for Y-axis domain
  const allPrices = data.flatMap((d) => [d.high, d.low]);
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const padding = (maxPrice - minPrice) * 0.1;

  const hasTime = data.some((d) => d.date.length > 8);
  const useKst = data.some((d) => isKoreanDate(d.date));
  const timeZone = primaryTimeZone ?? (useKst ? KST_TIMEZONE : undefined);
  const secondaryZone = secondaryTimeZone ?? (useKst ? undefined : KST_TIMEZONE);
  const locale = currency === 'KRW' || useKst ? 'ko-KR' : 'en-US';

  /** Price pane keeps whatever height is left once the volume pane is placed. */
  const priceHeight = Math.max(120, height - volumeHeight);

  // Prepare data with timestamps for accurate time scaling
  const chartData = data
    .map((d) => ({
      ...d,
      timestamp: parseTimestamp(d.date),
      hasTime,
      timeZone,
      secondaryTimeZone: secondaryZone,
      locale,
    }))
    .sort((a, b) => a.timestamp - b.timestamp);

  const minTimestamp = chartData[0]?.timestamp ?? Date.now();
  const maxTimestamp = chartData[chartData.length - 1]?.timestamp ?? minTimestamp;
  const timeRange = Math.max(1, maxTimestamp - minTimestamp);
  const timePadding = Math.max(60_000, Math.round(timeRange * 0.02));
  const timeDomain: [number, number] = [
    minTimestamp - timePadding,
    maxTimestamp + timePadding,
  ];

  return (
    <div
      style={{
        width: '100%',
        backgroundColor: color.surface,
        padding: space.lg,
        borderRadius: radius.lg,
        border: `1px solid ${color.border}`,
      }}
    >
      <ResponsiveContainer width="100%" height={priceHeight}>
        <ComposedChart
          data={chartData}
          syncId="hts-candle"
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={color.borderSoft} />
          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={timeDomain}
            tick={{ fontSize: 12 }}
            minTickGap={24}
            tickFormatter={(value: number) =>
              formatDateLabel(value, hasTime, timeZone, locale)
            }
          />
          <YAxis
            yAxisId="price"
            width={72}
            domain={[minPrice - padding, maxPrice + padding]}
            tick={{ fontSize: 12 }}
            tickFormatter={(value) =>
              currency === 'KRW'
                ? `₩${value.toLocaleString('ko-KR')}`
                : `$${value.toFixed(2)}`
            }
          />
          <Tooltip
            content={
              <CustomTooltip
                currency={currency}
                upColor={upColor}
                downColor={downColor}
                flatColor={flatColor}
              />
            }
          />
          <Legend
            payload={[
              { value: ko.chart.up, type: 'square', color: upColor },
              { value: ko.chart.down, type: 'square', color: downColor },
            ]}
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            stroke="rgba(0,0,0,0)"
            strokeWidth={0}
            dot={false}
            isAnimationActive={false}
            legendType="none"
          />
          <Customized
            component={CandlesLayer}
            upColor={upColor}
            downColor={downColor}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Volume pane, sharing the price pane's cursor via syncId */}
      <ResponsiveContainer width="100%" height={volumeHeight}>
        <ComposedChart
          data={chartData}
          syncId="hts-candle"
          margin={{ top: 0, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={color.borderSoft} />
          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={timeDomain}
            tick={{ fontSize: 12 }}
            minTickGap={24}
            tickFormatter={(value: number) =>
              formatDateLabel(value, hasTime, timeZone, locale)
            }
          />
          {secondaryZone && (
            <XAxis
              xAxisId="secondary-volume"
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={timeDomain}
              tick={{ fontSize: 11, fill: color.inkDim }}
              minTickGap={24}
              orientation="bottom"
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
              tickFormatter={(value: number) =>
                formatDateLabel(value, hasTime, secondaryZone, locale)
              }
            />
          )}
          {/* Matches the price pane's axis width so the two panes stay aligned. */}
          <YAxis width={72} tick={{ fontSize: 12 }} tickFormatter={formatVolume} />
          <Tooltip
            formatter={(value: number) => [formatVolume(value), ko.chart.volume]}
            labelFormatter={(value: number) =>
              formatTooltipLabel(value, hasTime, timeZone, locale)
            }
          />

          {/* Volume bars with color based on price change */}
          <Bar dataKey="volume" name={ko.chart.volume}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.close >= entry.open ? upColor : downColor}
                opacity={0.6}
              />
            ))}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
