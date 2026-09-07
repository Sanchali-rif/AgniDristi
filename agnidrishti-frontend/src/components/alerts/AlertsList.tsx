import { AlertTriangle, ArrowRight, Clock3 } from 'lucide-react'
import { useAlerts } from '../../services/alertService'
import { useSourceStore } from '../../stores/sourceStore'
import type { Alert } from '../../types/source'

const SEVERITY_STYLES: Record<string, string> = {
  HIGH: 'border-black bg-red-600 text-white font-bold',
  MEDIUM: 'border-black bg-amber-500 text-black font-bold',
  LOW: 'border-black bg-zinc-200 text-black font-bold',
}

function formatTimestamp(ts: string | null) {
  if (!ts) return '—'
  return new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(ts))
}

function AlertRow({ alert }: { alert: Alert }) {
  const openPanel = useSourceStore((s) => s.openPanel)
  const sev = alert.severity?.toUpperCase() ?? 'LOW'
  const style = SEVERITY_STYLES[sev] ?? SEVERITY_STYLES.LOW

  return (
    <li className="flex flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex min-w-0 items-start gap-3">
        <AlertTriangle size={20} className="mt-0.5 text-text-primary shrink-0 stroke-[2.2]" aria-hidden="true" />
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-bold uppercase text-text-primary">
              {alert.alert_type.replaceAll('_', ' ').toLowerCase()}
            </h3>
            <span className={`border px-2 py-0.5 font-mono text-[10px] uppercase ${style}`}>
              {sev}
            </span>
          </div>
          <p className="mt-1 font-mono text-xs text-text-secondary font-bold">
            {alert.object_uid ?? alert.firms_uid ?? `Alert #${alert.id}`}
          </p>
          {alert.message && <p className="mt-1 text-xs text-text-secondary">{alert.message}</p>}
          <p className="mt-1 flex items-center gap-1 text-xs text-text-secondary font-semibold">
            <Clock3 size={12} aria-hidden="true" />
            {formatTimestamp(alert.created_at)}
          </p>
        </div>
      </div>
      {alert.object_uid && (
        <button type="button" onClick={() => openPanel(alert.object_uid!)}
          className="inline-flex shrink-0 items-center gap-2 self-start border-2 border-black bg-black px-3 py-1.5 text-xs font-black uppercase text-white hover:bg-zinc-800 sm:self-auto">
          Investigate <ArrowRight size={14} aria-hidden="true" />
        </button>
      )}
    </li>
  )
}

export function AlertsList() {
  const { data: alerts = [], isLoading, isError, dataUpdatedAt } = useAlerts()

  if (isLoading) return <p className="mt-6 text-sm font-bold text-text-secondary">Loading alerts…</p>
  if (isError) return <p className="mt-6 text-sm font-bold text-danger">Unable to load alerts.</p>
  if (alerts.length === 0) return <p className="mt-6 border-2 border-black bg-surface p-8 text-center text-sm font-bold text-text-secondary">No active alerts.</p>

  return (
    <div className="mt-6 border-2 border-black bg-surface shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black px-4 py-3">
        <div>
          <h2 className="text-sm font-black uppercase tracking-wider text-text-primary">Active Alerts Stream</h2>
          <p className="mt-0.5 text-xs text-text-secondary font-medium">Thermal source alerts fetched from /dashboard/alerts API.</p>
        </div>
        <div className="text-right text-xs text-text-secondary font-bold">
          <span className="font-mono text-text-primary">{alerts.length}</span> ALERTS · POLLING 30S
          {dataUpdatedAt > 0 && <p className="mt-0.5 text-[10px]">Updated {formatTimestamp(new Date(dataUpdatedAt).toISOString())}</p>}
        </div>
      </div>
      <ul className="divide-y divide-black/20" aria-label="Active alerts">
        {alerts.map((a) => <AlertRow key={a.id} alert={a} />)}
      </ul>
    </div>
  )
}

