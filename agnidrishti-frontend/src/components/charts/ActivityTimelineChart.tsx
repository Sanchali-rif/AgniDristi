import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useSourceHistory } from '../../services/sourceService'

export function ActivityTimelineChart({ sourceId }: { sourceId: string }) {
  const { data = [], isLoading, isError } = useSourceHistory(sourceId)

  return (
    <section aria-label="Historical activity">
      <h3 className="text-sm font-semibold text-text-primary">Historical activity</h3>
       {isLoading && <div className="mt-3 h-48 animate-pulse rounded-lg bg-bg" role="status" aria-label="Loading activity" />}
      {isError && <p className="mt-3 text-xs text-danger">Unable to load activity.</p>}
      {!isLoading && !isError && (
        <div className="mt-3 h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} tickLine={false} />
              <YAxis yAxisId="detections" tick={{ fontSize: 10 }} tickLine={false} />
              <YAxis yAxisId="temperature" orientation="right" tick={{ fontSize: 10 }} tickLine={false} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar yAxisId="detections" dataKey="detections" name="Detections" fill="var(--color-accent)" radius={[3, 3, 0, 0]} />
              <Line yAxisId="temperature" type="monotone" dataKey="avgTempK" name="Avg temp (K)" stroke="var(--color-info)" strokeWidth={2} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
