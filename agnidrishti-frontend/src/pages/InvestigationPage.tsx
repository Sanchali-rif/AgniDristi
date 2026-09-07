import { Link, useParams } from 'react-router-dom'
import { NearbyFacilitiesTable } from '../components/tables/NearbyFacilitiesTable'
import { SatelliteContextViewer } from '../components/satellite/SatelliteContextViewer'
import { SourceHistoryTimeline } from '../components/timeline/SourceHistoryTimeline'
import { ActivityTimelineChart } from '../components/charts/ActivityTimelineChart'
import { ThermalFingerprintChart } from '../components/charts/ThermalFingerprintChart'
import { AnomalyDetectionChart } from '../components/charts/AnomalyDetectionChart'
import { useSourceDetail } from '../services/sourceService'
import { useSources } from '../services/sourceService'
import { useSourceStore } from '../stores/sourceStore'

export default function InvestigationPage() {
  const { sourceId: routeSourceId } = useParams()
  const selectedSourceId = useSourceStore((state) => state.selectedSourceId)
  const { data: sources = [] } = useSources()
  const sourceId = routeSourceId ? decodeURIComponent(routeSourceId) : selectedSourceId ?? sources[0]?.id
  const { data: source, isLoading, isError } = useSourceDetail(sourceId)

  return (
    <div className="mx-auto max-w-6xl">
      <Link to="/dashboard" className="text-xs font-medium text-accent hover:underline">← Back to dashboard</Link>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-text-secondary">Source investigation</p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">{sourceId}</h1>
          <p className="mt-1 text-sm text-text-secondary">Context and proximity assessment</p>
        </div>
        {source && <span className="rounded-full bg-accent/10 px-3 py-1.5 text-xs font-medium text-accent">{source.category} · {source.confidence}% confidence</span>}
      </div>
      {!sourceId && <p className="mt-8 text-sm text-text-secondary">Loading sources from the backend...</p>}
      {isLoading && <p className="mt-8 text-sm text-text-secondary">Loading source details...</p>}
      {isError && <p className="mt-8 text-sm text-danger">Unable to load source details.</p>}
      {source && (
        <>
          <div className="mt-8 grid gap-6 lg:grid-cols-3">
            <div className="rounded-lg border border-border bg-surface p-5 shadow-sm"><ActivityTimelineChart sourceId={source.id} /></div>
            <div className="rounded-lg border border-border bg-surface p-5 shadow-sm"><ThermalFingerprintChart sourceId={source.id} /></div>
            <div className="rounded-lg border border-border bg-surface p-5 shadow-sm"><AnomalyDetectionChart sourceId={source.id} /></div>
          </div>
          <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,1fr)]">
            <div className="rounded-lg border border-border bg-surface p-5 shadow-sm"><SatelliteContextViewer sourceId={source.id} /></div>
            <div className="rounded-lg border border-border bg-surface p-5 shadow-sm"><NearbyFacilitiesTable sourceId={source.id} /></div>
          </div>
          <div className="mt-6 rounded-lg border border-border bg-surface p-5 shadow-sm"><SourceHistoryTimeline source={source} /></div>
        </>
      )}
    </div>
  )
}
