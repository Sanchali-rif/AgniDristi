import type { AnomalyPoint, SourceSummary } from '../types/source'
import { mulberry32, seedFromString } from './mockGenerators'

export interface NearbyFacility {
  name: string
  type: string
  industry: string
  distanceKm: number
  direction: string
  nearbyInfrastructure: string
}

const DIRECTIONS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
const INFRASTRUCTURE = ['Rail siding', 'High-voltage substation', 'National highway', 'Port access road', 'None identified', 'Water pipeline']
const FACILITY_NAME_PREFIXES = ['East Ridge', 'Dhanbad', 'Kandra', 'North Basin', 'Riverside', 'Ganga Belt', 'Hill View', 'Central', 'Sundarban', 'Bardhaman']
const FACILITY_TYPES: { type: string; industry: string }[] = [
  { type: 'Industrial plant', industry: 'Steel manufacturing' },
  { type: 'Power station', industry: 'Thermal power' },
  { type: 'Storage terminal', industry: 'Petroleum storage' },
  { type: 'Industrial plant', industry: 'Brick production' },
  { type: 'Processing unit', industry: 'Cement manufacturing' },
  { type: 'Refinery', industry: 'Oil & gas' },
  { type: 'Foundry', industry: 'Metal casting' },
  { type: 'Mill', industry: 'Paper & pulp' },
]

export function generateNearbyFacilities(source: SourceSummary, count = 4): NearbyFacility[] {
  const rand = mulberry32(seedFromString(source.id + 'facilities'))
  const facilities: NearbyFacility[] = []
  const usedNames = new Set<string>()

  for (let i = 0; i < count; i++) {
    let prefix = FACILITY_NAME_PREFIXES[Math.floor(rand() * FACILITY_NAME_PREFIXES.length)]
    while (usedNames.has(prefix)) {
      prefix = FACILITY_NAME_PREFIXES[Math.floor(rand() * FACILITY_NAME_PREFIXES.length)]
    }
    usedNames.add(prefix)

    const typeInfo = FACILITY_TYPES[Math.floor(rand() * FACILITY_TYPES.length)]
    const distanceKm = Math.round((1.5 + rand() * 13) * 10) / 10
    const direction = DIRECTIONS[Math.floor(rand() * DIRECTIONS.length)]
    const nearbyInfrastructure = INFRASTRUCTURE[Math.floor(rand() * INFRASTRUCTURE.length)]
    const suffix = typeInfo.type === 'Storage terminal' ? 'Depot'
      : typeInfo.type === 'Power station' ? 'Thermal Station'
      : typeInfo.type === 'Refinery' ? 'Refinery'
      : typeInfo.type === 'Mill' ? 'Mill'
      : typeInfo.type === 'Foundry' ? 'Foundry'
      : 'Works'

    facilities.push({
      name: `${prefix} ${suffix}`,
      type: typeInfo.type,
      industry: typeInfo.industry,
      distanceKm,
      direction,
      nearbyInfrastructure,
    })
  }

  return facilities.sort((a, b) => a.distanceKm - b.distanceKm)
}

const ANOMALY_DATES = ['2025-04-15', '2025-06-15', '2025-08-15', '2025-10-15', '2025-12-15', '2026-03-05']

export function generateAnomalyTrend(source: SourceSummary): AnomalyPoint[] {
  const rand = mulberry32(seedFromString(source.id + 'anomaly'))
  const isHigh = source.anomalyLevel === 'high'
  const isMedium = source.anomalyLevel === 'medium'

  let baseline = 8
  let current = 8

  return ANOMALY_DATES.map((date) => {
    baseline += rand() * 2
    const drift = isHigh ? 2.2 : isMedium ? 1.1 : 0.4
    current += drift + (rand() - 0.4) * 1.5
    return {
      date,
      baseline: Math.round(baseline * 10) / 10,
      current: Math.round(current * 10) / 10,
    }
  })
}
