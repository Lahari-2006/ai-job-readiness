/**
 * ResultsPage Component
 * Assembles the complete results dashboard from all analysis sub-components.
 */

import DecisionBanner from './DecisionBanner'
import SkillMatrix from './SkillMatrix'
import MatchChart from './MatchChart'
import SuggestionRoadmap from './SuggestionRoadmap'
import styles from './ResultsPage.module.css'

export default function ResultsPage({ result, onReset }) {
  return (
    <div className={styles.page}>

      {/* ── Header Bar ──────────────────────────────── */}
      <div className={styles.topBar}>
        <div className={styles.meta}>
          <span className={styles.metaItem}>
            📋 <span>{result.resume_filename}</span>
          </span>
          <span className={styles.metaDivider}>vs</span>
          <span className={styles.metaItem}>
            📝 <span>{result.job_description_source}</span>
          </span>
        </div>
        <button className={styles.resetBtn} onClick={onReset}>
          ← New Analysis
        </button>
      </div>

      {/* ── Decision Banner ──────────────────────────── */}
      <DecisionBanner
        decision={result.decision}
        confidence={result.confidence}
      />

      {/* ── Two-column grid ──────────────────────────── */}
      <div className={styles.grid}>
        <div className={styles.colMain}>
          <SkillMatrix result={result} />
          <SuggestionRoadmap
            suggestions={result.suggestions}
            missingSkills={result.missing_skills}
          />
        </div>
        <div className={styles.colSide}>
          <MatchChart matchBreakdown={result.match_breakdown} />
          <StatsCard result={result} />
        </div>
      </div>

      {/* ── Raw JSON (dev) ───────────────────────────── */}
      <details className={styles.rawJson}>
        <summary className={styles.rawJsonToggle}>🔧 View Raw JSON Response</summary>
        <pre className={styles.rawJsonContent}>{JSON.stringify(result, null, 2)}</pre>
      </details>

    </div>
  )
}

function StatsCard({ result }) {
  const total = result.resume_skills.length
  const matched = result.matched_skills.length
  const missing = result.missing_skills.length
  const jobTotal = result.job_skills.length

  return (
    <div className={styles.statsCard}>
      <h3 className={styles.statsTitle}>📊 Summary Stats</h3>
      <div className={styles.statsList}>
        <Stat label="Your Skills Found"    value={total}    unit="skills" />
        <Stat label="Job Requirements"     value={jobTotal} unit="skills" />
        <Stat label="Matched"              value={matched}  unit="skills" color="var(--green)" />
        <Stat label="Gap to Close"         value={missing}  unit="skills" color="var(--red)" />
        <Stat label="Overall Match"        value={`${result.confidence}%`} color={
          result.confidence >= 80 ? 'var(--green)'
          : result.confidence >= 50 ? 'var(--yellow)'
          : 'var(--red)'
        } />
      </div>
    </div>
  )
}

function Stat({ label, value, unit, color }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statLabel}>{label}</span>
      <span className={styles.statValue} style={color ? { color } : {}}>
        {value}{unit ? <span className={styles.statUnit}> {unit}</span> : ''}
      </span>
    </div>
  )
}
