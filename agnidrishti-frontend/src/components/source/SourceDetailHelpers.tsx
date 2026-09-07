import { MAP_CATEGORY_COLORS, MAP_CATEGORY_LABELS, getMapCategory } from '../../lib/mapColors'
import type { SourceDetail } from '../../types/source'

export function DetailField({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="border-b border-border py-3 last:border-b-0">
      <dt className="text-xs font-medium uppercase tracking-wide text-text-secondary">{label}</dt>
      <dd className="mt-1 text-sm tabular-nums text-text-primary">{value}</dd>
    </div>
  )
}

function StatusBadge({ label, color }: { label: string; color: string }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide"
      style={{ backgroundColor: `${color}14`, borderColor: `${color}40`, color }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} aria-hidden="true" />
      {label}
    </span>
  )
}

function getConfidenceColor(confidence: number) {
  if (confidence >= 80) return '#22C55E'
  if (confidence >= 50) return '#F59E0B'
  return '#EF4444'
}

const PERSISTENCE_COLORS = { persistent: '#A855F7', new: '#3B82F6', transient: '#64748B' } as const
const ANOMALY_COLORS = { low: '#22C55E', medium: '#F59E0B', high: '#EF4444' } as const

export function SourceStatusSummary({ source }: { source: SourceDetail }) {
  const mapCategory = getMapCategory(source.category)
  return (
    <div className="mt-5 flex flex-wrap gap-2" aria-label="Source status summary">
      <StatusBadge label={MAP_CATEGORY_LABELS[mapCategory]} color={MAP_CATEGORY_COLORS[mapCategory]} />
      <StatusBadge label={source.status} color={PERSISTENCE_COLORS[source.status]} />
      <StatusBadge label={`${source.confidence}% confidence`} color={getConfidenceColor(source.confidence)} />
      <StatusBadge label={`${source.anomalyLevel} anomaly`} color={ANOMALY_COLORS[source.anomalyLevel]} />
    </div>
  )
}
