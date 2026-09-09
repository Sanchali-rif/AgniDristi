import { Link, useParams } from 'react-router-dom'
import { SatelliteContextViewer } from '../components/satellite/SatelliteContextViewer'
import { SourceHistoryTimeline } from '../components/timeline/SourceHistoryTimeline'
import { ActivityTimelineChart } from '../components/charts/ActivityTimelineChart'
import { ThermalFingerprintChart } from '../components/charts/ThermalFingerprintChart'
import { AnomalyDetectionChart } from '../components/charts/AnomalyDetectionChart'
import { useSourceDetail, useSources } from '../services/sourceService'
import { useSourceStore } from '../stores/sourceStore'

export default function InvestigationPage() {
  const { sourceId: routeSourceId } = useParams()
  const selectedSourceId = useSourceStore((state) => state.selectedSourceId)
  const sourceId = routeSourceId ? decodeURIComponent(routeSourceId) : selectedSourceId
  const { data: source, isLoading, isError } = useSourceDetail(sourceId)
  const { data: sources = [] } = useSources()

  if (!sourceId) {
    return (
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-text-secondary">SOURCE INVESTIGATION</span>
          <h1 className="text-2xl font-black uppercase tracking-tight text-text-primary">Thermal Source Intelligence Dossier</h1>
        </div>
        <div className="border-2 border-text-primary bg-surface p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <h2 className="text-sm font-black uppercase tracking-wider text-text-primary">Select a Thermal Source for Deep-Dive Analysis</h2>
          <p className="mt-1 text-xs font-medium text-text-secondary">
            Select a registered thermal source below to inspect satellite context imagery, activity timelines, and thermal fingerprints.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {sources.slice(0, 8).map((s) => (
              <Link key={s.id} to={`/investigation/${encodeURIComponent(s.id)}`} className="border-2 border-text-primary bg-bg/50 px-3 py-1.5 font-mono text-xs font-bold text-text-primary hover:bg-[#d8f5a9] hover:text-black transition-colors">
                {s.id} ({s.anomalyLevel.toUpperCase()})
              </Link>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-text-primary/20 pt-4">
            <Link to="/anomaly" className="border-2 border-text-primary bg-[#d8f5a9] px-4 py-2 text-xs font-black uppercase text-black hover:bg-[#c9f090]">
              Browse Anomaly Radar →
            </Link>
            <Link to="/dashboard" className="border-2 border-text-primary bg-surface px-4 py-2 text-xs font-black uppercase text-text-primary hover:bg-black hover:text-white dark:hover:bg-zinc-800">
              Open Spatial Map →
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <Link to="/dashboard" className="text-xs font-black uppercase text-text-primary hover:underline">← Back to dashboard</Link>
      <div className="flex flex-wrap items-end justify-between gap-3 border-b-2 border-text-primary pb-4">
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-text-secondary">SOURCE INVESTIGATION</span>
          <h1 className="mt-1 text-3xl font-black uppercase tracking-tight text-text-primary">{sourceId}</h1>
          <p className="mt-1 text-xs font-semibold text-text-secondary">Context and spatial proximity assessment</p>
        </div>
        {source && (
          <div className="flex items-center gap-2">
            <span className="border-2 border-black dark:border-zinc-700 bg-[#d8f5a9] px-3 py-1 text-xs font-black uppercase text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              {source.industrySubtype ?? source.category} · {source.confidence}% CONF
            </span>
          </div>
        )}
      </div>
      {isLoading && <p className="mt-8 text-xs font-bold uppercase text-text-secondary">Loading source details...</p>}
      {isError && <p className="mt-8 text-xs font-bold uppercase text-danger">Unable to load source details.</p>}
      {source && (
        <>
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="border-2 border-black dark:border-zinc-700 bg-surface p-5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"><ActivityTimelineChart sourceId={source.id} /></div>
            <div className="border-2 border-black dark:border-zinc-700 bg-surface p-5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"><ThermalFingerprintChart sourceId={source.id} /></div>
            <div className="border-2 border-black dark:border-zinc-700 bg-surface p-5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"><AnomalyDetectionChart sourceId={source.id} anomalyLevel={source.anomalyLevel} /></div>
          </div>
          <div className="border-2 border-black dark:border-zinc-700 bg-surface p-5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"><SatelliteContextViewer sourceId={source.id} /></div>
          <div className="border-2 border-black dark:border-zinc-700 bg-surface p-5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"><SourceHistoryTimeline source={source} /></div>
        </>
      )}
    </div>
  )
}
