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
      <div className="flex items-center justify-between border-b border-black/10 dark:border-zinc-800 pb-2">
        <h3 className="text-xs font-black uppercase tracking-wider text-text-primary">Historical Activity</h3>
        <span className="font-mono text-[10px] font-bold text-text-secondary">{sourceId}</span>
      </div>
      {isLoading && <div className="mt-3 h-44 animate-pulse bg-zinc-200 dark:bg-zinc-800" role="status" aria-label="Loading activity" />}
      {isError && <p className="mt-3 text-xs font-bold text-danger">Unable to load activity.</p>}
      {!isLoading && !isError && (
        <div className="mt-3 h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -22 }}>
              <CartesianGrid stroke="#71717a" strokeDasharray="2 2" strokeOpacity={0.3} />
              <XAxis dataKey="month" tick={{ fontSize: 10, fill: 'currentColor' }} tickLine={false} />
              <YAxis yAxisId="detections" tick={{ fontSize: 10, fill: 'currentColor' }} tickLine={false} />
              <YAxis yAxisId="temperature" orientation="right" tick={{ fontSize: 10, fill: 'currentColor' }} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(255, 255, 255, 0.08)' }} contentStyle={{ backgroundColor: '#18181b', color: '#fff', border: '1px solid #3f3f46', fontSize: '11px', borderRadius: '0px' }} />
              <Legend wrapperStyle={{ fontSize: 10, fontWeight: 700 }} />
              <Bar yAxisId="detections" dataKey="detections" name="Detections" fill="#22c55e" radius={[2, 2, 0, 0]} />
              <Line yAxisId="temperature" type="monotone" dataKey="avgTempK" name="Avg temp (K)" stroke="#3b82f6" strokeWidth={2.5} dot={{ r: 3, fill: '#3b82f6' }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
