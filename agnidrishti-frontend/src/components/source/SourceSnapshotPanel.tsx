import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useSourceStore } from '../../stores/sourceStore'
import { useSourceDetail } from '../../services/sourceService'
import { DataSourceBadge } from './DataSourceBadge'
import { DetailField, SourceStatusSummary } from './SourceDetailHelpers'

export function SourceSnapshotPanel() {
  const selectedSourceId = useSourceStore((s) => s.selectedSourceId)
  const isPanelOpen = useSourceStore((s) => s.isPanelOpen)
  const closePanel = useSourceStore((s) => s.closePanel)
  const { data: source, isLoading, isError } = useSourceDetail(selectedSourceId)

  function handleClose() {
    closePanel()
    requestAnimationFrame(() => document.querySelector<HTMLElement>('.leaflet-container')?.focus())
  }

  return (
    <AnimatePresence>
      {isPanelOpen && (
        <motion.aside initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ type: 'tween', duration: 0.24 }}
          role="dialog" aria-modal="true" aria-label="Source snapshot"
          className="source-panel-scroll fixed inset-y-0 right-0 z-[1100] w-full max-w-md overflow-y-auto border-l border-border bg-surface p-6 shadow-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-text-secondary">Source snapshot</p>
              <h2 className="mt-1 text-xl font-semibold text-text-primary">{selectedSourceId}</h2>
            </div>
            <button type="button" onClick={handleClose} aria-label="Close source snapshot"
              className="rounded-lg p-2 text-text-secondary hover:bg-bg hover:text-text-primary">
              <X size={20} aria-hidden="true" />
            </button>
          </div>
          {isLoading && <p className="mt-6 text-sm text-text-secondary">Loading source details...</p>}
          {isError && <p className="mt-6 text-sm text-danger">Unable to load source details.</p>}
          {source && (
            <>
              <SourceStatusSummary source={source} />
              <div className="mt-4"><DataSourceBadge /></div>
              <dl className="mt-5">
                <DetailField label="Source ID" value={source.id} />
                <DetailField label="Classification" value={source.category} />
                <DetailField label="Industry subtype" value={source.industrySubtype ?? 'Not classified'} />
                <DetailField label="Confidence score" value={`${source.confidence}%`} />
                <DetailField label="Persistence status" value={source.status} />
                <DetailField label="Anomaly level" value={source.anomalyLevel} />
                <DetailField label="Coordinates" value={`${source.lat.toFixed(4)}, ${source.lon.toFixed(4)}`} />
              </dl>
              <Link to={`/investigation/${encodeURIComponent(source.id)}`} onClick={handleClose}
                className="mt-6 block rounded-lg bg-accent px-4 py-2.5 text-center text-sm font-medium text-white hover:opacity-90">
                View Full Investigation
              </Link>
            </>
          )}
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
