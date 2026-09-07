import { useQuery } from '@tanstack/react-query'
import { axiosClient } from '../lib/axiosClient'
import type { ActivityPoint, AnomalyPoint, ThermalFingerprint } from '../types/source'

export function useSourceHistory(sourceId?: string | null) {
  return useQuery({
    queryKey: ['source-history', sourceId],
    enabled: Boolean(sourceId),
    queryFn: async (): Promise<ActivityPoint[]> => {
      if (!sourceId) throw new Error('Source ID is required')
      try {
        const res = await axiosClient.get<ActivityPoint[]>(
          `/sources/${encodeURIComponent(sourceId)}/history`
        )
        return res.data
      } catch {
        return []
      }
    },
  })
}

export function useSourceFingerprint(sourceId?: string | null) {
  return useQuery({
    queryKey: ['source-fingerprint', sourceId],
    enabled: Boolean(sourceId),
    queryFn: async (): Promise<ThermalFingerprint | null> => {
      if (!sourceId) throw new Error('Source ID is required')
      try {
        const res = await axiosClient.get<ThermalFingerprint>(
          `/sources/${encodeURIComponent(sourceId)}/fingerprint`
        )
        return res.data
      } catch {
        return null
      }
    },
  })
}

export function useSourceAnomaly(sourceId?: string | null) {
  return useQuery({
    queryKey: ['source-anomaly', sourceId],
    enabled: Boolean(sourceId),
    queryFn: async (): Promise<AnomalyPoint[]> => {
      if (!sourceId) throw new Error('Source ID is required')
      try {
        const res = await axiosClient.get<AnomalyPoint[]>(
          `/sources/${encodeURIComponent(sourceId)}/anomaly`
        )
        return res.data
      } catch {
        return []
      }
    },
  })
}
