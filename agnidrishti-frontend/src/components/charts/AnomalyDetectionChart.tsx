import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useSourceAnomaly } from '../../services/sourceService'

function getSeverity(maxDelta: number) {
  if (maxDelta >= 8) return { label: 'High', className: 'bg-danger/10 text-danger' }
  if (maxDelta >= 4) return { label: 'Medium', className: 'bg-warning/10 text-warning' }
  return { label: 'Low', className: 'bg-success/10 text-success' }
}

export function AnomalyDetectionChart({ sourceId }: { sourceId: string }) {
  const { data = [], isLoading, isError } = useSourceAnomaly(sourceId)
  const maxDelta = data.reduce((max, point) => Math.max(max, point.current - point.baseline), 0)
  const severity = getSeverity(maxDelta)
  const trend = data.length > 0 && data[data.length - 1].current >= data[data.length - 1].baseline ? 'Above baseline' : 'Below baseline'

  return (
    <section aria-label="Anomaly detection">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-text-primary">Anomaly detection</h3>
        {!isLoading && !isError && <span className={`rounded-full px-2 py-1 text-xs font-medium ${severity.className}`}>{severity.label} severity</span>}
      </div>
      {!isLoading && !isError && <p className="mt-1 text-xs text-text-secondary">Trend: {trend}</p>}
       {isLoading && <div className="mt-3 h-40 animate-pulse rounded-lg bg-bg" role="status" aria-label="Loading anomaly data" />}
      {isError && <p className="mt-3 text-xs text-danger">Unable to load anomaly data.</p>}
      {!isLoading && !isError && (
        <div className="mt-3 h-40 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
              <YAxis tick={{ fontSize: 10 }} tickLine={false} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line type="monotone" dataKey="baseline" name="Baseline" stroke="var(--color-text-secondary)" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="current" name="Current" stroke="var(--color-danger)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
