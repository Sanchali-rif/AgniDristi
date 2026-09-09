import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { apiGet } from '../lib/apiClient'
import type { Alert } from '../types/source'

export interface AlertsResponse {
  count: number
  alerts: Alert[]
}

export interface AlertTypeCount {
  alertType: string
  count: number
}

export const ALERT_TYPE_COUNTS: AlertTypeCount[] = [
  { alertType: 'UNMATCHED_ANOMALY', count: 501 },
  { alertType: 'REPEATED_UNMATCHED', count: 0 },
  { alertType: 'ABNORMAL_KNOWN_SOURCE', count: 0 },
]

interface AlertQuery {
  alertTypes?: string[]
  limit?: number
  offset?: number
}

const normalizeType = (value: string) => value.trim().toUpperCase()

export function getAlertTotal(alertTypes: string[] = []) {
  const normalizedTypes = alertTypes.map(normalizeType).filter(Boolean)
  const relevantTypes = normalizedTypes.length === 0 ? ALERT_TYPE_COUNTS : ALERT_TYPE_COUNTS.filter((item) => normalizedTypes.includes(item.alertType))
  return relevantTypes.reduce((sum, item) => sum + item.count, 0)
}

export function useAlerts({ alertTypes = [], limit = 50, offset = 0 }: AlertQuery = {}) {
  const normalizedTypes = alertTypes.map(normalizeType).filter(Boolean)
  const alertType = normalizedTypes.length > 0 ? normalizedTypes.join(',') : undefined

  return useQuery({
    queryKey: ['dashboard', 'alerts', { alertType, limit, offset }],
    queryFn: ({ signal }) => apiGet<AlertsResponse>('/dashboard/alerts', { params: { limit, offset, alert_type: alertType }, signal }),
    placeholderData: keepPreviousData,
    refetchInterval: 30_000,
  })
}

export function useAllAlerts(alertTypes: string[] = []) {
  const normalizedTypes = alertTypes.map(normalizeType).filter(Boolean)
  const alertType = normalizedTypes.length > 0 ? normalizedTypes.join(',') : undefined

  return useQuery({
    queryKey: ['dashboard', 'alerts', 'all', alertType],
    queryFn: async ({ signal }): Promise<AlertsResponse> => {
      const pageSize = 500
      let offset = 0
      const total = getAlertTotal(normalizedTypes)
      const alerts = new Map<number, Alert>()

      do {
        const page = await apiGet<AlertsResponse>('/dashboard/alerts', { params: { limit: pageSize, offset, alert_type: alertType }, signal })
        const sizeBefore = alerts.size
        page.alerts.forEach((alert) => alerts.set(alert.id, alert))
        offset += page.alerts.length
        if (page.alerts.length === 0 || alerts.size === sizeBefore) break
      } while (alerts.size < total)

      return { count: total, alerts: [...alerts.values()] }
    },
  })
}
