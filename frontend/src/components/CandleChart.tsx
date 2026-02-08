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

export interface CandleData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandleChartProps {
  data: CandleData[];
  currency?: 'USD' | 'KRW';
  height?: number;
  primaryTimeZone?: string;
  secondaryTimeZone?: string;
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
  timeZone?: string
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
  return new Intl.DateTimeFormat('en-US', options).format(
    new Date(timestamp)
  );
};

const formatTooltipLabel = (
  timestamp: number,
  withTime: boolean,
  timeZone?: string
) => {
  const options: Intl.DateTimeFormatOptions = withTime
    ? { timeZone, dateStyle: 'medium', timeStyle: 'short' }
    : { timeZone, dateStyle: 'medium' };
  return new Intl.DateTimeFormat('en-US', options).format(
    new Date(timestamp)
  );
};

// Custom tooltip
const CustomTooltip: React.FC<any> = ({ active, payload, currency = 'USD' }) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const hasTime = data.hasTime;
  const dateLabel = formatTooltipLabel(
    data.timestamp,
    hasTime,
    data.timeZone
  );
  const secondaryLabel = data.secondaryTimeZone
    ? formatTooltipLabel(data.timestamp, hasTime, data.secondaryTimeZone)
    : null;
  const isPositive = data.close >= data.open;
  const change = data.close - data.open;
  const changePercent = data.open !== 0 ? ((change / data.open) * 100).toFixed(2) : '0.00';

  const formatPrice = (value: number) => {
    if (currency === 'KRW') {
      return `₩${value.toLocaleString()}`;
    }
    return `$${value.toFixed(2)}`;
  };

  const formatVolume = (value: number) => {
    if (value >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(2)}M`;
    } else if (value >= 1_000) {
      return `${(value / 1_000).toFixed(2)}K`;
    }
    return value.toLocaleString();
  };

  return (
    <div
      style={{
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '6px',
        padding: '12px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}
    >
      <p style={{ margin: '0 0 4px 0', fontWeight: 'bold' }}>{dateLabel}</p>
      {secondaryLabel && (
        <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#6b7280' }}>
          {secondaryLabel}
        </p>
      )}
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Open: {formatPrice(data.open)}</p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>High: {formatPrice(data.high)}</p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Low: {formatPrice(data.low)}</p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Close: {formatPrice(data.close)}</p>
      <p
        style={{
          margin: '4px 0',
          fontSize: '14px',
          color: isPositive ? '#10b981' : '#ef4444',
        }}
      >
        Change: {formatPrice(Math.abs(change))} ({isPositive ? '+' : '-'}
        {Math.abs(parseFloat(changePercent))}%)
      </p>
      <p style={{ margin: '4px 0', fontSize: '14px' }}>Volume: {formatVolume(data.volume)}</p>
    </div>
  );
};

export const CandleChart: React.FC<CandleChartProps> = ({
  data,
  currency = 'USD',
  height = 500,
  primaryTimeZone,
  secondaryTimeZone,
}) => {
  if (!data || data.length === 0) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f9fafb',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
        }}
      >
        <p style={{ color: '#6b7280' }}>No chart data available</p>
      </div>
    );
  }

  // Calculate price range for Y-axis domain
  const allPrices = data.flatMap((d) => [d.high, d.low]);
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const padding = (maxPrice - minPrice) * 0.1;

  // Calculate max volume for secondary Y-axis (unused but kept for potential future use)
  // const maxVolume = Math.max(...data.map((d) => d.volume));

  const hasTime = data.some((d) => d.date.length > 8);
  const useKst = data.some((d) => isKoreanDate(d.date));
  const timeZone = primaryTimeZone ?? (useKst ? KST_TIMEZONE : undefined);
  const secondaryZone =
    secondaryTimeZone ?? (useKst ? undefined : KST_TIMEZONE);

  // Prepare data with timestamps for accurate time scaling
  const chartData = data
    .map((d) => ({
      ...d,
      timestamp: parseTimestamp(d.date),
      hasTime,
      timeZone,
      secondaryTimeZone: secondaryZone,
    }))
    .sort((a, b) => a.timestamp - b.timestamp);

  const minTimestamp = chartData[0]?.timestamp ?? Date.now();
  const maxTimestamp = chartData[chartData.length - 1]?.timestamp ?? minTimestamp;
  const timeRange = Math.max(1, maxTimestamp - minTimestamp);
  const timePadding = Math.max(60_000, Math.round(timeRange * 0.02));

  const formatVolume = (value: number) => {
    if (value >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(1)}M`;
    } else if (value >= 1_000) {
      return `${(value / 1_000).toFixed(1)}K`;
    }
    return value.toString();
  };

  const CandlesLayer: React.FC<any> = ({
    xAxisMap,
    yAxisMap,
    data: layerData,
    offset,
    width,
    height,
  }) => {
    const xAxis = Object.values(xAxisMap || {})[0] as any;
    const yAxis = Object.values(yAxisMap || {})[0] as any;
    if (!xAxis || !yAxis) return null;

    const xScale = xAxis.scale;
    const yScale = yAxis.scale;
    if (!xScale || !yScale) return null;

    const clipId = React.useId();
    const clipX = offset?.left ?? 0;
    const clipY = offset?.top ?? 0;
    const clipWidth = offset?.width ?? width ?? 0;
    const clipHeight = offset?.height ?? height ?? 0;

    let candleWidth = 6;
    if (layerData && layerData.length >= 2) {
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
            <rect
              x={clipX}
              y={clipY}
              width={clipWidth}
              height={clipHeight}
            />
          </clipPath>
        </defs>
        {layerData.map((entry: any, index: number) => {
          const x = xScale(entry.timestamp);
          if (!Number.isFinite(x)) return null;

          const openY = yScale(entry.open);
          const closeY = yScale(entry.close);
          const highY = yScale(entry.high);
          const lowY = yScale(entry.low);

          const isUp = entry.close >= entry.open;
          const color = isUp ? '#16a34a' : '#dc2626';
          const bodyY = Math.min(openY, closeY);
          const bodyHeight = Math.max(1, Math.abs(openY - closeY));

          return (
            <g key={`candle-${index}`}>
              <line
                x1={x}
                x2={x}
                y1={highY}
                y2={lowY}
                stroke={color}
                strokeWidth={1}
              />
              <rect
                x={x - candleWidth / 2}
                y={bodyY}
                width={candleWidth}
                height={bodyHeight}
                fill={color}
                stroke={color}
                rx={1}
                ry={1}
              />
            </g>
          );
        })}
      </g>
    );
  };

  return (
    <div style={{ width: '100%', backgroundColor: 'white', padding: '16px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
      <ResponsiveContainer width="100%" height={height - 100}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={[minTimestamp - timePadding, maxTimestamp + timePadding]}
            tick={{ fontSize: 12 }}
            minTickGap={24}
            tickFormatter={(value: number) =>
              formatDateLabel(value, hasTime, timeZone)
            }
          />
          <YAxis
            yAxisId="price"
            domain={[minPrice - padding, maxPrice + padding]}
            tick={{ fontSize: 12 }}
            tickFormatter={(value) =>
              currency === 'KRW'
                ? `₩${value.toLocaleString()}`
                : `$${value.toFixed(2)}`
            }
          />
          <Tooltip content={<CustomTooltip currency={currency} />} />
          <Legend
            payload={[
              { value: 'Up', type: 'square', color: '#16a34a' },
              { value: 'Down', type: 'square', color: '#dc2626' },
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
          <Customized component={CandlesLayer} />
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Volume chart below */}
      <ResponsiveContainer width="100%" height={100}>
        <ComposedChart
          data={chartData}
          margin={{ top: 0, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={[minTimestamp - timePadding, maxTimestamp + timePadding]}
            tick={{ fontSize: 12 }}
            minTickGap={24}
            tickFormatter={(value: number) =>
              formatDateLabel(value, hasTime, timeZone)
            }
          />
          {secondaryZone && (
            <XAxis
              xAxisId="secondary-volume"
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={[minTimestamp - timePadding, maxTimestamp + timePadding]}
              tick={{ fontSize: 11, fill: '#6b7280' }}
              minTickGap={24}
              orientation="bottom"
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
              tickFormatter={(value: number) =>
                formatDateLabel(value, hasTime, secondaryZone)
              }
            />
          )}
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={formatVolume}
          />
          <Tooltip
            formatter={(value: number) => [formatVolume(value), 'Volume']}
          />
          
          {/* Volume bars with color based on price change */}
          <Bar dataKey="volume" name="Volume">
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.close >= entry.open ? '#10b981' : '#ef4444'}
                opacity={0.6}
              />
            ))}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
