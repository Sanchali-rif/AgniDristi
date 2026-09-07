import { useQuery } from '@tanstack/react-query'
import { axiosClient } from '../lib/axiosClient'
import type { Alert } from '../types/source'

interface AlertsResponse {
  count: number
  alerts: Alert[]
}

export function useAlerts(alertType?: string) {
  return useQuery({
    queryKey: ['alerts', alertType],
    queryFn: async (): Promise<Alert[]> => {
      const params: Record<string, string | number> = { limit: 100 }
      if (alertType) params.alert_type = alertType
      const res = await axiosClient.get<AlertsResponse>(
        '/dashboard/alerts',
        { params }
      )
      return res.data.alerts ?? []
    },
    refetchInterval: 30_000,
  })
}
