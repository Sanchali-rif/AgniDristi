import { ActivityTimelineChart } from '../charts/ActivityTimelineChart'
import { ThermalFingerprintChart } from '../charts/ThermalFingerprintChart'
import { AnomalyDetectionChart } from '../charts/AnomalyDetectionChart'

export function DashboardCharts({ sourceId }: { sourceId: string | null }) {
  const placeholder = (title: string) => (
    <section aria-label={title} className="py-2">
      <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary">{title}</h3>
      <p className="mt-2 text-xs text-text-secondary font-medium">Select a source pin on the map to display data.</p>
    </section>
  )

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="rounded-none border-2 border-black bg-surface p-5 shadow-sm">
        {sourceId ? <ActivityTimelineChart sourceId={sourceId} /> : placeholder('Historical activity')}
      </div>
      <div className="rounded-none border-2 border-black bg-surface p-5 shadow-sm">
        {sourceId ? <ThermalFingerprintChart sourceId={sourceId} /> : placeholder('Thermal fingerprint')}
      </div>
      <div className="rounded-none border-2 border-black bg-surface p-5 shadow-sm">
        {sourceId ? <AnomalyDetectionChart sourceId={sourceId} /> : placeholder('Anomaly detection')}
      </div>
    </div>
  )
}

