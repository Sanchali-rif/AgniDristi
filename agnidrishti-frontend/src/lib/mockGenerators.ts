import type { ActivityPoint, SourceSummary, ThermalFingerprint } from '../types/source'

export function seedFromString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0
  }
  return Math.abs(hash)
}

export function mulberry32(seed: number) {
  return function () {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const MONTHS = ['2025-05', '2025-07', '2025-09', '2025-11', '2026-01', '2026-03']

export function generateActivityHistory(source: SourceSummary): ActivityPoint[] {
  const rand = mulberry32(seedFromString(source.id))
  const baseline = source.status === 'persistent' ? 15 : 6
  const growth = source.status === 'persistent' ? 1.4 : 0.3

  return MONTHS.map((month, i) => ({
    month,
    detections: Math.round(baseline + growth * i + rand() * 4),
    avgTempK: Math.round(320 + source.confidence * 0.3 + rand() * 15),
  }))
}

const TEMP_BINS = [300, 310, 320, 330, 340, 350, 360]
const INDUSTRY_TEMPLATES: Record<string, number[]> = {
  'Steel Plant': [0.03, 0.08, 0.16, 0.22, 0.28, 0.14, 0.06],
  'Cement Works': [0.05, 0.14, 0.24, 0.26, 0.16, 0.09, 0.04],
  'Thermal Power Station': [0.08, 0.2, 0.28, 0.2, 0.12, 0.08, 0.04],
  'Refinery': [0.1, 0.22, 0.24, 0.18, 0.12, 0.09, 0.05],
  default: [0.06, 0.12, 0.2, 0.24, 0.18, 0.12, 0.06],
}

export function generateThermalFingerprint(source: SourceSummary): ThermalFingerprint {
  const rand = mulberry32(seedFromString(source.id + 'fp'))
  const isIndustrial = source.category === 'industrial' || source.category === 'persistent' || source.category === 'gas_flare'
  const templateKey = source.industrySubtype && INDUSTRY_TEMPLATES[source.industrySubtype] ? source.industrySubtype : 'default'
  const template = INDUSTRY_TEMPLATES[templateKey]

  const bins = TEMP_BINS.map((tempK, i) => ({
    tempK,
    normalizedFreq: Math.max(0.01, template[i] + (rand() - 0.5) * 0.03),
  }))

  return {
    bins,
    bestMatchIndustry: isIndustrial ? (source.industrySubtype ?? 'Unclassified Industrial') : 'No industrial match',
    similarityScore: isIndustrial ? Math.round(78 + rand() * 18) : Math.round(20 + rand() * 25),
  }
}
