import { useQuery } from '@tanstack/react-query'
import { axiosClient } from '../lib/axiosClient'
import type { SourceDetail, SourceSummary } from '../types/source'

interface BackendObject {
  object_uid: string
  latitude: number
  longitude: number
  classification_label: string | null
  classification_source: string | null
  confidence: number | null
  detection_count: number | null
  persistence_ratio: number | null
  temp_mean: number | null
}

interface ObjectsResponse {
  total: number
  objects: BackendObject[]
}

function mapToSource(obj: BackendObject): SourceSummary {
  const conf = Math.round((obj.confidence ?? 0.5) * 100)
  const label = obj.classification_label?.toLowerCase() ?? 'unknown'
  const category = label.includes('industrial') ? 'industrial'
    : label.includes('biomass') ? 'natural_biomass'
    : (obj.persistence_ratio ?? 0) > 0.6 ? 'persistent'
    : 'unknown'

  return {
    id: obj.object_uid,
    category,
    industrySubtype: obj.classification_label ?? null,
    confidence: conf,
    status: (obj.persistence_ratio ?? 0) > 0.6 ? 'persistent' : 'new',
    anomalyLevel: conf < 50 ? 'high' : conf < 75 ? 'medium' : 'low',
    lat: obj.latitude,
    lon: obj.longitude,
  }
}

export type SourceFilters = Record<string, string | number | undefined>

export function useSources(filters: SourceFilters = {}) {
  return useQuery({
    queryKey: ['sources', filters],
    queryFn: async (): Promise<SourceSummary[]> => {
      const params: Record<string, string> = {}
      if (filters.classification) params.classification = String(filters.classification)
      const res = await axiosClient.get<ObjectsResponse>(
        '/dashboard/objects',
        { params }
      )
      return (res.data.objects ?? []).map(mapToSource)
    },
  })
}

export function useSourceDetail(sourceId?: string | null) {
  return useQuery({
    queryKey: ['source-detail', sourceId],
    enabled: Boolean(sourceId),
    queryFn: async (): Promise<SourceDetail> => {
      if (!sourceId) throw new Error('Source ID is required')
      const res = await axiosClient.get<Record<string, unknown>>(
        `/dashboard/objects/${encodeURIComponent(sourceId)}`
      )
      const d = res.data
      const loc = d.location as { latitude: number; longitude: number } | undefined
      const cls = d.classification as { label?: string; confidence?: number } | undefined
      const conf = Math.round((cls?.confidence ?? 0.5) * 100)

      return {
        id: String(d.object_uid),
        category: 'industrial',
        industrySubtype: cls?.label ?? null,
        confidence: conf,
        status: 'persistent',
        anomalyLevel: conf < 50 ? 'high' : conf < 75 ? 'medium' : 'low',
        lat: loc?.latitude ?? 0,
        lon: loc?.longitude ?? 0,
        firstDetected: '',
        lastDetected: '',
      }
    },
  })
}
