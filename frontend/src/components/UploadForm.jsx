/**
 * UploadForm Component
 * Handles file uploads for resume and job description.
 * Supports drag-and-drop and text paste for JD.
 */

import { useState, useRef, useCallback } from 'react'
import { truncateFilename } from '../utils/helpers'
import styles from './UploadForm.module.css'

function FileDropZone({ label, accept, file, onFile, icon, hint }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.type === 'application/pdf') {
      onFile(dropped)
    }
  }, [onFile])

  const handleDragOver = (e) => { e.preventDefault(); setDragging(true) }
  const handleDragLeave = () => setDragging(false)

  return (
    <div
      className={`${styles.dropZone} ${dragging ? styles.dragging : ''} ${file ? styles.hasFile : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={(e) => onFile(e.target.files[0])}
      />

      {file ? (
        <div className={styles.fileInfo}>
          <span className={styles.fileIcon}>📄</span>
          <div>
            <p className={styles.fileName}>{truncateFilename(file.name)}</p>
            <p className={styles.fileSize}>{(file.size / 1024).toFixed(1)} KB</p>
          </div>
          <button
            className={styles.removeBtn}
            onClick={(e) => { e.stopPropagation(); onFile(null) }}
            title="Remove file"
          >
            ✕
          </button>
        </div>
      ) : (
        <div className={styles.dropPrompt}>
          <span className={styles.dropIcon}>{icon}</span>
          <p className={styles.dropLabel}>{label}</p>
          <p className={styles.dropHint}>{hint}</p>
        </div>
      )}
    </div>
  )
}

export default function UploadForm({ onSubmit, isLoading }) {
  const [resumeFile, setResumeFile]   = useState(null)
  const [jdFile, setJdFile]           = useState(null)
  const [jdText, setJdText]           = useState('')
  const [jdMode, setJdMode]           = useState('file') // 'file' | 'text'
  const [useAws, setUseAws]           = useState(false)

  const canSubmit = resumeFile && (jdFile || jdText.trim().length > 50)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!canSubmit || isLoading) return
    onSubmit({ resumeFile, jdFile: jdMode === 'file' ? jdFile : null, jdText: jdMode === 'text' ? jdText : '', useAws })
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>

      {/* ── Resume Upload ──────────────────────────────── */}
      <div className={styles.section}>
        <label className={styles.sectionLabel}>
          <span className={styles.labelNum}>01</span>
          Upload Your Resume
        </label>
        <FileDropZone
          label="Drop resume PDF here"
          accept="application/pdf"
          file={resumeFile}
          onFile={setResumeFile}
          icon="📋"
          hint="PDF only · Drag & drop or click to browse"
        />
      </div>

      {/* ── Job Description ────────────────────────────── */}
      <div className={styles.section}>
        <label className={styles.sectionLabel}>
          <span className={styles.labelNum}>02</span>
          Job Description
        </label>

        {/* Mode Toggle */}
        <div className={styles.modeToggle}>
          <button
            type="button"
            className={`${styles.modeBtn} ${jdMode === 'file' ? styles.modeBtnActive : ''}`}
            onClick={() => setJdMode('file')}
          >
            📎 Upload PDF
          </button>
          <button
            type="button"
            className={`${styles.modeBtn} ${jdMode === 'text' ? styles.modeBtnActive : ''}`}
            onClick={() => setJdMode('text')}
          >
            ✏️ Paste Text
          </button>
        </div>

        {jdMode === 'file' ? (
          <FileDropZone
            label="Drop job description PDF here"
            accept="application/pdf"
            file={jdFile}
            onFile={setJdFile}
            icon="📝"
            hint="PDF only · Drag & drop or click to browse"
          />
        ) : (
          <textarea
            className={styles.textArea}
            placeholder="Paste the full job description here... (minimum 50 characters)"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            rows={8}
          />
        )}
      </div>

      {/* ── AWS Mode Toggle ────────────────────────────── */}
      <div className={styles.awsToggle}>
        <label className={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={useAws}
            onChange={(e) => setUseAws(e.target.checked)}
            className={styles.checkbox}
          />
          <span className={styles.toggleText}>
            <strong>Use AWS</strong>
            <span className={styles.toggleHint}>Enable S3 upload + Comprehend NLP (requires configured credentials)</span>
          </span>
        </label>
        {!useAws && (
          <p className={styles.localMode}>⚡ Running in local mode — uses keyword matching (no AWS required)</p>
        )}
      </div>

      {/* ── Submit ─────────────────────────────────────── */}
      <button
        type="submit"
        className={`${styles.submitBtn} ${!canSubmit ? styles.submitDisabled : ''}`}
        disabled={!canSubmit || isLoading}
      >
        {isLoading ? (
          <span className={styles.loadingInner}>
            <span className={styles.spinner} />
            Analyzing...
          </span>
        ) : (
          '⚡ Analyze Job Readiness'
        )}
      </button>

      {!canSubmit && (resumeFile || jdFile || jdText) && (
        <p className={styles.validationHint}>
          {!resumeFile ? '↑ Please upload your resume PDF' : '↑ Please provide a job description (PDF or text)'}
        </p>
      )}
    </form>
  )
}
