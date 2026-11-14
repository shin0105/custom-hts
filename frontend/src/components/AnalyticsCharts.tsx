/**
 * Small chart building blocks for the basis and bond yield views.
 *
 * Two measures on different scales are drawn as two stacked charts that
 * share an x-axis, never as one chart with two y-axes.
 */

import React from 'react';
import {
  Bar,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { chartTheme, isoDate, shortDate } from './chartTheme';

type TooltipEntry = {
  name?: string;
  value?: number | null;
  color?: string;
  dataKey?: string | number;
};

type ChartTooltipProps = {
  active?: boolean;
  label?: string;
  payload?: TooltipEntry[];
  format: (value: number) => string;
  colorFor?: (entry: TooltipEntry) => string | undefined;
};

const ChartTooltip: React.FC<ChartTooltipProps> = ({
  active,
  label,
  payload,
  format,
  colorFor,
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        backgroundColor: chartTheme.surface,
        border: `1px solid ${chartTheme.grid}`,
        borderRadius: '6px',
        padding: '8px 10px',
        fontSize: '12px',
        color: chartTheme.ink,
        boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
      }}
    >
      <div style={{ color: chartTheme.inkMuted, marginBottom: '4px' }}>
        {label ? isoDate(label) : ''}
      </div>
      {payload
        .filter((entry) => entry.value !== null && entry.value !== undefined)
        .map((entry) => (
          <div
            key={String(entry.dataKey)}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '2px',
                backgroundColor: colorFor?.(entry) ?? entry.color,
              }}
            />
            <span style={{ color: chartTheme.inkSecondary }}>{entry.name}</span>
            <strong style={{ marginLeft: 'auto', paddingLeft: '12px' }}>
              {format(entry.value as number)}
            </strong>
          </div>
        ))}
    </div>
  );
};

const legendText = (value: string) => (
  <span style={{ color: chartTheme.inkSecondary, fontSize: '12px' }}>{value}</span>
);

const axisTick = { fontSize: 12, fill: chartTheme.inkMuted };

export type TwoLinePoint = {
  date: string;
  first?: number | null;
  second?: number | null;
};

type TwoLineChartProps = {
  data: TwoLinePoint[];
  firstName: string;
  secondName: string;
  format: (value: number) => string;
  axisFormat?: (value: number) => string;
  height?: number;
  /** Mark each first-series observation, for series with gaps. */
  firstDots?: boolean;
};

/** Two series that share a unit, on one y-axis. */
export const TwoLineChart: React.FC<TwoLineChartProps> = ({
  data,
  firstName,
  secondName,
  format,
  axisFormat,
  height = 260,
  firstDots = false,
}) => (
  <ResponsiveContainer width="100%" height={height}>
    <ComposedChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
      <CartesianGrid stroke={chartTheme.grid} vertical={false} />
      <XAxis
        dataKey="date"
        tick={axisTick}
        tickLine={false}
        axisLine={{ stroke: chartTheme.grid }}
        minTickGap={32}
        tickFormatter={shortDate}
      />
      <YAxis
        domain={['auto', 'auto']}
        tick={axisTick}
        tickLine={false}
        axisLine={false}
        width={72}
        tickFormatter={axisFormat ?? format}
      />
      <Tooltip
        content={<ChartTooltip format={format} />}
        cursor={{ stroke: chartTheme.zeroLine, strokeWidth: 1 }}
      />
      <Legend
        verticalAlign="top"
        align="right"
        height={28}
        formatter={legendText}
        payload={[
          { value: firstName, type: 'line', color: chartTheme.series1 },
          { value: secondName, type: 'line', color: chartTheme.series2 },
        ]}
      />
      {/* Drawn second-then-first so the first series sits on top. */}
      <Line
        dataKey="second"
        name={secondName}
        stroke={chartTheme.series2}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        dot={false}
        activeDot={{ r: 4, stroke: chartTheme.surface, strokeWidth: 2 }}
        connectNulls
        isAnimationActive={false}
      />
      <Line
        dataKey="first"
        name={firstName}
        stroke={chartTheme.series1}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        dot={
          firstDots
            ? { r: 4, fill: chartTheme.series1, stroke: chartTheme.surface, strokeWidth: 2 }
            : false
        }
        activeDot={{ r: 4, stroke: chartTheme.surface, strokeWidth: 2 }}
        connectNulls
        isAnimationActive={false}
      />
    </ComposedChart>
  </ResponsiveContainer>
);

export type SignedBarPoint = { date: string; value?: number | null };

type SignedBarChartProps = {
  data: SignedBarPoint[];
  name: string;
  positiveLabel: string;
  negativeLabel: string;
  positiveColor: string;
  negativeColor: string;
  format: (value: number) => string;
  height?: number;
};

/** One measure around zero; the bar colour says which side it is on. */
export const SignedBarChart: React.FC<SignedBarChartProps> = ({
  data,
  name,
  positiveLabel,
  negativeLabel,
  positiveColor,
  negativeColor,
  format,
  height = 160,
}) => {
  const colorOf = (value?: number | null) =>
    (value ?? 0) >= 0 ? positiveColor : negativeColor;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid stroke={chartTheme.grid} vertical={false} />
        <XAxis
          dataKey="date"
          tick={axisTick}
          tickLine={false}
          axisLine={{ stroke: chartTheme.grid }}
          minTickGap={32}
          tickFormatter={shortDate}
        />
        <YAxis
          tick={axisTick}
          tickLine={false}
          axisLine={false}
          width={72}
          tickFormatter={format}
        />
        <Tooltip
          content={
            <ChartTooltip format={format} colorFor={(entry) => colorOf(entry.value)} />
          }
          cursor={{ fill: 'rgba(107,114,128,0.08)' }}
        />
        <Legend
          verticalAlign="top"
          align="right"
          height={28}
          formatter={legendText}
          payload={[
            { value: positiveLabel, type: 'square', color: positiveColor },
            { value: negativeLabel, type: 'square', color: negativeColor },
          ]}
        />
        <ReferenceLine y={0} stroke={chartTheme.zeroLine} />
        <Bar dataKey="value" name={name} radius={2} isAnimationActive={false}>
          {data.map((point) => (
            <Cell key={point.date} fill={colorOf(point.value)} />
          ))}
        </Bar>
      </ComposedChart>
    </ResponsiveContainer>
  );
};
