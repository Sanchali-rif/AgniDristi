import { useQuery } from '@tanstack/react-query'
import { axiosClient } from '../lib/axiosClient'
import type { KPISummary } from '../types/source'

interface DashboardSummaryResponse {
  thermal_objects: number
  firms_detections: number
  matched_firms: number
  unmatched_firms: number
  alerts: number
  latest_monitoring: {
    status: string
    run_uid: string
    trigger_type: string
  } | null
}

export function useKPISummary() {
  return useQuery({
    queryKey: ['kpi-summary'],
    queryFn: async (): Promise<KPISummary> => {
      const res = await axiosClient.get<DashboardSummaryResponse>(
        '/dashboard/summary'
      )
      const d = res.data
      return {
        thermalObjects: d.thermal_objects,
        firmsDetections: d.firms_detections,
        matchedFirms: d.matched_firms,
        unmatchedFirms: d.unmatched_firms,
        alerts: d.alerts,
        latestMonitoringStatus: d.latest_monitoring?.status ?? null,
      }
    },
  })
}
