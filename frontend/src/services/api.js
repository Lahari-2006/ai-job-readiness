/**
 * API Service
 * Centralizes all HTTP calls to the FastAPI backend.
 * Uses Axios with a configured base URL.
 */

import axios from 'axios'

// Base URL — in dev, Vite proxies /api → localhost:8000
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 120_000, // 2 min — PDF processing + Comprehend can be slow
})

/**
 * Analyze resume against job description.
 *
 * @param {File}    resumeFile        - PDF file for resume
 * @param {File|null} jdFile          - PDF file for job description (optional)
 * @param {string}  jdText            - Plain text job description (optional)
 * @param {boolean} useAws            - Whether to use AWS services
 * @param {Function} onUploadProgress - Progress callback (0–100)
 * @returns {Promise<AnalysisResult>}
 */
export async function analyzeResume({
  resumeFile,
  jdFile = null,
  jdText = '',
  useAws = true,
  onUploadProgress = null,
}) {
  const formData = new FormData()
  formData.append('resume', resumeFile)

  if (jdFile) {
    formData.append('job_description_file', jdFile)
  }
  if (jdText) {
    formData.append('job_description_text', jdText)
  }

  formData.append('use_aws', useAws.toString())

  const config = {
    headers: { 'Content-Type': 'multipart/form-data' },
  }

  if (onUploadProgress) {
    config.onUploadProgress = (progressEvent) => {
      const percent = Math.round(
        (progressEvent.loaded * 100) / (progressEvent.total || 1)
      )
      onUploadProgress(percent)
    }
  }

  const response = await apiClient.post('/api/v1/analyze', formData, config)
  return response.data
}

/**
 * Get decision threshold configuration from the backend.
 * Used by the UI to render the scoring scale.
 */
export async function getDecisionThresholds() {
  const response = await apiClient.get('/api/v1/decisions')
  return response.data
}

/**
 * Health check
 */
export async function checkHealth() {
  const response = await apiClient.get('/health')
  return response.data
}
