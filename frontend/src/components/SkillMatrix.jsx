/**
 * SkillMatrix Component
 * Displays matched skills, missing skills, and per-category breakdown.
 */

import { CATEGORY_LABELS, CATEGORY_EMOJIS } from '../utils/helpers'
import styles from './SkillMatrix.module.css'

function SkillChip({ skill, variant }) {
  return (
    <span className={`${styles.chip} ${styles[variant]}`}>
      {variant === 'matched' && <span className={styles.chipDot} />}
      {skill}
    </span>
  )
}

function CategoryBar({ category, resumeSkills, jobSkills }) {
  const jobSet = new Set(jobSkills)
  const resumeSet = new Set(resumeSkills)
  const matched = jobSkills.filter(s => resumeSet.has(s)).length
  const total = jobSkills.length

  if (total === 0) return null

  const pct = Math.round((matched / total) * 100)

  return (
    <div className={styles.catRow}>
      <div className={styles.catHeader}>
        <span className={styles.catEmoji}>{CATEGORY_EMOJIS[category]}</span>
        <span className={styles.catName}>{CATEGORY_LABELS[category]}</span>
        <span className={styles.catScore}>{matched}/{total}</span>
      </div>
      <div className={styles.catBarTrack}>
        <div
          className={styles.catBarFill}
          style={{
            width: `${pct}%`,
            '--bar-color': pct >= 80 ? 'var(--green)' : pct >= 50 ? 'var(--yellow)' : 'var(--red)',
          }}
        />
      </div>
      <span className={styles.catPct}>{pct}%</span>
    </div>
  )
}

const CATEGORIES = ['languages', 'frameworks', 'tools', 'cloud', 'databases', 'concepts']

export default function SkillMatrix({ result }) {
  const {
    matched_skills,
    missing_skills,
    resume_skill_categories,
    job_skill_categories,
  } = result

  return (
    <div className={styles.matrix}>

      {/* ── Skill Lists ──────────────────────────────── */}
      <div className={styles.skillsGrid}>

        {/* Matched */}
        <div className={styles.skillCard}>
          <div className={styles.cardHeader}>
            <span className={styles.cardIcon}>✓</span>
            <h3 className={styles.cardTitle}>Matched Skills</h3>
            <span className={`${styles.badge} ${styles.badgeGreen}`}>{matched_skills.length}</span>
          </div>
          <div className={styles.chipList}>
            {matched_skills.length > 0
              ? matched_skills.map(s => <SkillChip key={s} skill={s} variant="matched" />)
              : <p className={styles.empty}>No matched skills found</p>
            }
          </div>
        </div>

        {/* Missing */}
        <div className={styles.skillCard}>
          <div className={styles.cardHeader}>
            <span className={styles.cardIconRed}>✗</span>
            <h3 className={styles.cardTitle}>Missing Skills</h3>
            <span className={`${styles.badge} ${styles.badgeRed}`}>{missing_skills.length}</span>
          </div>
          <div className={styles.chipList}>
            {missing_skills.length > 0
              ? missing_skills.map(s => <SkillChip key={s} skill={s} variant="missing" />)
              : <p className={styles.empty}>🎉 No missing skills — you're a full match!</p>
            }
          </div>
        </div>
      </div>

      {/* ── Category Breakdown ───────────────────────── */}
      <div className={styles.breakdown}>
        <h3 className={styles.breakdownTitle}>
          <span className={styles.breakdownIcon}>📊</span>
          Category Breakdown
        </h3>
        <div className={styles.catList}>
          {CATEGORIES.map(cat => (
            <CategoryBar
              key={cat}
              category={cat}
              resumeSkills={resume_skill_categories[cat] || []}
              jobSkills={job_skill_categories[cat] || []}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
