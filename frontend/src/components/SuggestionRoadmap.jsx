/**
 * SuggestionRoadmap Component
 * Renders actionable suggestions as a visual numbered roadmap.
 */

import styles from './SuggestionRoadmap.module.css'

export default function SuggestionRoadmap({ suggestions, missingSkills }) {
  if (!suggestions || suggestions.length === 0) {
    return (
      <div className={styles.empty}>
        <span className={styles.emptyIcon}>🏆</span>
        <p>You have all the required skills! No learning roadmap needed.</p>
      </div>
    )
  }

  return (
    <div className={styles.roadmap}>
      <div className={styles.header}>
        <span className={styles.headerIcon}>🗺️</span>
        <div>
          <h3 className={styles.title}>Learning Roadmap</h3>
          <p className={styles.subtitle}>
            {suggestions.length} action{suggestions.length > 1 ? 's' : ''} to close your skill gaps
          </p>
        </div>
      </div>

      <div className={styles.steps}>
        {suggestions.map((suggestion, index) => (
          <div key={index} className={styles.step} style={{ animationDelay: `${index * 0.07}s` }}>
            <div className={styles.stepLeft}>
              <div className={styles.stepNum}>{String(index + 1).padStart(2, '0')}</div>
              {index < suggestions.length - 1 && <div className={styles.stepLine} />}
            </div>
            <div className={styles.stepContent}>
              <span className={styles.skillTag}>
                {missingSkills[index] || 'Skill'}
              </span>
              <p className={styles.stepText}>{suggestion}</p>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.footer}>
        <span className={styles.footerIcon}>💡</span>
        <p className={styles.footerText}>
          Focus on the top 2–3 skills that appear most frequently in job descriptions in your target role.
          Building projects around these skills has the highest ROI for job applications.
        </p>
      </div>
    </div>
  )
}
