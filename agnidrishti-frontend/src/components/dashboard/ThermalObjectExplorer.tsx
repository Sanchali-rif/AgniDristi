import { useMemo } from 'react'
import { ChevronLeft, ChevronRight, Database, Flame, Radar } from 'lucide-react'
import { useDashboardMap, useThermalObjects } from '../../services/dashboardService'
import { useFilterStore } from '../../stores/filterStore'
import { useSourceStore } from '../../stores/sourceStore'
import type { MapDatasetMode } from '../../pages/DashboardPage'
import { ThermalMap } from '../map/ThermalMap'

const fieldClass = 'mt-1 w-full border-2 border-black dark:border-zinc-700 bg-surface px-3 py-2 text-xs font-bold text-text-primary outline-none focus:ring-2 focus:ring-text-primary'
const display = (value: string | number | null | undefined, suffix = '') => value == null || value === '' ? 'Not available' : `${value}${suffix}`
const isLikelyFlare = (object: { gas_flare_likelihood?: string | null }) => object.gas_flare_likelihood === 'LIKELY'

type ThermalObjectExplorerProps = {
  requestedDate: string | null
  selectedDate: string | null
  datasetMode: MapDatasetMode
  onDatasetModeChange: (mode: MapDatasetMode) => void
}

export function ThermalObjectExplorer({ requestedDate, selectedDate, datasetMode, onDatasetModeChange }: ThermalObjectExplorerProps) {
  const filters = useFilterStore()
  const openPanel = useSourceStore((state) => state.openPanel)
  const mapQuery = useDashboardMap(requestedDate, 'all', 0)
  const persistentObjectsQuery = useThermalObjects({ limit: 5_000, offset: 0, gas_flare_only: filters.likelyFlaresOnly })
  const mapData = mapQuery.data
  const allKnownObjects = useMemo(() => mapData?.objects ?? [], [mapData?.objects])
  const persistentFirms = useMemo(
    () => mapQuery.isPlaceholderData
      ? []
      : (mapData?.firms ?? []).filter((detection) => detection.known_source === true && Boolean(detection.matched_object_uid)),
    [mapData?.firms, mapQuery.isPlaceholderData],
  )
  const associatedObjectUids = useMemo(
    () => new Set(persistentFirms.map((detection) => detection.matched_object_uid)),
    [persistentFirms],
  )
  const vnfObjects = useMemo(
    () => persistentObjectsQuery.isPlaceholderData ? [] : persistentObjectsQuery.data?.objects ?? [],
    [persistentObjectsQuery.data?.objects, persistentObjectsQuery.isPlaceholderData],
  )
  const visibleObjects = useMemo(
    () => {
      const vnfFallbackObjects = vnfObjects.length > 0 ? vnfObjects : allKnownObjects
      const objects = datasetMode === 'firms' ? allKnownObjects.filter((object) => associatedObjectUids.has(object.object_uid)) : vnfFallbackObjects
      if (!filters.likelyFlaresOnly) return objects
      return objects.filter(isLikelyFlare)
    },
    [allKnownObjects, associatedObjectUids, datasetMode, filters.likelyFlaresOnly, vnfObjects],
  )
  const classificationOptions = useMemo(() => {
    const counts = new Map<string, number>()
    visibleObjects.forEach((object) => {
      const label = (object.classification_label || object.industry_name || 'Unknown').trim() || 'Unknown'
      counts.set(label, (counts.get(label) ?? 0) + 1)
    })
    return [...counts.entries()]
      .map(([label, count]) => ({ label, count }))
      .sort((left, right) => left.label.localeCompare(right.label))
  }, [visibleObjects])
  const allObjects = useMemo(() => {
    const requestedClassification = filters.classification.trim().toLocaleLowerCase()
    return visibleObjects.filter((object) => {
      if (!requestedClassification) return true
      const objectClassification = (object.classification_label || object.industry_name || 'Unknown').trim().toLocaleLowerCase()
      return objectClassification === requestedClassification
    })
  }, [visibleObjects, filters.classification])
  const objects = useMemo(() => allObjects.slice(filters.objectOffset, filters.objectOffset + filters.objectLimit), [allObjects, filters.objectOffset, filters.objectLimit])
  const filteredObjectUids = useMemo(() => new Set(allObjects.map((object) => object.object_uid)), [allObjects])
  const mapFirms = useMemo(
    () => persistentFirms.filter((detection) => detection.matched_object_uid && filteredObjectUids.has(detection.matched_object_uid)),
    [filteredObjectUids, persistentFirms],
  )
  const total = allObjects.length
  const canNext = filters.objectOffset + filters.objectLimit < total
  const activeLoading = datasetMode === 'vnf' ? persistentObjectsQuery.isLoading && vnfObjects.length === 0 && allKnownObjects.length === 0 : mapQuery.isLoading
  const activeError = datasetMode === 'vnf' ? persistentObjectsQuery.isError : mapQuery.isError
  const reset = () => { filters.reset(); onDatasetModeChange('firms') }

  return (
    <div className="space-y-4">
      <section className="p-4 border-2 border-text-primary bg-surface" aria-label="Thermal object filters">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <label className="text-[10px] font-black uppercase tracking-wider text-text-secondary">Industry classification
            <select className={fieldClass} value={filters.classification} onChange={(event) => { filters.setClassification(event.target.value); filters.setObjectOffset(0) }}><option value="">All classifications</option>{classificationOptions.map((entry) => <option key={entry.label} value={entry.label}>{entry.label} ({entry.count})</option>)}</select>
          </label>
          <label className="flex min-h-14 cursor-pointer items-center justify-center gap-2 border-2 border-black bg-surface px-3 text-xs font-black uppercase text-text-primary hover:bg-black hover:text-white dark:border-zinc-700 dark:hover:bg-[#d8f5a9] dark:hover:text-black">
            <input
              type="checkbox"
              checked={filters.likelyFlaresOnly}
              onChange={(event) => { filters.setLikelyFlaresOnly(event.target.checked); filters.setObjectOffset(0) }}
              className="h-4 w-4 accent-black"
            />
            <Flame size={15} />
            Likely gas flares only
          </label>
          <button type="button" aria-pressed={datasetMode === 'vnf'} onClick={() => { onDatasetModeChange(datasetMode === 'firms' ? 'vnf' : 'firms'); filters.setObjectOffset(0) }} className="flex min-h-14 items-center justify-center gap-2 border-2 border-black bg-surface px-3 text-xs font-black uppercase text-text-primary hover:bg-black hover:text-white dark:border-zinc-700 dark:hover:bg-[#d8f5a9] dark:hover:text-black">{datasetMode === 'firms' ? <Database size={15} /> : <Radar size={15} />}{datasetMode === 'firms' ? 'View VNF data' : `View FIRMS for ${selectedDate ?? 'selected date'}`}</button>
          <button type="button" onClick={reset} className="min-h-14 border-2 border-black bg-black px-4 text-xs font-black uppercase text-white dark:bg-[#d8f5a9] dark:text-black hover:bg-[#d8f5a9]/50 transition-colors cursor-pointer">Reset filters</button>
        </div>
      </section>

      <ThermalMap
        objects={allObjects}
        detections={datasetMode === 'firms' ? mapFirms : []}
        vnfDetections={[]}
        datasetMode={datasetMode}
        isLoading={activeLoading}
        error={activeError}
        onRetry={() => { void mapQuery.refetch(); if (datasetMode === 'vnf') void persistentObjectsQuery.refetch() }}
      />

      <section className="overflow-hidden border-2 border-text-primary bg-surface" aria-labelledby="thermal-object-list-heading">
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-b-2 border-text-primary"><div><h3 id="thermal-object-list-heading" className="text-sm font-black uppercase">Thermal object list</h3><p className="text-xs text-text-secondary">Showing {objects.length} on this page, {total} spatial matches</p></div><label className="text-[10px] font-black uppercase text-text-secondary">Rows<select value={filters.objectLimit} onChange={(event) => { filters.setObjectLimit(Number(event.target.value)); filters.setObjectOffset(0) }} className="p-1 ml-2 text-xs border-2 border-black bg-surface text-text-primary"><option value={10}>10</option><option value={25}>25</option><option value={50}>50</option><option value={100}>100</option></select></label></div>
        {activeLoading && <div className="p-4 space-y-2" role="status"><div className="h-9 animate-pulse bg-text-primary/10" /><div className="h-9 animate-pulse bg-text-primary/10" /><span className="sr-only">Loading thermal objects</span></div>}
        {activeError && <div className="p-6 text-center"><p className="text-sm font-bold text-danger">{datasetMode === 'vnf' ? 'Persistent clusters could not be loaded.' : 'Thermal objects could not be loaded.'}</p><button type="button" onClick={() => { if (datasetMode === 'vnf') void persistentObjectsQuery.refetch(); else void mapQuery.refetch() }} className="mt-3 border-2 border-black bg-black px-3 py-1.5 text-xs font-black uppercase text-white">Retry</button></div>}
        {!activeLoading && !activeError && objects.length === 0 && <div className="p-8 text-center"><p className="text-sm font-black uppercase">No objects match these filters</p><p className="mt-1 text-xs text-text-secondary">Clear one or more filters to broaden the result.</p><button type="button" onClick={reset} className="mt-3 border-2 border-black px-3 py-1.5 text-xs font-black uppercase">Clear filters</button></div>}
        {objects.length > 0 && <div className="overflow-x-auto"><table className="w-full min-w-[820px] text-left text-xs"><thead className="text-white bg-black dark:bg-zinc-800"><tr><th className="p-3">Object</th><th className="p-3">Classification</th><th className="p-3">Temporal source</th><th className="p-3">Flare assessment</th><th className="p-3">Temperature</th><th className="p-3">Coordinates</th></tr></thead><tbody className="divide-y divide-text-primary/15">{objects.map((object) => <tr key={object.object_uid} role="button" tabIndex={0} aria-label={`Open details for ${object.object_uid}`} onClick={() => openPanel(object.object_uid)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openPanel(object.object_uid) } }} className="cursor-pointer hover:bg-bg/40 focus:bg-bg/40 focus:outline focus:outline-2 focus:outline-offset-[-2px]"><td className="p-3 font-mono font-black underline decoration-2 underline-offset-2">{object.object_uid}</td><td className="p-3">{display(object.classification_label)}<span className="block text-[10px] text-text-secondary">Confidence: {object.confidence == null ? 'Not available' : `${Math.round(object.confidence * 100)}%`}</span></td><td className="p-3">{display(object.temporal_source_hint)}</td><td className="p-3"><span className={`font-black ${object.gas_flare_likelihood === 'LIKELY' ? 'text-red-600' : object.gas_flare_likelihood === 'POSSIBLE' ? 'text-warning' : 'text-info'}`}>{display(object.gas_flare_likelihood)}</span><span className="block text-[10px] text-text-secondary">Score: {object.gas_flare_score == null ? 'Not available' : `${Math.round(object.gas_flare_score * 100)}%`}</span></td><td className="p-3">Mean {display(object.temp_mean, ' K')}<span className="block text-[10px] text-text-secondary">Max {display(object.temp_max, ' K')}</span></td><td className="p-3 font-mono">{object.latitude.toFixed(4)}, {object.longitude.toFixed(4)}</td></tr>)}</tbody></table></div>}
        <div className="flex items-center justify-between p-3 border-t-2 border-text-primary"><button type="button" disabled={filters.objectOffset === 0} onClick={() => filters.setObjectOffset(Math.max(0, filters.objectOffset - filters.objectLimit))} className="inline-flex items-center gap-1 border-2 border-black px-3 py-1.5 text-xs font-black uppercase disabled:opacity-40 cursor-pointer transition-colors hover:bg-[#000000]/70"><ChevronLeft size={14} /> Previous</button><span className="font-mono text-xs font-bold">Page {Math.floor(filters.objectOffset / filters.objectLimit) + 1} of {Math.ceil(total / filters.objectLimit) || 1} ({total === 0 ? 0 : filters.objectOffset + 1}–{Math.min(total, filters.objectOffset + filters.objectLimit)} of {total})</span><button type="button" disabled={!canNext} onClick={() => filters.setObjectOffset(filters.objectOffset + filters.objectLimit)} className="inline-flex items-center gap-1 border-2 border-black bg-black px-3 py-1.5 text-xs font-black uppercase text-white disabled:opacity-40 cursor-pointer transition-colors hover:bg-[#000000]/70">Next <ChevronRight size={14} /></button></div>
      </section>
    </div>
  )
}
