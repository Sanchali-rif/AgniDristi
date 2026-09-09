import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ALERT_TYPE_COUNTS, getAlertTotal, useAlerts } from '../../services/alertService'
import { useSourceStore } from '../../stores/sourceStore'

const formatTime = (input: string | null) => {
  if (!input) return 'Creation time unavailable'
  const date = new Date(input)
  return Number.isNaN(date.getTime()) ? input : new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

export function RecentAlertsWidget() {
  const [selectedCat, setSelectedCat] = useState<string>('ALL')
  const query = useAlerts({ alertTypes: selectedCat === 'ALL' ? [] : [selectedCat], limit: 5 })
  const openPanel = useSourceStore((state) => state.openPanel)
  const allAlerts = query.data?.alerts ?? []
  const allCount = getAlertTotal()
  const selectedCount = selectedCat === 'ALL' ? allCount : getAlertTotal([selectedCat])

  return (
    <section className="border-2 border-text-primary bg-surface p-5" aria-labelledby="recent-alerts-heading">
      <div className="flex items-center justify-between border-b-2 border-text-primary pb-3">
        <div>
          <h2 id="recent-alerts-heading" className="text-sm font-black uppercase tracking-wider">Recent alerts</h2>
          <p className="mt-0.5 text-[10px] font-bold text-text-secondary">Grouped anomaly detection events</p>
        </div>
        <Link to={`/alerts${selectedCat !== 'ALL' ? `?type=${selectedCat}` : ''}`} className="border-2 border-black bg-black px-2.5 py-1 text-xs font-black uppercase hover:text-white dark:bg-[#d8f5a9] dark:text-black hover:bg-zinc-800">
          View all ({selectedCount})
        </Link>
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5 border-b border-text-primary/20 pb-3">
        <button type="button" onClick={() => setSelectedCat('ALL')} aria-pressed={selectedCat === 'ALL'} className={`border border-black px-2.5 py-1 text-[10px] font-black uppercase transition-colors ${selectedCat === 'ALL' ? 'bg-black text-white dark:bg-[#d8f5a9] dark:text-black' : 'bg-surface text-text-primary hover:bg-black/10'}`}>All ({allCount})</button>
        {ALERT_TYPE_COUNTS.map(({ alertType, count }) => <button key={alertType} type="button" onClick={() => setSelectedCat(alertType)} aria-pressed={selectedCat === alertType} className={`border border-black px-2.5 py-1 text-[10px] font-black uppercase transition-colors ${selectedCat === alertType ? 'bg-black text-white dark:bg-[#d8f5a9] dark:text-black' : 'bg-surface text-text-primary hover:bg-black/10'}`}>{alertType.replaceAll('_', ' ')} ({count})</button>)}
      </div>

      {query.isLoading && <div className="mt-4 space-y-2" role="status"><div className="h-14 animate-pulse bg-text-primary/10" /><div className="h-14 animate-pulse bg-text-primary/10" /></div>}
      {query.isError && <div className="py-8 text-center"><p className="text-xs font-bold text-danger">Alerts could not be loaded.</p><button type="button" onClick={() => query.refetch()} className="mt-3 border-2 border-black px-3 py-1 text-xs font-black uppercase">Retry</button></div>}
      {!query.isLoading && !query.isError && allAlerts.length === 0 && <p className="py-8 text-center text-xs font-bold text-text-secondary">No alerts in this category.</p>}

      <ul className="divide-y divide-text-primary/15">
        {allAlerts.map((alert) => (
          <li key={alert.id} className="py-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-black uppercase">{alert.alert_type.replaceAll('_', ' ')}</p>
                <p className="mt-1 text-xs text-text-secondary">{alert.message ?? 'No message provided'}</p>
                <p className="mt-1 font-mono text-[10px] text-text-secondary">{formatTime(alert.created_at)}{alert.latitude != null && alert.longitude != null ? ` · ${alert.latitude.toFixed(4)}, ${alert.longitude.toFixed(4)}` : ''}</p>
              </div>
              <span className="border-2 border-black px-2 py-0.5 text-[10px] font-black uppercase">{alert.severity ?? 'MEDIUM'}</span>
            </div>
            {alert.object_uid && <button type="button" onClick={() => openPanel(alert.object_uid!)} className="mt-2 text-[10px] font-black uppercase underline">Open object {alert.object_uid}</button>}
          </li>
        ))}
      </ul>
    </section>
  )
}
