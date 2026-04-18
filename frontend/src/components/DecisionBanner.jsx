/**
 * DecisionBanner
 * The hero component showing the final verdict with animated score.
 */

import { useEffect, useState } from 'react'
import { getDecisionStyle, scoreLabel } from '../utils/helpers'
import styles from './DecisionBanner.module.css'

function AnimatedScore({ target }) {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    let start = 0
    const duration = 1200
    const startTime = performance.now()

    const animate = (now) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCurrent(Math.round(eased * target))
      if (progress < 1) requestAnimationFrame(animate)
    }

    requestAnimationFrame(animate)
  }, [target])

  return <span>{current}</span>
}

export default function DecisionBanner({ decision, confidence }) {
  const style = getDecisionStyle(decision)
  const circumference = 2 * Math.PI * 54  // r=54

  const [strokeOffset, setStrokeOffset] = useState(circumference)

  useEffect(() => {
    const timer = setTimeout(() => {
      setStrokeOffset(circumference * (1 - confidence / 100))
    }, 200)
    return () => clearTimeout(timer)
  }, [confidence, circumference])

  return (
    <div
      className={styles.banner}
      style={{ '--decision-color': style.color, '--decision-dim': style.dimColor, '--decision-mid': style.midColor }}
    >
      {/* Ambient glow */}
      <div className={styles.glow} />

      {/* Left: Score ring */}
      <div className={styles.scoreRing}>
        <svg viewBox="0 0 120 120" className={styles.ringsvg}>
          {/* Track */}
          <circle cx="60" cy="60" r="54" className={styles.ringTrack} />
          {/* Progress */}
          <circle
            cx="60" cy="60" r="54"
            className={styles.ringProgress}
            strokeDasharray={circumference}
            strokeDashoffset={strokeOffset}
            style={{ stroke: style.color, transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)' }}
          />
        </svg>
        <div className={styles.ringLabel}>
          <span className={styles.ringScore}>
            <AnimatedScore target={confidence} />
          </span>
          <span className={styles.ringPercent}>%</span>
        </div>
      </div>

      {/* Right: Decision text */}
      <div className={styles.content}>
        <div className={styles.emoji}>{style.emoji}</div>
        <h2 className={styles.decision}>{decision}</h2>
        <p className={styles.scoreLabel}>{scoreLabel(confidence)} · {confidence}% match</p>
        <p className={styles.description}>
          {getDecisionDescription(decision)}
        </p>
      </div>
    </div>
  )
}

function getDecisionDescription(decision) {
  switch (decision) {
    case 'APPLY NOW':
      return 'Your skills strongly align with this role. You are well-positioned to compete for this position.'
    case 'IMPROVE BEFORE APPLYING':
      return 'You have a solid foundation, but closing a few skill gaps will significantly boost your chances.'
    case 'NOT SUITABLE':
      return 'There are significant skill gaps to address. Use the roadmap below to build the required skills first.'
    default:
      return ''
  }
}
