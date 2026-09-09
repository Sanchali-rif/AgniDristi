import { AnimatePresence, motion } from 'framer-motion'
import { ChevronLeft, ChevronRight, RotateCw, X } from 'lucide-react'
import { useThermalObjectDetail } from '../../services/dashboardService'
import { useSourceStore } from '../../stores/sourceStore'

const show = (value: string | number | boolean | null | undefined, suffix = '') => value == null || value === '' ? 'Not available' : `${typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value}${suffix}`
const percent = (value: number | null | undefined) => value == null ? 'Not available' : `${Math.round(value * 100)}%`
const reasonLabel = (reason: string) => reason.replaceAll('_', ' ').toLowerCase().replace(/^./, (letter) => letter.toUpperCase())
const sourceDescriptions: Record<string, string> = {
  GEM_OIL_GAS_AND_VNF: 'Supported by GEM oil and gas context and VNF thermal evidence.',
  GEM_NON_OIL_GAS_AND_VNF: 'GEM identifies another industry type.',
  VNF_HEURISTIC: 'Based only on thermal and temporal features.',
}

function Field({ label, value, suffix = '' }: { label: string; value: string | number | boolean | null | undefined; suffix?: string }) {
  return <div className="py-2"><dt className="text-[10px] font-black uppercase tracking-wider text-text-secondary">{label}</dt><dd className="mt-0.5 break-words font-mono text-xs font-bold text-text-primary">{show(value, suffix)}</dd></div>
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="border-t-2 border-text-primary pt-4"><h3 className="text-xs font-black uppercase tracking-widest">{title}</h3><dl className="mt-2 grid grid-cols-2 gap-x-4">{children}</dl></section>
}

export function SourceSnapshotPanel() {
  const selectedId = useSourceStore((state) => state.selectedSourceId)
  const isOpen = useSourceStore((state) => state.isPanelOpen)
  const collapsed = useSourceStore((state) => state.isPanelCollapsed)
  const toggleCollapse = useSourceStore((state) => state.togglePanelCollapse)
  const closePanel = useSourceStore((state) => state.closePanel)
  const query = useThermalObjectDetail(selectedId)

  const close = () => { closePanel(); requestAnimationFrame(() => document.querySelector<HTMLElement>('.leaflet-container')?.focus()) }
  if (!isOpen) return null

  return <AnimatePresence>{collapsed ? <motion.div initial={{ x: 50 }} animate={{ x: 0 }} exit={{ x: 50 }} className="fixed right-0 top-24 z-[1100] border-2 border-black bg-surface p-2 shadow-lg"><button type="button" onClick={toggleCollapse} aria-label="Expand object details" className="flex items-center gap-1 text-xs font-black uppercase"><ChevronLeft size={18} /><span className="max-w-40 truncate">{selectedId}</span></button></motion.div> :
    <motion.aside initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ type: 'tween', duration: 0.2 }} aria-label="Thermal object details" className="fixed inset-y-0 right-0 z-[1100] flex w-full max-w-2xl flex-col overflow-hidden border-2 border-text-primary bg-surface shadow-2xl">
      <div className="flex shrink-0 items-start justify-between gap-4 border-b-2 border-text-primary bg-surface p-5 pb-4"><div><p className="text-[10px] font-black uppercase tracking-widest text-text-secondary">Thermal object detail</p><h2 className="mt-1 break-all font-mono text-base font-black">{selectedId}</h2></div><div className="flex gap-1"><button type="button" onClick={toggleCollapse} aria-label="Collapse object details" className="border-2 border-text-primary p-1.5 hover:bg-black hover:text-white cursor-pointer"><ChevronRight size={18} /></button><button type="button" onClick={close} aria-label="Close object details" className="border-2 border-text-primary p-1.5 hover:bg-black hover:text-white cursor-pointer"><X size={18} /></button></div></div>

      <div className="source-panel-scroll flex-1 overflow-y-auto p-5">
        {query.isLoading && <div className="space-y-3" role="status"><div className="h-20 animate-pulse bg-text-primary/10" /><div className="h-40 animate-pulse bg-text-primary/10" /><span className="sr-only">Loading object details</span></div>}
        {query.isError && <div className="border-2 border-danger p-5 text-center"><p className="text-sm font-bold text-danger">Object details could not be loaded.</p><button type="button" onClick={() => query.refetch()} className="mt-3 inline-flex items-center gap-2 border-2 border-black bg-black px-3 py-1.5 text-xs font-black uppercase text-white cursor-pointer"><RotateCw size={13} /> Retry</button></div>}

        {query.data && (() => { const object = query.data; const flare = object.gas_flare_assessment; const evidence = flare?.evidence; return <div className="space-y-5">
          <Section title="Location"><Field label="Latitude" value={object.location.latitude} /><Field label="Longitude" value={object.location.longitude} /><Field label="Object radius" value={object.object_radius_m} suffix=" m" /><Field label="Stage 3 object ID" value={object.stage3_object_id} /></Section>
          <Section title="Industry classification"><Field label="Label" value={object.classification.label} /><Field label="Source" value={object.classification.source} /><Field label="Confidence" value={percent(object.classification.confidence)} /></Section>
          <Section title="Temporal behavior"><Field label="Detection count" value={object.temporal.detection_count} /><Field label="Active months" value={object.temporal.active_months} /><Field label="Persistence ratio" value={percent(object.temporal.persistence_ratio)} /><Field label="Source persistence" value={percent(object.temporal.source_persistence_ratio)} /><Field label="Longest active run" value={object.temporal.longest_active_run} /><Field label="Maximum inactive gap" value={object.temporal.max_inactive_gap} /><Field label="Source hint" value={object.temporal.source_hint} /><Field label="TCI" value={object.temporal.tci} /><Field label="Seasonal concentration" value={object.temporal.seasonal_concentration} /></Section>
          <Section title="Temperature statistics"><Field label="Mean" value={object.temperature.mean} suffix=" K" /><Field label="Median" value={object.temperature.median} suffix=" K" /><Field label="Minimum" value={object.temperature.min} suffix=" K" /><Field label="Maximum" value={object.temperature.max} suffix=" K" /><Field label="Standard deviation" value={object.temperature.std} suffix=" K" /><Field label="Range" value={object.temperature.range} suffix=" K" /><Field label="Coefficient of variation" value={object.temperature.cv} /></Section>
          <Section title="Emitting-area statistics"><Field label="Mean" value={object.area.mean} /><Field label="Standard deviation" value={object.area.std} /><Field label="Coefficient of variation" value={object.area.cv} /></Section>
          <Section title="Radiant heat"><Field label="Mean" value={object.radiant_heat.mean} /><Field label="Standard deviation" value={object.radiant_heat.std} /><Field label="Coefficient of variation" value={object.radiant_heat.cv} /></Section>
          <section className="border-t-2 border-text-primary pt-4"><h3 className="text-xs font-black uppercase tracking-widest">Gas-flare likelihood assessment</h3><p className="mt-1 text-xs text-text-secondary">This assessment is supporting evidence, not guaranteed proof of a gas flare.</p><dl className="mt-2 grid grid-cols-2 gap-x-4"><Field label="Likelihood" value={flare?.likelihood} /><Field label="Score" value={percent(flare?.score)} /><Field label="Candidate" value={flare?.candidate} /><Field label="Assessment source" value={flare?.source} /><Field label="GEM facility" value={evidence?.gem_facility_name} /><Field label="GEM exact industry type" value={evidence?.gem_industry_exact_type} /></dl>{flare?.source && <p className="mt-2 border-2 border-text-primary p-3 text-xs text-text-secondary">{sourceDescriptions[flare.source] ?? 'Assessment source reported by automated spatial analysis.'}</p>}{evidence?.reasons?.length ? <div className="mt-4"><h4 className="text-[10px] font-black uppercase text-text-secondary">Evidence reasons</h4><ul className="mt-2 list-inside list-disc text-xs">{evidence.reasons.map((reason) => <li key={reason}>{reasonLabel(reason)}</li>)}</ul></div> : <p className="mt-3 text-xs text-text-secondary">No detailed flare reasons or GEM evidence were supplied.</p>}{evidence && Object.keys(evidence.signal_contributions).length > 0 && <div className="mt-4 space-y-3"><h4 className="text-[10px] font-black uppercase text-text-secondary">Signal contributions</h4>{Object.entries(evidence.signal_contributions).map(([signal, raw]) => { const normalized = raw <= 1 ? raw * 100 : raw; const width = Math.max(0, Math.min(100, normalized)); return <div key={signal}><div className="flex justify-between text-[10px] font-bold"><span>{reasonLabel(signal)}</span><span>{Math.round(normalized)}%</span></div><div className="mt-1 h-2 border border-text-primary bg-text-primary/10"><div className="h-full bg-[#d8f5a9]" style={{ width: `${width}%` }} /></div></div> })}</div>}</section>
          <section className="border-t-2 border-text-primary pt-4"><h3 className="text-xs font-black uppercase tracking-widest">Recent FIRMS detections</h3>{object.recent_firms.length === 0 ? <p className="mt-3 text-xs text-text-secondary">No recent FIRMS detections are linked to this object.</p> : <div className="mt-3 overflow-x-auto"><table className="w-full min-w-[540px] text-left text-xs"><thead className="bg-black text-white"><tr><th className="p-2">Detection</th><th className="p-2">Acquired</th><th className="p-2">Temperature</th><th className="p-2">FRP</th><th className="p-2">Distance</th></tr></thead><tbody className="divide-y divide-text-primary/15">{object.recent_firms.map((detection) => <tr key={detection.firms_uid}><td className="p-2 font-mono">{detection.firms_uid}</td><td className="p-2">{show(detection.acq_date)} {show(detection.acq_time)}</td><td className="p-2">{show(detection.bright_ti4, ' K')}</td><td className="p-2">{show(detection.frp)}</td><td className="p-2">{show(detection.match_distance_km, ' km')}</td></tr>)}</tbody></table></div>}</section>
        </div> })()}
      </div>
    </motion.aside>}
</AnimatePresence>
}
