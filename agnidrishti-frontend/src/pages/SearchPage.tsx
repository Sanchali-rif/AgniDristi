import { useState } from 'react'
import { ArrowRight, Filter, Search } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useSources } from '../services/sourceService'
import { useSourceStore } from '../stores/sourceStore'

export default function SearchPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [classification, setClassification] = useState('')
  const { data: sources = [], isLoading, isError } = useSources({ classification: classification || undefined })
  const openPanel = useSourceStore((s) => s.openPanel)

  const filtered = sources.filter((s) =>
    s.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (s.industrySubtype ?? '').toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-text-secondary">EXPLORER & DISCOVERY</span>
        <h1 className="text-2xl font-black uppercase tracking-tight text-text-primary">Search & Discovery</h1>
        <p className="mt-1 text-xs font-semibold text-text-secondary">Search thermal objects dynamically across satellite pipeline records.</p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
          <input type="text" placeholder="Search by Source UID or Classification..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full border-2 border-black bg-surface py-2 pl-9 pr-3 text-xs font-bold uppercase placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-black" />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-text-secondary" />
          <select value={classification} onChange={(e) => setClassification(e.target.value)}
            className="border-2 border-black bg-surface px-3 py-2 text-xs font-black uppercase focus:outline-none cursor-pointer focus:ring-2 focus:ring-black">
            <option value="">All Classifications</option>
            <option value="industrial">Industrial</option>
            <option value="biomass">Biomass / Natural</option>
            <option value="persistent">Persistent Thermal</option>
          </select>
        </div>
      </div>

      {isLoading && <p className="py-8 text-center text-xs font-bold uppercase text-text-secondary">Fetching thermal objects from satellite catalog...</p>}
      {isError && <p className="py-8 text-center text-xs font-bold text-danger uppercase">Unable to load search index.</p>}

      {!isLoading && !isError && (
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b-2 border-text-primary pb-2 text-xs font-black uppercase">
            <span>Query Results ({filtered.length})</span>
            <span className="text-text-secondary">Thermal Source Index</span>
          </div>
          {filtered.length === 0 ? (
            <div className="border-2 border-black dark:border-zinc-700 bg-surface p-8 text-center text-xs font-bold text-text-secondary">No matching thermal sources found.</div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((s) => (
                <div key={s.id} className="border-2 border-black dark:border-zinc-700 bg-surface p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-transform hover:-translate-y-0.5">
                  <div className="flex items-center justify-between border-b border-black/20 dark:border-zinc-700 pb-2">
                    <span className="font-mono text-xs font-black text-text-primary">{s.id}</span>
                    <span className="border border-black bg-[#d8f5a9] px-2 py-0.5 font-mono text-[10px] font-black uppercase text-black">{s.confidence}% CONF</span>
                  </div>
                  <div className="mt-3 space-y-1 text-xs font-bold text-text-secondary">
                    <p className="uppercase text-text-primary">{s.industrySubtype ?? 'Unclassified Thermal Source'}</p>
                    <p className="font-mono text-[11px] text-text-primary">{s.lat.toFixed(4)}° N, {s.lon.toFixed(4)}° E</p>
                    <p className="text-[10px] uppercase font-semibold text-text-secondary">Status: <span className="text-text-primary font-bold">{s.status}</span> · Anomaly: <span className="text-text-primary font-bold">{s.anomalyLevel}</span></p>
                  </div>
                  <div className="mt-4 flex items-center gap-2">
                    <button type="button" onClick={() => openPanel(s.id)}
                      className="flex-1 border-2 border-black dark:border-zinc-700 bg-zinc-200 dark:bg-zinc-800 py-1.5 text-center text-xs font-black uppercase text-black dark:text-white hover:bg-zinc-300 dark:hover:bg-zinc-700 cursor-pointer transition-colors">
                      Quick Snapshot
                    </button>
                    <Link to={`/investigation/${encodeURIComponent(s.id)}`}
                      className="flex items-center justify-center gap-1 border-2 border-black bg-black dark:bg-[#d8f5a9] px-3 py-1.5 text-xs font-black uppercase text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-[#c9f090] transition-colors">
                      View <ArrowRight size={12} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
