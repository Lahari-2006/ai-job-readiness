/**
 * Utility helpers for the UI layer.
 */

/** Returns CSS variable name and emoji for each decision type */
export function getDecisionStyle(decision) {
  switch (decision) {
    case 'APPLY NOW':
      return {
        color: 'var(--green)',
        dimColor: 'var(--green-dim)',
        midColor: 'var(--green-mid)',
        emoji: '🚀',
        icon: '✓',
      }
    case 'IMPROVE BEFORE APPLYING':
      return {
        color: 'var(--yellow)',
        dimColor: 'var(--yellow-dim)',
        midColor: 'var(--yellow-mid)',
        emoji: '📈',
        icon: '△',
      }
    case 'NOT SUITABLE':
      return {
        color: 'var(--red)',
        dimColor: 'var(--red-dim)',
        midColor: 'var(--red-mid)',
        emoji: '🛑',
        icon: '✗',
      }
    default:
      return {
        color: 'var(--text-secondary)',
        dimColor: 'var(--bg-elevated)',
        midColor: 'var(--border-default)',
        emoji: '?',
        icon: '?',
      }
  }
}

/** Category label map */
export const CATEGORY_LABELS = {
  languages:  'Languages',
  frameworks: 'Frameworks',
  tools:      'Tools & DevOps',
  cloud:      'Cloud',
  databases:  'Databases',
  concepts:   'Concepts',
}

/** Category emoji map */
export const CATEGORY_EMOJIS = {
  languages:  '⌨️',
  frameworks: '🧩',
  tools:      '🔧',
  cloud:      '☁️',
  databases:  '🗄️',
  concepts:   '💡',
}

/** Clamp a number between min and max */
export const clamp = (val, min, max) => Math.min(Math.max(val, min), max)

/** Truncate a filename for display */
export function truncateFilename(name, maxLen = 28) {
  if (!name || name.length <= maxLen) return name
  const ext = name.split('.').pop()
  return name.substring(0, maxLen - ext.length - 4) + '...' + ext
}

/** Format a score as a readable label */
export function scoreLabel(score) {
  if (score >= 80) return 'Excellent Match'
  if (score >= 60) return 'Good Match'
  if (score >= 40) return 'Partial Match'
  return 'Low Match'
}
