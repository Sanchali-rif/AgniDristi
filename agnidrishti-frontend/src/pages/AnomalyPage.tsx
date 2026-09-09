import { useState } from 'react'
import { AlertCircle, ArrowRight, ShieldAlert, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getAlertTotal } from '../services/alertService'
import { useSources } from '../services/sourceService'

export default function AnomalyPage() {
  const [level, setLevel] = useState<string>('ALL')
  const { data: sources = [], isLoading: loadingSources } = useSources()

  const highCount = sources.filter((s) => s.anomalyLevel === 'high').length
  const medCount = sources.filter((s) => s.anomalyLevel === 'medium').length
  const alertCount = getAlertTotal()

  const filteredSources = sources.filter((s) => level === 'ALL' || s.anomalyLevel.toUpperCase() === level)

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-text-secondary">CHANGE & ANOMALY ANALYSIS</span>
        <h1 className="text-2xl font-black uppercase tracking-tight text-text-primary">Thermal Anomaly Intelligence</h1>
        <p className="mt-1 text-xs font-semibold text-text-secondary">Dynamic thermal output spikes and industrial anomaly detection telemetry.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="border-2 border-black dark:border-zinc-700 bg-surface p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
          <p className="flex items-center gap-1.5 text-xs font-black uppercase text-red-600 dark:text-red-400"><ShieldAlert size={16} /> High Risk Anomalies</p>
          <p className="mt-2 font-mono text-2xl font-black text-text-primary">{highCount}</p>
        </div>
        <div className="border-2 border-black dark:border-zinc-700 bg-surface p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
          <p className="flex items-center gap-1.5 text-xs font-black uppercase text-amber-600 dark:text-amber-400"><AlertCircle size={16} /> Moderate Anomalies</p>
          <p className="mt-2 font-mono text-2xl font-black text-text-primary">{medCount}</p>
        </div>
        <div className="border-2 border-black dark:border-zinc-700 bg-surface p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
          <p className="flex items-center gap-1.5 text-xs font-black uppercase text-text-primary"><TrendingUp size={16} /> Total Alerts Logged</p>
          <p className="mt-2 font-mono text-2xl font-black text-text-primary">{alertCount}</p>
        </div>
      </div>

      <div className="flex items-center justify-between border-b-2 border-text-primary pb-3">
        <h2 className="text-sm font-black uppercase tracking-wider text-text-primary">Detected Anomaly Sources ({filteredSources.length})</h2>
        <div className="flex gap-2">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
            <button key={lvl} type="button" onClick={() => setLevel(lvl)}
              className={`border-2 border-black dark:border-zinc-700 px-3 py-1 text-xs font-black uppercase transition-all ${level === lvl ? 'bg-black dark:bg-[#d8f5a9] text-white dark:text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]' : 'bg-surface text-text-primary hover:bg-black hover:text-white dark:hover:bg-zinc-800 dark:hover:text-white'}`}>
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {loadingSources && <p className="py-8 text-center text-xs font-bold uppercase text-text-secondary">Loading anomaly data...</p>}

      {!loadingSources && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredSources.map((s) => (
            <div key={s.id} className="border-2 border-black dark:border-zinc-700 bg-surface p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
              <div className="flex items-center justify-between border-b border-black/20 dark:border-zinc-700 pb-2">
                <span className="font-mono text-xs font-black text-text-primary">{s.id}</span>
                <span className={`border border-black px-2 py-0.5 font-mono text-[10px] font-black uppercase ${s.anomalyLevel === 'high' ? 'bg-red-600 text-white' : s.anomalyLevel === 'medium' ? 'bg-amber-500 text-black' : 'bg-zinc-200 text-black'}`}>
                  {s.anomalyLevel} risk
                </span>
              </div>
              <div className="mt-3 space-y-1 text-xs font-bold text-text-secondary">
                <p className="uppercase text-text-primary">{s.industrySubtype ?? 'Thermal Source'}</p>
                <p className="font-mono text-[11px] text-text-primary">{s.lat.toFixed(4)}° N, {s.lon.toFixed(4)}° E</p>
                <p className="text-[10px] uppercase font-semibold text-text-secondary">Confidence: <span className="text-text-primary font-bold">{s.confidence}%</span> · Status: <span className="text-text-primary font-bold">{s.status}</span></p>
              </div>
              <Link to={`/investigation/${encodeURIComponent(s.id)}`}
                className="mt-4 flex items-center justify-center gap-1.5 border-2 border-black bg-black dark:bg-[#d8f5a9] py-2 text-xs font-black uppercase text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-[#c9f090] transition-colors">
                Inspect Anomaly Telemetry <ArrowRight size={14} />
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
