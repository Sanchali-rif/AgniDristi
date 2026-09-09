import { useRef, useState } from 'react'
import { Activity, FolderOpen, Play, Upload } from 'lucide-react'
import { useLatestMonitoringRun, useMonitoringRunHistory, useTriggerMonitoringRun, useVnfCsvUpload } from '../services/dashboardService'
import type { MonitoringRun, VnfUploadResult } from '../types/dashboard'

const show = (value: string | number | null | undefined) => value == null ? 'Not available' : String(value)
const time = (value: string | null | undefined) => value ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : 'Not available'

function RunSummary({ run }: { run: MonitoringRun }) {
  return <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Stat label="Status" value={run.status} /><Stat label="Trigger" value={run.trigger_type} /><Stat label="Started" value={time(run.started_at)} /><Stat label="Duration" value={run.duration_seconds == null ? 'Not available' : `${run.duration_seconds.toFixed(1)} s`} /><Stat label="Fetched" value={show(run.fetched)} /><Stat label="Inserted" value={show(run.inserted)} /><Stat label="Matched" value={show(run.matched)} /><Stat label="Alerts created" value={show(run.alerts_created)} /></div>
}

export default function SystemStatusPage() {
  const latest = useLatestMonitoringRun()
  const history = useMonitoringRunHistory(20)
  const trigger = useTriggerMonitoringRun()
  const upload = useVnfCsvUpload()
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [dayRange, setDayRange] = useState(1)
  const [uploadPercent, setUploadPercent] = useState<number | null>(null)
  const [uploadResult, setUploadResult] = useState<VnfUploadResult | null>(null)
  const [message, setMessage] = useState('')
  const latestRun = latest.data && 'run_uid' in latest.data ? latest.data : null

  function startRun() {
    const normalized = Math.min(10, Math.max(1, Math.round(dayRange)))
    setDayRange(normalized)
    if (!window.confirm(`Trigger FIRMS monitoring for ${normalized} day${normalized === 1 ? '' : 's'}?`)) return
    setMessage('')
    trigger.mutate(normalized, { onSuccess: () => setMessage('Monitoring completed and dashboard data was refreshed.'), onError: (error) => setMessage(`Monitoring failed: ${error.message}`) })
  }

  function startUpload() {
    if (!file) { setMessage('Choose a CSV file first.'); return }
    if (!file.name.toLowerCase().endsWith('.csv') && file.type !== 'text/csv') { setMessage('Only CSV files can be uploaded.'); return }
    setMessage(''); setUploadResult(null); setUploadPercent(0)
    upload.mutate({ file, onProgress: setUploadPercent }, {
      onSuccess: (result) => { setUploadResult(result); setMessage('VNF processing completed and affected dashboard data was refreshed.') },
      onError: (error) => setMessage(`Upload failed: ${error.message}`),
    })
  }

  return <div className="mx-auto max-w-6xl space-y-6 pb-12">
    <header className="border-b-2 border-text-primary pb-5"><p className="text-[10px] font-black uppercase tracking-[0.2em] text-text-secondary">System and model telemetry</p><h1 className="mt-1 text-2xl font-black uppercase">Pipeline operations</h1><p className="mt-1 text-xs text-text-secondary">Run FIRMS monitoring, process VNF CSV data, and review execution history.</p></header>

    <section className="border-2 border-text-primary bg-surface p-5" aria-labelledby="latest-run-heading"><div className="flex items-center gap-2 border-b-2 border-text-primary pb-3"><Activity size={18} /><h2 id="latest-run-heading" className="text-sm font-black uppercase">Latest monitoring run</h2></div>{latest.isLoading && <div className="mt-4 h-24 animate-pulse bg-text-primary/10" />}{latest.isError && <ErrorState label="Latest run could not be loaded." retry={() => latest.refetch()} />}{latest.data && 'message' in latest.data && <p className="mt-4 text-xs text-text-secondary">{latest.data.message}</p>}{latestRun && <div className="mt-4"><RunSummary run={latestRun} />{latestRun.error_message && <p className="mt-3 text-xs font-bold text-danger">{latestRun.error_message}</p>}</div>}</section>

    <div className="grid gap-6 lg:grid-cols-2">
      <section className="border-2 border-text-primary bg-surface p-5"><h2 className="text-sm font-black uppercase">Trigger FIRMS monitoring</h2><p className="mt-1 text-xs text-text-secondary">Choose 1 to 10 days. Confirmation is required before the request begins.</p><label className="mt-4 block text-[10px] font-black uppercase text-text-secondary">Day range<input type="number" min="1" max="10" value={dayRange} onChange={(event) => setDayRange(Number(event.target.value))} className="mt-1 block w-28 border-2 border-black bg-surface px-3 py-2 text-xs font-bold text-text-primary" /></label><button type="button" disabled={trigger.isPending} onClick={startRun} className="mt-4 inline-flex items-center gap-2 border-2 border-black bg-black px-4 py-2 text-xs font-black uppercase text-white disabled:cursor-not-allowed disabled:opacity-50 dark:bg-[#d8f5a9] hover:bg-[#d8f5a9]/50 dark:text-black cursor-pointer transition-colors"><Play size={14} />{trigger.isPending ? 'Monitoring in progress…' : 'Run monitoring'}</button>{trigger.data && <div className="mt-4 border-2 border-text-primary p-3"><h3 className="text-[10px] font-black uppercase text-text-secondary">Returned execution summary</h3><pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs">{JSON.stringify(trigger.data, null, 2)}</pre></div>}</section>

      <section className="border-2 border-text-primary bg-surface p-5"><h2 className="text-sm font-black uppercase">Upload VNF CSV</h2><p className="mt-1 text-xs text-text-secondary">The selected CSV is uploaded as multipart field <code>file</code>, then processed by the system intelligence engine.</p><input ref={inputRef} type="file" accept=".csv,text/csv" className="sr-only" onChange={(event) => { setFile(event.target.files?.[0] ?? null); setUploadResult(null); setUploadPercent(null) }} /><div className="mt-4 flex flex-wrap items-center gap-3"><button type="button" onClick={() => inputRef.current?.click()} className="inline-flex items-center gap-2 border-2 border-black px-3 py-2 text-xs font-black uppercase"><FolderOpen size={14} />Choose CSV</button><span className="max-w-64 truncate font-mono text-xs text-text-secondary">{file?.name ?? 'No file chosen'}</span><button type="button" disabled={!file || upload.isPending} onClick={startUpload} className="inline-flex items-center gap-2 border-2 border-black bg-[#d8f5a9] px-4 py-2 text-xs font-black uppercase text-black disabled:opacity-40"><Upload size={14} />{upload.isPending ? uploadPercent === 100 ? 'Processing…' : 'Uploading…' : 'Upload and process'}</button></div>{upload.isPending && <div className="mt-4" role="status"><div className="flex justify-between text-[10px] font-black uppercase"><span>{uploadPercent === 100 ? 'System processing' : 'Upload progress'}</span><span>{uploadPercent ?? 0}%</span></div><div className="mt-1 h-3 border-2 border-black bg-text-primary/10"><div className="h-full bg-[#d8f5a9]" style={{ width: `${uploadPercent ?? 0}%` }} /></div></div>}{uploadResult && <div className="mt-4 border-2 border-text-primary p-3"><h3 className="text-[10px] font-black uppercase text-text-secondary">Processing summary</h3><dl className="mt-2 grid grid-cols-2 gap-2 text-xs">{Object.entries(uploadResult).filter(([, value]) => typeof value !== 'object').map(([key, value]) => <div key={key}><dt className="text-[10px] font-bold uppercase text-text-secondary">{key.replaceAll('_', ' ')}</dt><dd className="font-mono font-bold">{show(value as string | number | null)}</dd></div>)}</dl></div>}</section>
    </div>

    {message && <p role="status" className={`border-2 p-3 text-xs font-bold ${message.includes('failed') || message.includes('Only') ? 'border-danger text-danger' : 'border-text-primary bg-[#d8f5a9] text-black'}`}>{message}</p>}

    <section className="overflow-hidden border-2 border-text-primary bg-surface" aria-labelledby="run-history-heading"><div className="border-b-2 border-text-primary p-4"><h2 id="run-history-heading" className="text-sm font-black uppercase">Run history</h2><p className="text-xs text-text-secondary">Latest 20 monitoring executions</p></div>{history.isLoading && <div className="m-4 h-24 animate-pulse bg-text-primary/10" />}{history.isError && <ErrorState label="Run history could not be loaded." retry={() => history.refetch()} />}{history.data?.runs.length === 0 && <p className="p-6 text-xs text-text-secondary">No run history is available.</p>}{history.data && history.data.runs.length > 0 && <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-xs"><thead className="bg-black text-white"><tr><th className="p-3">Run</th><th className="p-3">Status</th><th className="p-3">Started</th><th className="p-3">Fetched</th><th className="p-3">Inserted</th><th className="p-3">Matched</th><th className="p-3">Alerts</th></tr></thead><tbody className="divide-y divide-text-primary/15">{history.data.runs.map((run) => <tr key={run.run_uid}><td className="p-3 font-mono">{run.run_uid}</td><td className="p-3 font-black">{run.status}</td><td className="p-3">{time(run.started_at)}</td><td className="p-3">{show(run.fetched)}</td><td className="p-3">{show(run.inserted)}</td><td className="p-3">{show(run.matched)}</td><td className="p-3">{show(run.alerts_created)}</td></tr>)}</tbody></table></div>}</section>
  </div>
}

function Stat({ label, value }: { label: string; value: string }) { return <div className="border-2 border-text-primary p-3"><p className="text-[10px] font-black uppercase text-text-secondary">{label}</p><p className="mt-1 break-words font-mono text-xs font-black">{value}</p></div> }
function ErrorState({ label, retry }: { label: string; retry: () => unknown }) { return <div className="m-4 text-center"><p className="text-xs font-bold text-danger">{label}</p><button type="button" onClick={retry} className="mt-2 border-2 border-black px-3 py-1 text-xs font-black uppercase">Retry</button></div> }
