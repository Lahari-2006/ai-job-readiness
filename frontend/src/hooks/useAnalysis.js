/**
 * useAnalysis Hook
 * Manages the full lifecycle of an analysis request:
 *   idle → uploading → analyzing → success | error
 */

import { useState, useCallback } from 'react'
import { analyzeResume } from '../services/api'

export const STATES = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  ANALYZING: 'analyzing',
  SUCCESS: 'success',
  ERROR: 'error',
}

export function useAnalysis() {
  const [status, setStatus]         = useState(STATES.IDLE)
  const [result, setResult]         = useState(null)
  const [error, setError]           = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)

  const analyze = useCallback(async ({ resumeFile, jdFile, jdText, useAws }) => {
    setStatus(STATES.UPLOADING)
    setError(null)
    setResult(null)
    setUploadProgress(0)

    try {
      const data = await analyzeResume({
        resumeFile,
        jdFile,
        jdText,
        useAws,
        onUploadProgress: (pct) => {
          setUploadProgress(pct)
          if (pct === 100) setStatus(STATES.ANALYZING)
        },
      })
      setResult(data)
      setStatus(STATES.SUCCESS)
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        'An unexpected error occurred. Please try again.'
      setError(message)
      setStatus(STATES.ERROR)
    }
  }, [])

  const reset = useCallback(() => {
    setStatus(STATES.IDLE)
    setResult(null)
    setError(null)
    setUploadProgress(0)
  }, [])

  return { status, result, error, uploadProgress, analyze, reset }
}
