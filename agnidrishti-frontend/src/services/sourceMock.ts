import type { SourceSummary } from '../types/source'
import mockSources from '../lib/mockData/sources.json'

export type SourceFilters = Record<string, string | number | undefined>

export function filterMockSources(filters: SourceFilters) {
  return (mockSources as SourceSummary[]).filter((source) => {
    const sourceId = String(filters.sourceId ?? '').toLowerCase()
    const industryType = String(filters.industryType ?? '').toLowerCase()
    const confidence = String(filters.confidenceLevel ?? '')
    const confidenceMinimum = confidence ? Number(confidence) : 0

    if (sourceId && !source.id.toLowerCase().includes(sourceId)) return false
    if (filters.sourceType && source.category !== filters.sourceType) return false
    if (industryType && !(source.industrySubtype ?? '').toLowerCase().includes(industryType)) return false
    if (filters.anomalyLevel && source.anomalyLevel !== filters.anomalyLevel) return false
    if (filters.persistenceStatus && source.status !== filters.persistenceStatus) return false
    if (confidenceMinimum > 0 && source.confidence < confidenceMinimum) return false
    if (confidence === 'high' && source.confidence < 80) return false
    if (confidence === 'medium' && (source.confidence < 60 || source.confidence >= 80)) return false
    if (confidence === 'low' && source.confidence >= 60) return false
    return true
  })
}

export function findMockSource(sourceId: string): SourceSummary {
  const source = (mockSources as SourceSummary[]).find((s) => s.id === sourceId)
  if (!source) throw new Error(`Mock source not found: ${sourceId}`)
  return source
}

export const REGIONS: { district: string; state: string }[] = [
  { district: 'Ranchi', state: 'Jharkhand' },
  { district: 'Dhanbad', state: 'Jharkhand' },
  { district: 'Patna', state: 'Bihar' },
  { district: 'Gaya', state: 'Bihar' },
  { district: 'Bhagalpur', state: 'Bihar' },
  { district: 'Kolkata', state: 'West Bengal' },
  { district: 'Purulia', state: 'West Bengal' },
  { district: 'Paschim Bardhaman', state: 'West Bengal' },
]

export function seedFromString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0
  }
  return Math.abs(hash)
}

export function regionForSource(source: SourceSummary) {
  return REGIONS[seedFromString(source.id) % REGIONS.length]
}

export function firstDetectedForSource(source: SourceSummary): string {
  const seed = seedFromString(source.id + 'first')
  const daysAgo = source.status === 'persistent' ? 400 + (seed % 300) : 5 + (seed % 60)
  const date = new Date('2026-09-03T00:00:00Z')
  date.setDate(date.getDate() - daysAgo)
  return date.toISOString()
}

export const LAST_DETECTED = '2026-09-03T04:12:00Z'
