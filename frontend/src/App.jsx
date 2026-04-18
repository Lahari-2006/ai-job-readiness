/**
 * App.jsx — Root Component
 * Orchestrates the full UI state machine:
 *   idle → loading → results | error
 */

import { useAnalysis, STATES } from './hooks/useAnalysis'
import UploadForm from './components/UploadForm'
import LoadingState from './components/LoadingState'
import ResultsPage from './components/ResultsPage'
import styles from './App.module.css'

export default function App() {
  const { status, result, error, uploadProgress, analyze, reset } = useAnalysis()

  const isLoading = status === STATES.UPLOADING || status === STATES.ANALYZING

  return (
    <div className={styles.app}>
      {/* ── Header ──────────────────────────────────── */}
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.logo}>
            <span className={styles.logoIcon}>⚡</span>
            <div>
              <span className={styles.logoText}>JobReadiness</span>
              <span className={styles.logoSub}>.ai</span>
            </div>
          </div>
          <nav className={styles.nav}>
            <span className={styles.navBadge}>Beta</span>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.navLink}
            >
              API Docs
            </a>
          </nav>
        </div>
      </header>

      {/* ── Main ────────────────────────────────────── */}
      <main className={styles.main}>
        <div className={styles.container}>

          {/* Hero — only shown on idle/error */}
          {(status === STATES.IDLE || status === STATES.ERROR) && (
            <div className={styles.hero}>
              <div className={styles.heroEyebrow}>
                <span className={styles.eyebrowDot} />
                AI-Powered Career Intelligence
              </div>
              <h1 className={styles.heroTitle}>
                Know Before You Apply.
              </h1>
              <p className={styles.heroSub}>
                Upload your resume and a job description. Get an instant skill gap analysis,
                readiness decision, and a personalized learning roadmap — powered by
                AWS Comprehend NLP.
              </p>

              {/* Feature pills */}
              <div className={styles.pills}>
                {[
                  '🧠 NLP Skill Extraction',
                  '⚖️ Gap Analysis',
                  '⚡ Instant Decision',
                  '🗺️ Learning Roadmap',
                  '📊 Category Breakdown',
                  '☁️ AWS Comprehend',
                ].map(pill => (
                  <span key={pill} className={styles.pill}>{pill}</span>
                ))}
              </div>
            </div>
          )}

          {/* Error banner */}
          {status === STATES.ERROR && error && (
            <div className={styles.errorBanner}>
              <span className={styles.errorIcon}>⚠</span>
              <div>
                <strong>Analysis Failed</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          {/* Upload form */}
          {(status === STATES.IDLE || status === STATES.ERROR) && (
            <div className={styles.formCard}>
              <div className={styles.formCardHeader}>
                <h2 className={styles.formCardTitle}>Start Analysis</h2>
                <span className={styles.formCardHint}>Free · No login required</span>
              </div>
              <UploadForm onSubmit={analyze} isLoading={isLoading} />
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div className={styles.loadingCard}>
              <LoadingState status={status} uploadProgress={uploadProgress} />
            </div>
          )}

          {/* Results */}
          {status === STATES.SUCCESS && result && (
            <ResultsPage result={result} onReset={reset} />
          )}

        </div>
      </main>

      {/* ── Footer ──────────────────────────────────── */}
      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <span className={styles.footerText}>
            Built with FastAPI · React · AWS Comprehend · S3
          </span>
          <span className={styles.footerText}>
            Skills are extracted using NLP and matched against a curated taxonomy of 200+ tech skills
          </span>
        </div>
      </footer>
    </div>
  )
}
