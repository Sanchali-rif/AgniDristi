import type { GasFlareLikelihood, MonitoringRun } from './monitoring'
export type { GasFlareLikelihood, LatestRunResponse, MonitoringRun, MonitoringRunsResponse, MonitoringState } from './monitoring'

export interface DashboardSummary {
  thermal_objects: number
  temporal_source_hints?: Record<string, number> | number | null
  firms_detections: number
  matched_firms: number
  unmatched_firms: number
  alerts: number
  latest_monitoring: MonitoringRun | null
}

export interface ClassDistribution {
  count: number
  classes: Array<{ label: string; count: number }>
}

export interface ThermalObject {
  object_uid: string
  latitude: number
  longitude: number
  classification_label: string | null
  classification_source: string | null
  confidence: number | null
  detection_count: number | null
  active_months: number | null
  persistence_ratio: number | null
  source_persistence_ratio?: number | null
  temporal_source_hint?: string | null
  tci?: number | null
  seasonal_concentration?: number | null
  temp_mean: number | null
  temp_max: number | null
  object_radius_m: number | null
  industry_name?: string | null
  gem_industry_exact_type?: string | null
  gem_facility_name?: string | null
  gem_match_radius_m?: number | null
  gas_flare_candidate?: boolean | null
  gas_flare_likelihood?: GasFlareLikelihood | null
  gas_flare_score?: number | null
  gas_flare_source?: string | null
}

export interface ThermalObjectsResponse { total: number; limit: number; offset: number; objects: ThermalObject[] }

export interface RecentFirmsDetection {
  firms_uid: string
  latitude: number
  longitude: number
  frp: number | null
  bright_ti4: number | null
  bright_ti5: number | null
  acq_date: string | null
  acq_time: string | null
  satellite: string | null
  confidence: string | number | null
  daynight?: string | null
  known_source: boolean | null
  matched_object_uid: string | null
  match_distance_km: number | null
}

export interface RecentFirmsResponse { count: number; detections: RecentFirmsDetection[] }

export interface MapDateHit {
  date: string
  firms_count: number
  matched_count: number
  unmatched_count: number
}

export interface MapDatesResponse {
  count: number
  dates: MapDateHit[]
}

export type MapObjectScope = 'matched' | 'all'

export interface VnfMapDetection {
  id: number
  id_key: string | null
  latitude: number
  longitude: number
  raw_latitude: number | null
  raw_longitude: number | null
  position_source: 'OBJECT_CENTROID' | 'RAW_DETECTION'
  matched_object_uid: string | null
  temp_primary: number | null
  temp_background: number | null
  rh_primary: number | null
  area_primary: number | null
  sensor: string | null
  vnf_version: string | null
  mscan_date: string | null
  mscan_time: string | null
  processing_state: string | null
  vnf_type?: 'persistent' | 'transient' | null
  gem_industry_exact_type: string | null
  gem_facility_name: string | null
}

export type VnfPersistence = 'persistent' | 'transient' | 'both'

export interface VnfDetectionsResponse {
  filters: {
    persistence: VnfPersistence
    processing_states: string[]
  }
  total: number
  limit: number
  offset: number
  counts: {
    persistent_objects: number
    transient_detections: number
    returned_objects: number
    returned_detections: number
  }
  positioning?: {
    latitude_longitude: string
    raw_latitude_raw_longitude: string
  }
  objects: ThermalObject[]
  detections: VnfMapDetection[]
}

export interface DashboardMapResponse {
  selected_date: string | null
  filters?: {
    object_scope: MapObjectScope
    firms_limit: number
    object_limit: number
    vnf_limit: number
  }
  counts: {
    firms: number
    matched_firms: number
    unmatched_firms: number
    objects: number
    vnf_detections: number
  }
  positioning?: {
    objects: string
    firms: string
    vnf_detections: string
  }
  objects: ThermalObject[]
  firms: RecentFirmsDetection[]
  vnf_detections: VnfMapDetection[]
}
export interface DashboardAlert { id: number; alert_type: string; firms_uid: string | null; object_uid: string | null; latitude: number | null; longitude: number | null; severity: string | null; message: string | null; created_at: string | null }
export interface AlertsResponse { count: number; alerts: DashboardAlert[] }

export interface GasFlareEvidence { reasons: string[]; signal_contributions: Record<string, number>; gem_facility_name: string | null; gem_industry_exact_type: string | null }

export interface ThermalObjectDetail {
  object_uid: string
  stage3_object_id: string | null
  location: { latitude: number; longitude: number }
  classification: { label: string | null; source: string | null; confidence: number | null }
  temporal: { detection_count: number | null; active_months: number | null; persistence_ratio: number | null; source_persistence_ratio?: number | null; longest_active_run: number | null; max_inactive_gap: number | null; source_hint?: string | null; tci?: number | null; seasonal_concentration?: number | null }
  temperature: { mean: number | null; median: number | null; min: number | null; max: number | null; std: number | null; range: number | null; cv: number | null }
  area: { mean: number | null; std: number | null; cv: number | null }
  radiant_heat: { mean: number | null; std: number | null; cv: number | null }
  gas_flare_assessment?: { candidate: boolean | null; likelihood: GasFlareLikelihood | null; score: number | null; source: string | null; evidence: GasFlareEvidence | null } | null
  thermal_fingerprint: Record<string, number> | null
  object_radius_m: number | null
  recent_firms: Array<{ firms_uid: string; latitude: number; longitude: number; bright_ti4: number | null; bright_ti5: number | null; frp: number | null; acq_date: string | null; acq_time: string | null; satellite: string | null; confidence: string | number | null; match_distance_km: number | null }>
}

export interface VnfUploadResult { filename: string; status?: string; mode?: string; batch_id?: string; input_detections?: number; inserted_detections?: number; duplicates?: number; matched_existing?: number; new_candidates?: number; objects_found?: number; new_objects?: number; processing_time_seconds?: number; [key: string]: unknown }
