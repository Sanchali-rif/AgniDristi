import { CheckCircle2, Clock3, Radio, ScanSearch } from 'lucide-react'
import { useSourceHistory } from '../../services/sourceService'
import type { SourceDetail } from '../../types/source'

type TimelineEvent = {
  date: string
  title: string
  detail: string
  icon: typeof CheckCircle2
  tone: string
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium' }).format(new Date(value))
}

export function SourceHistoryTimeline({ source }: { source: SourceDetail }) {
  const { data: history = [], isLoading, isError } = useSourceHistory(source.id)
  const latestActivity = history[history.length - 1]
  const statusLabel = source.status === 'persistent' ? 'Persistence confirmed' : `Status marked ${source.status}`

  const events: TimelineEvent[] = [
    {
      date: source.firstDetected,
      title: 'First detected',
      detail: `Thermal source identified at ${source.lat.toFixed(4)}, ${source.lon.toFixed(4)}.`,
      icon: Radio,
      tone: 'bg-info text-white',
    },
    {
      date: source.firstDetected,
      title: 'Source classified',
      detail: `${source.industrySubtype ?? 'Unclassified source'} · ${source.confidence}% confidence`,
      icon: ScanSearch,
      tone: 'bg-accent text-white',
    },
    {
      date: source.lastDetected,
      title: statusLabel,
      detail: `${source.anomalyLevel} anomaly level recorded in the current assessment.`,
      icon: CheckCircle2,
      tone: 'bg-success text-white',
    },
    ...(latestActivity ? [{
      date: `${latestActivity.month}-01`,
      title: 'Latest activity observation',
      detail: `${latestActivity.detections} detections · average temperature ${latestActivity.avgTempK} K`,
      icon: Clock3,
      tone: 'bg-warning text-white',
    }] : []),
    {
      date: source.lastDetected,
      title: 'Last detected',
      detail: 'Most recent observation in the selected source record.',
      icon: Radio,
      tone: 'bg-text-secondary text-white',
    },
  ]

  return (
    <section aria-labelledby="source-history-heading">
      <div>
        <h2 id="source-history-heading" className="text-lg font-semibold text-text-primary">Source history</h2>
        <p className="mt-1 text-sm text-text-secondary">Detection lifecycle and status changes for {source.id}.</p>
      </div>
      {isLoading && <p className="mt-6 text-sm text-text-secondary">Loading source history...</p>}
      {isError && <p className="mt-6 text-sm text-danger">Unable to load source history.</p>}
      {!isLoading && !isError && (
        <ol className="mt-6">
          {events.map((event, index) => {
            const Icon = event.icon
            return (
              <li key={`${event.title}-${event.date}`} className="relative flex gap-4 pb-7 last:pb-0">
                {index < events.length - 1 && <span className="absolute left-[15px] top-8 h-[calc(100%-8px)] w-px bg-border" aria-hidden="true" />}
                <span className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${event.tone}`}><Icon size={15} aria-hidden="true" /></span>
                <div className="min-w-0 pt-0.5">
                  <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1"><h3 className="text-sm font-medium text-text-primary">{event.title}</h3><time className="font-mono text-xs text-text-secondary" dateTime={event.date}>{formatDate(event.date)}</time></div>
                  <p className="mt-1 text-sm text-text-secondary">{event.detail}</p>
                </div>
              </li>
            )
          })}
        </ol>
      )}
    </section>
  )
}
