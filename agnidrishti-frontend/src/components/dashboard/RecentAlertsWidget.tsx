import { Link } from 'react-router-dom'
import { useAlerts } from '../../services/alertService'
import type { Alert } from '../../types/source'

function formatAlertType(type: string) {
  return type.replaceAll('_', ' ').toLowerCase()
}

function formatTimestamp(ts: string | null) {
  if (!ts) return '—'
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
  }).format(new Date(ts))
}

function severityStyle(severity: string | null) {
  const s = severity?.toUpperCase()
  if (s === 'HIGH') return 'bg-red-600 text-white font-bold'
  if (s === 'MEDIUM') return 'bg-amber-500 text-black font-bold'
  return 'bg-zinc-200 text-black font-bold'
}

function AlertRow({ alert }: { alert: Alert }) {
  return (
    <div className="flex items-start justify-between gap-3 py-3 first:pt-0 last:pb-0">
      <div className="min-w-0">
        <p className="truncate text-xs font-bold uppercase text-text-primary">
          {formatAlertType(alert.alert_type)}
        </p>
        <p className="mt-1 truncate font-mono text-[10px] text-text-secondary">
          {alert.object_uid ?? alert.firms_uid ?? `Alert #${alert.id}`}
        </p>
        <p className="mt-1 text-[10px] text-text-secondary">
          {formatTimestamp(alert.created_at)}
        </p>
      </div>
      <span className={`shrink-0 border border-black px-2 py-0.5 font-mono text-[10px] uppercase ${severityStyle(alert.severity)}`}>
        {alert.severity ?? 'info'}
      </span>
    </div>
  )
}

export function RecentAlertsWidget() {
  const { data: alerts = [], isLoading } = useAlerts()
  const sorted = [...alerts]
    .sort((a, b) => Date.parse(b.created_at ?? '') - Date.parse(a.created_at ?? ''))
    .slice(0, 5)

  return (
    <section className="rounded-none border-2 border-black bg-surface p-5 shadow-sm" aria-labelledby="recent-alerts-heading">
      <div className="flex items-center justify-between gap-3 border-b-2 border-black pb-3">
        <h2 id="recent-alerts-heading" className="text-sm font-black uppercase tracking-wider text-text-primary">Recent Alerts</h2>
        <Link to="/alerts" className="text-xs font-bold uppercase tracking-wider text-text-primary hover:underline">View All →</Link>
      </div>
      <div className="mt-4 divide-y divide-black/20">
        {isLoading && <p className="py-3 text-xs font-bold text-text-secondary">Loading…</p>}
        {!isLoading && sorted.map((a) => <AlertRow key={a.id} alert={a} />)}
        {!isLoading && alerts.length === 0 && (
          <p className="py-3 text-xs text-text-secondary">No recent alerts.</p>
        )}
      </div>
    </section>
  )
}

