/**
 * MatchChart Component
 * Renders a radar chart showing per-category match scores using Recharts.
 */

import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Cell,
} from 'recharts'
import { CATEGORY_LABELS } from '../utils/helpers'
import styles from './MatchChart.module.css'
import { useState } from 'react'

const COLORS = {
  green:  '#00e5a0',
  yellow: '#f5c518',
  red:    '#ff4d6d',
  accent: '#4f8ef7',
}

function getBarColor(value) {
  if (value >= 80) return COLORS.green
  if (value >= 50) return COLORS.yellow
  return COLORS.red
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    const val = payload[0].value
    return (
      <div className={styles.tooltip}>
        <span className={styles.tooltipLabel}>{payload[0].payload.category}</span>
        <span className={styles.tooltipValue} style={{ color: getBarColor(val) }}>{val}%</span>
      </div>
    )
  }
  return null
}

export default function MatchChart({ matchBreakdown }) {
  const [chartType, setChartType] = useState('bar')

  const data = Object.entries(matchBreakdown)
    .filter(([, val]) => val > 0 || true) // include all categories
    .map(([key, value]) => ({
      category: CATEGORY_LABELS[key] || key,
      value: Math.round(value),
      fullMark: 100,
    }))

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <span className={styles.icon}>📡</span>
          <h3 className={styles.title}>Match Breakdown by Category</h3>
        </div>
        <div className={styles.toggle}>
          <button
            className={`${styles.toggleBtn} ${chartType === 'bar' ? styles.toggleActive : ''}`}
            onClick={() => setChartType('bar')}
          >Bar</button>
          <button
            className={`${styles.toggleBtn} ${chartType === 'radar' ? styles.toggleActive : ''}`}
            onClick={() => setChartType('radar')}
          >Radar</button>
        </div>
      </div>

      <div className={styles.chart}>
        <ResponsiveContainer width="100%" height={280}>
          {chartType === 'bar' ? (
            <BarChart data={data} margin={{ top: 10, right: 16, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
              <XAxis
                dataKey="category"
                tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'DM Mono' }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'DM Mono' }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--bg-hover)' }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={48}>
                {data.map((entry, index) => (
                  <Cell key={index} fill={getBarColor(entry.value)} />
                ))}
              </Bar>
            </BarChart>
          ) : (
            <RadarChart data={data}>
              <PolarGrid stroke="var(--border-default)" />
              <PolarAngleAxis
                dataKey="category"
                tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'DM Mono' }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
                axisLine={false}
              />
              <Radar
                name="Match"
                dataKey="value"
                stroke={COLORS.accent}
                fill={COLORS.accent}
                fillOpacity={0.25}
                strokeWidth={2}
              />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className={styles.legend}>
        {[
          { color: COLORS.green,  label: '≥ 80% Strong' },
          { color: COLORS.yellow, label: '50–79% Moderate' },
          { color: COLORS.red,    label: '< 50% Weak' },
        ].map(({ color, label }) => (
          <div key={label} className={styles.legendItem}>
            <span className={styles.legendDot} style={{ background: color }} />
            <span className={styles.legendLabel}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
