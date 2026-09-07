export type SourceCategory =
  | 'industrial'
  | 'persistent'
  | 'new'
  | 'abnormal'
  | 'natural_biomass'
  | 'gas_flare'
  | 'unknown'

export interface SourceSummary {
  id: string
  category: SourceCategory
  industrySubtype: string | null
  confidence: number
  status: 'persistent' | 'new' | 'transient'
  anomalyLevel: 'low' | 'medium' | 'high'
  lat: number
  lon: number
}

export interface SourceDetail extends SourceSummary {
  firstDetected: string
  lastDetected: string
  district?: string
  state?: string
}

export interface KPISummary {
  thermalObjects: number
  firmsDetections: number
  matchedFirms: number
  unmatchedFirms: number
  alerts: number
  latestMonitoringStatus: string | null
}

export interface ActivityPoint {
  month: string
  detections: number
  avgTempK: number
}

export interface ThermalFingerprint {
  bins: { tempK: number; normalizedFreq: number }[]
  bestMatchIndustry: string
  similarityScore: number
}

export interface AnomalyPoint {
  date: string
  baseline: number
  current: number
}

export interface Alert {
  id: number
  alert_type: string
  firms_uid: string | null
  object_uid: string | null
  latitude: number | null
  longitude: number | null
  severity: string | null
  message: string | null
  created_at: string | null
}
