import { useMemo } from 'react'
import { Layers, CheckSquare, Square, Eye, EyeOff, RefreshCw, CheckCircle, SlidersHorizontal } from 'lucide-react'
import { useKPISummary } from '../services/kpiService'
import { useSourceStore } from '../stores/sourceStore'

export default function DataLayersPage() {
  const { data: summary, refetch } = useKPISummary()
  const activeLayerIds = useSourceStore((s) => s.activeLayerIds)
  const toggleLayerId = useSourceStore((s) => s.toggleLayerId)
  const setAllLayers = useSourceStore((s) => s.setAllLayers)

  const layers = useMemo(() => [
    { id: 'firms', name: 'NASA FIRMS VIIRS Thermal Detections', provider: 'NASA LANCE / VIIRS', resolution: '375m', type: 'Point Vector', telemetry: `${summary?.firmsDetections ?? 0} active detections fetched` },
    { id: 'persistent', name: 'Persistent Thermal Object Registry', provider: 'AGNI DRISHTI Core Engine', resolution: '100m', type: 'Clustered Halo Dots', telemetry: `${summary?.thermalObjects ?? 0} thermal objects registered` },
    { id: 'modis', name: 'MODIS Thermal Anomaly Feed', provider: 'NASA Terra / Aqua MODIS', resolution: '1000m', type: 'Raster Heatmap', telemetry: `${summary?.unmatchedFirms ?? 0} unmatched observations logged` },
    { id: 'facilities', name: 'Industrial Facility Proximity Layer', provider: 'OpenStreetMap / GEM Infrastructure', resolution: '50m', type: 'Infrastructure Mesh', telemetry: `${summary?.matchedFirms ?? 0} matched industrial sources` },
  ], [summary])

  const enableAll = () => setAllLayers(layers.map((l) => l.id))
  const disableAll = () => setAllLayers([])

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-text-secondary">GEOSPATIAL LAYERS & OVERLAYS</span>
          <h1 className="text-2xl font-black tracking-tight uppercase text-text-primary">Data Layers & Satellite Feeds</h1>
          <p className="mt-1 text-xs font-semibold text-text-secondary">Control active GIS raster and vector overlays dynamically synced across map engines.</p>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={enableAll} className="border-2 border-text-primary bg-[#d8f5a9] px-3 py-1.5 text-xs font-black uppercase text-black hover:bg-[#c9f090] cursor-pointer flex items-center gap-1"><CheckCircle size={13} /> Enable All</button>
          <button type="button" onClick={disableAll} className="border-2 border-text-primary bg-surface px-3 py-1.5 text-xs font-black uppercase text-text-primary hover:bg-black hover:text-white dark:hover:bg-zinc-800 cursor-pointer flex items-center gap-1"><EyeOff size={13} /> Disable All</button>
          <button type="button" onClick={() => refetch()} className="border-2 border-text-primary bg-surface p-1.5 text-text-primary hover:bg-black hover:text-white dark:hover:bg-zinc-800 cursor-pointer" title="Refresh Telemetry Feeds"><RefreshCw size={15} /></button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-4">
        {[
          { label: 'Total Objects Registered', val: summary?.thermalObjects ?? 0 },
          { label: 'Matched FIRMS Sources', val: summary?.matchedFirms ?? 0 },
          { label: 'Unmatched Detections', val: summary?.unmatchedFirms ?? 0 },
          { label: 'Active Layers Enabled', val: `${activeLayerIds.length} / ${layers.length}` },
        ].map((kpi) => (
          <div key={kpi.label} className="border-2 border-text-primary bg-surface p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] dark:shadow-[3px_3px_0px_0px_rgba(216,245,169,0.2)]">
            <p className="text-xs font-black uppercase text-text-secondary">{kpi.label}</p>
            <p className="mt-1 font-mono text-2xl font-black text-text-primary">{kpi.val}</p>
          </div>
        ))}
      </div>

      <div className="border-2 border-text-primary bg-surface shadow-sm">
        <div className="flex items-center justify-between px-4 py-3 border-b-2 border-text-primary">
          <h2 className="flex items-center gap-2 text-sm font-black tracking-wider uppercase text-text-primary"><Layers size={18} /> Active Layer Registry</h2>
          <span className="font-mono text-xs font-bold uppercase text-emerald-600 dark:text-emerald-400">● LIVE MAP ENGINE SYNC</span>
        </div>
        <div className="divide-y divide-text-primary/20">
          {layers.map((layer) => {
            const active = activeLayerIds.includes(layer.id)
            return (
              <div key={layer.id} className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                <div className="flex items-start gap-3">
                  <button type="button" onClick={() => toggleLayerId(layer.id)} className="mt-0.5 text-text-primary cursor-pointer" aria-label={`Toggle ${layer.name}`}>
                    {active ? <CheckSquare size={20} className="fill-[#d8f5a9] text-black" /> : <Square size={20} />}
                  </button>
                  <div>
                    <h3 className="text-xs font-black uppercase text-text-primary">{layer.name}</h3>
                    <p className="mt-1 font-mono text-[11px] font-bold text-text-secondary">
                      Provider: {layer.provider} · Res: {layer.resolution} · Format: {layer.type} · <span className="text-text-primary font-black">{layer.telemetry}</span>
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`border-2 border-text-primary px-2 py-0.5 font-mono text-[10px] font-black uppercase ${active ? 'bg-[#d8f5a9] text-black' : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'}`}>{active ? 'LAYER ONLINE' : 'LAYER OFF'}</span>
                  <button type="button" onClick={() => toggleLayerId(layer.id)} className={`flex items-center gap-1 border-2 border-text-primary px-3 py-1 text-xs font-black uppercase transition-colors cursor-pointer ${active ? 'bg-surface text-text-primary hover:bg-black hover:text-white dark:hover:bg-[#d8f5a9] dark:hover:text-black' : 'bg-[#d8f5a9] text-black hover:bg-[#c9f090]'}`}>
                    {active ? <EyeOff size={12} /> : <Eye size={12} />} {active ? 'Disable' : 'Enable'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="border-2 border-text-primary bg-bg/50 p-4 text-xs font-bold text-text-secondary flex items-center gap-2">
        <SlidersHorizontal size={16} className="shrink-0 text-text-primary" />
        <span>Toggling layers updates spatial overlays in real-time across the main Dashboard map and Satellite Context viewer.</span>
      </div>
    </div>
  )
}
