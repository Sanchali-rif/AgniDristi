import { Activity, CheckCircle2, Clock, Play, Upload, XCircle } from 'lucide-react'
import { useLatestRun, useTriggerMonitoring } from '../services/monitoringRunService'
import { useVNFUpload } from '../services/vnfService'
import { useRef, useState } from 'react'

function formatDt(iso: string | null) {
  if (!iso) return '—'
  return new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
}

export default function SystemStatusPage() {
  const { data: latest, isLoading, isError } = useLatestRun()
  const trigger = useTriggerMonitoring()
  const upload = useVNFUpload()
  const fileRef = useRef<HTMLInputElement>(null)
  const [msg, setMsg] = useState('')

  const handleUpload = () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return setMsg('Select a CSV file first.')
    upload.mutate(file, {
      onSuccess: (r) => setMsg(`Uploaded ${r.filename}: ${r.inserted_detections} inserted, ${r.objects_found} objects found.`),
      onError: (e) => setMsg(`Upload failed: ${(e as Error).message}`),
    })
  }

  return (
    <div className="mx-auto max-w-5xl">
      <p className="text-xs font-medium uppercase tracking-wide text-text-secondary">Platform</p>
      <h1 className="mt-1 text-2xl font-semibold text-text-primary">System / Model Status</h1>
      <p className="mt-1 text-sm text-text-secondary">Live backend connectivity and monitoring run status.</p>

      <section className="mt-6 rounded-lg border border-border bg-surface p-5 shadow-sm">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-text-primary"><Activity size={16} />Latest Monitoring Run</h2>
        {isLoading && <p className="mt-3 text-xs text-text-secondary">Loading…</p>}
        {isError && <p className="mt-3 text-xs text-danger">Unable to fetch latest run.</p>}
        {latest && 'run_uid' in latest && (
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Status" value={latest.status} icon={latest.status === 'COMPLETED' ? <CheckCircle2 size={14} className="text-success" /> : <XCircle size={14} className="text-danger" />} />
            <Stat label="Trigger" value={latest.trigger_type} />
            <Stat label="Started" value={formatDt(latest.started_at)} icon={<Clock size={14} />} />
            <Stat label="Duration" value={latest.duration_seconds ? `${latest.duration_seconds.toFixed(1)}s` : '—'} />
            <Stat label="Fetched" value={String(latest.fetched)} />
            <Stat label="Inserted" value={String(latest.inserted)} />
            <Stat label="Matched" value={String(latest.matched)} />
            <Stat label="Alerts Created" value={String(latest.alerts_created)} />
          </div>
        )}
      </section>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <section className="rounded-lg border border-border bg-surface p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-text-primary">Trigger FIRMS Monitoring</h2>
          <p className="mt-1 text-xs text-text-secondary">Manually start a FIRMS data sync.</p>
          <button type="button" disabled={trigger.isPending} onClick={() => trigger.mutate(1, {
            onSuccess: () => setMsg('Monitoring run triggered successfully.'),
            onError: (e) => setMsg(`Trigger failed: ${(e as Error).message}`),
          })} className="mt-4 inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50">
            <Play size={14} />{trigger.isPending ? 'Running…' : 'Run FIRMS Sync'}
          </button>
        </section>

        <section className="rounded-lg border border-border bg-surface p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-text-primary">Upload VNF Dataset</h2>
          <p className="mt-1 text-xs text-text-secondary">Upload a VNF CSV for processing.</p>
          <div className="mt-4 flex items-center gap-3">
            <input ref={fileRef} type="file" accept=".csv" className="text-xs" />
            <button type="button" disabled={upload.isPending} onClick={handleUpload} className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2 text-xs font-medium text-white hover:opacity-90 disabled:opacity-50">
              <Upload size={14} />{upload.isPending ? 'Uploading…' : 'Upload'}
            </button>
          </div>
        </section>
      </div>
      {msg && <p role="status" className="mt-4 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-text-secondary">{msg}</p>}
    </div>
  )
}

function Stat({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="rounded-lg bg-bg p-3">
      <p className="flex items-center gap-1 text-[10px] text-text-secondary">{icon}{label}</p>
      <p className="mt-1 font-mono text-sm font-semibold text-text-primary">{value}</p>
    </div>
  )
}
