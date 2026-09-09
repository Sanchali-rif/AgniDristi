import { AlertTriangle, ArrowRight, Clock3 } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { ALERT_TYPE_COUNTS, getAlertTotal, useAlerts } from '../../services/alertService'
import { useSourceStore } from '../../stores/sourceStore'
import type { Alert } from '../../types/source'

const PAGE_SIZE = 50
const SEVERITY_STYLES: Record<string, string> = { CRITICAL: 'bg-red-600 text-white', HIGH: 'bg-red-600 text-white', MEDIUM: 'bg-amber-500 text-black', LOW: 'bg-emerald-500 text-black' }
const typeLabel = (alertType: string) => alertType.replaceAll('_', ' ')

function formatTimestamp(ts?: string | null) {
  if (!ts) return 'Not available'
  const date = new Date(ts)
  return Number.isNaN(date.getTime()) ? ts : new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

function AlertRow({ alert }: { alert: Alert }) {
  const openPanel = useSourceStore((state) => state.openPanel)
  const severity = alert.severity?.toUpperCase() ?? 'LOW'
  const style = SEVERITY_STYLES[severity] ?? SEVERITY_STYLES.LOW

  return (
    <li className="flex flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-start gap-3">
        <AlertTriangle size={20} className="mt-0.5 shrink-0 stroke-[2.2] text-text-primary" />
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2"><h3 className="font-bold uppercase text-text-primary">{typeLabel(alert.alert_type)}</h3><span className={`border border-black px-2 py-0.5 font-mono text-[10px] font-black uppercase ${style}`}>{severity}</span></div>
          <p className="mt-1 font-mono text-xs font-bold text-text-secondary">{alert.object_uid ?? `Alert #${alert.id}`}</p>
          {alert.message && <p className="mt-1 text-xs text-text-secondary">{alert.message}</p>}
          {alert.latitude != null && alert.longitude != null && <p className="mt-1 font-mono text-xs text-text-secondary">{alert.latitude.toFixed(4)}, {alert.longitude.toFixed(4)}</p>}
          <p className="mt-1 flex items-center gap-1 text-xs font-semibold text-text-secondary"><Clock3 size={12} />{formatTimestamp(alert.created_at)}</p>
        </div>
      </div>
      {alert.object_uid && <button type="button" onClick={() => openPanel(alert.object_uid!)} className="inline-flex shrink-0 items-center gap-2 border-2 border-black bg-black px-3 py-1.5 text-xs font-black uppercase text-white hover:bg-zinc-800 dark:bg-[#d8f5a9] dark:text-black">Investigate <ArrowRight size={14} /></button>}
    </li>
  )
}

export function AlertsList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedType = searchParams.get('type')?.split(',')[0]?.trim().toUpperCase() || null
  const selectedTypes = selectedType ? [selectedType] : []
  const requestedPage = Number(searchParams.get('page') ?? 1)
  const page = Number.isInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1
  const offset = (page - 1) * PAGE_SIZE
  const alertsQuery = useAlerts({ alertTypes: selectedTypes, limit: PAGE_SIZE, offset })
  const alerts = alertsQuery.data?.alerts ?? []
  const filteredTotal = getAlertTotal(selectedTypes)
  const allTotal = getAlertTotal()
  const firstResult = filteredTotal === 0 ? 0 : offset + 1
  const lastResult = Math.min(offset + alerts.length, filteredTotal)
  const canGoNext = offset + alerts.length < filteredTotal

  const selectType = (nextType: string | null) => {
    const next = new URLSearchParams()
    if (nextType) next.set('type', nextType)
    setSearchParams(next)
  }

  const goToPage = (nextPage: number) => {
    const next = new URLSearchParams(searchParams)
    if (nextPage <= 1) next.delete('page')
    else next.set('page', String(nextPage))
    setSearchParams(next)
  }

  if (alertsQuery.isLoading) return <p className="mt-6 text-sm font-bold text-text-secondary">Loading alerts...</p>
  if (alertsQuery.isError) return <div className="mt-6 border-2 border-black bg-surface p-6 text-center"><p className="text-sm font-bold text-danger">Unable to load alerts.</p><button type="button" onClick={() => alertsQuery.refetch()} className="mt-3 border-2 border-black px-3 py-1 text-xs font-black uppercase">Retry</button></div>

  return (
    <div className="mt-6 border-2 border-black bg-surface shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black px-4 py-3">
        <div><h2 className="text-sm font-black uppercase tracking-wider text-text-primary">Active Alerts Stream</h2><p className="mt-0.5 text-xs font-medium text-text-secondary">Real-time thermal source detection and satellite anomaly alerts.</p></div>
        <div className="text-right text-xs font-bold text-text-secondary"><span className="font-mono text-text-primary">{firstResult}-{lastResult}</span> OF <span className="font-mono text-text-primary">{filteredTotal}</span> ALERTS · POLLING 30S{alertsQuery.isFetching && !alertsQuery.isLoading ? ' · UPDATING' : ''}{alertsQuery.dataUpdatedAt > 0 && <p className="mt-0.5 text-[10px]">Updated {formatTimestamp(new Date(alertsQuery.dataUpdatedAt).toISOString())}</p>}</div>
      </div>
      <div className="flex flex-wrap gap-2 border-b-2 border-black bg-surface p-3" aria-label="Filter alerts by type">
        <button type="button" onClick={() => selectType(null)} aria-pressed={!selectedType} className={`border-2 border-black px-3 py-1 text-xs font-black uppercase transition-all ${!selectedType ? 'bg-black text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] dark:bg-[#d8f5a9] dark:text-black' : 'bg-surface text-text-primary hover:bg-black hover:text-white'}`}>All Categories ({allTotal})</button>
        {ALERT_TYPE_COUNTS.map(({ alertType, count }) => (
          <button key={alertType} type="button" onClick={() => selectType(alertType)} aria-pressed={selectedType === alertType} className={`border-2 border-black px-3 py-1 text-xs font-black uppercase transition-all ${selectedType === alertType ? 'bg-black text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] dark:bg-[#d8f5a9] dark:text-black' : 'bg-surface text-text-primary hover:bg-black hover:text-white'}`}>{typeLabel(alertType)} ({count})</button>
        ))}
      </div>
      {alerts.length === 0 ? <p className="p-8 text-center text-sm font-bold text-text-secondary">No alerts found for the selected categories.</p> : <ul className="divide-y divide-black/20" aria-label="Active alerts">{alerts.map((alert) => <AlertRow key={alert.id} alert={alert} />)}</ul>}
      {filteredTotal > PAGE_SIZE && <div className="flex items-center justify-between gap-3 border-t-2 border-black p-3"><button type="button" disabled={page === 1 || alertsQuery.isFetching} onClick={() => goToPage(page - 1)} className="border-2 border-black px-3 py-1.5 text-xs font-black uppercase disabled:cursor-not-allowed disabled:opacity-40">Previous</button><span className="font-mono text-xs font-bold">Page {page} of {Math.ceil(filteredTotal / PAGE_SIZE)}</span><button type="button" disabled={!canGoNext || alertsQuery.isFetching} onClick={() => goToPage(page + 1)} className="border-2 border-black bg-black px-3 py-1.5 text-xs font-black uppercase text-white disabled:cursor-not-allowed disabled:opacity-40 dark:bg-[#d8f5a9] dark:text-black">Next</button></div>}
    </div>
  )
}
