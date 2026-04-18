/**
 * LoadingState Component
 * Shows an animated step-by-step progress indicator during analysis.
 */

import { useState, useEffect } from 'react'
import { STATES } from '../hooks/useAnalysis'
import styles from './LoadingState.module.css'

const STEPS = [
  { id: 'upload',    label: 'Uploading files',              icon: '📤' },
  { id: 'extract',   label: 'Extracting PDF text',          icon: '📄' },
  { id: 'nlp',       label: 'Running NLP analysis',         icon: '🧠' },
  { id: 'skills',    label: 'Identifying skills',           icon: '🔍' },
  { id: 'compare',   label: 'Comparing skill sets',         icon: '⚖️'  },
  { id: 'decide',    label: 'Generating decision',          icon: '⚡' },
]

export default function LoadingState({ status, uploadProgress }) {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    if (status === STATES.UPLOADING) {
      setActiveStep(0)
    } else if (status === STATES.ANALYZING) {
      // Auto-progress through steps with timed intervals
      setActiveStep(1)
      const timers = []
      const delays = [400, 900, 1600, 2400, 3400]
      delays.forEach((delay, i) => {
        timers.push(setTimeout(() => setActiveStep(i + 2), delay))
      })
      return () => timers.forEach(clearTimeout)
    }
  }, [status])

  return (
    <div className={styles.container}>
      <div className={styles.pulseRing} />
      <div className={styles.inner}>

        <div className={styles.logoMark}>⚡</div>
        <h3 className={styles.heading}>Analyzing your profile...</h3>

        <div className={styles.steps}>
          {STEPS.map((step, index) => {
            const isDone    = index < activeStep
            const isActive  = index === activeStep
            const isPending = index > activeStep

            return (
              <div
                key={step.id}
                className={`${styles.step} ${isDone ? styles.done : ''} ${isActive ? styles.active : ''} ${isPending ? styles.pending : ''}`}
              >
                <div className={styles.stepIcon}>
                  {isDone
                    ? <span className={styles.checkmark}>✓</span>
                    : isActive
                    ? <span className={styles.stepSpinner} />
                    : <span className={styles.stepEmoji}>{step.icon}</span>
                  }
                </div>
                <span className={styles.stepLabel}>{step.label}</span>
                {index === 0 && isActive && (
                  <span className={styles.progress}>{uploadProgress}%</span>
                )}
              </div>
            )
          })}
        </div>

        <p className={styles.hint}>
          This may take 10–30 seconds depending on file size and AWS response times.
        </p>
      </div>
    </div>
  )
}
