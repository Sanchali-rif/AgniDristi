import { useState } from 'react'
import { useFilterStore } from '../../stores/filterStore'
import { FilterInput, FilterSelect } from './FilterFields'

const sourceTypes: [string, string][] = [
  ['industrial', 'Industrial'], ['persistent', 'Persistent'], ['new', 'New'],
  ['abnormal', 'Abnormal'], ['natural_biomass', 'Natural / Biomass'],
  ['gas_flare', 'Gas Flare'], ['unknown', 'Unknown'],
]

const anomalyOptions: [string, string][] = [['low', 'Low'], ['medium', 'Medium'], ['high', 'High']]
const persistOptions: [string, string][] = [['persistent', 'Persistent'], ['new', 'New'], ['transient', 'Transient']]

export function FilterPanel() {
  const filters = useFilterStore()
  const [d, setD] = useState({
    sourceId: filters.sourceId, location: filters.location, facility: filters.facility,
    from: filters.dateRange.from, to: filters.dateRange.to, sourceType: filters.sourceType,
    industryType: filters.industryType, anomalyLevel: filters.anomalyLevel,
    confidenceLevel: filters.confidenceLevel, persistenceStatus: filters.persistenceStatus,
  })

  const u = (field: keyof typeof d) => (v: string) => setD((c) => ({ ...c, [field]: v }))

  function apply() {
    filters.setSourceId(d.sourceId); filters.setLocation(d.location); filters.setFacility(d.facility)
    filters.setDateRange({ from: d.from, to: d.to }); filters.setSourceType(d.sourceType)
    filters.setIndustryType(d.industryType); filters.setAnomalyLevel(d.anomalyLevel)
    filters.setConfidenceLevel(d.confidenceLevel); filters.setPersistenceStatus(d.persistenceStatus)
  }

  function reset() {
    filters.reset()
    setD({ sourceId: '', location: '', facility: '', from: '', to: '', sourceType: '', industryType: '', anomalyLevel: '', confidenceLevel: '', persistenceStatus: '' })
  }

  return (
    <section className="rounded-none border-2 border-black bg-surface p-5 shadow-sm" aria-label="Source filters">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b-2 border-black pb-3">
        <div>
          <h2 className="text-base font-black uppercase tracking-wider text-text-primary">Search &amp; Filters</h2>
          <p className="mt-0.5 text-xs text-text-secondary font-medium">Narrow down spatial objects and filter query parameters</p>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={reset} className="rounded-none border-2 border-black bg-surface px-3.5 py-1.5 text-xs font-black uppercase text-text-primary hover:bg-zinc-100 transition-colors">Reset</button>
          <button type="button" onClick={apply} className="rounded-none border-2 border-black bg-black px-4 py-1.5 text-xs font-black uppercase text-white hover:bg-zinc-800 transition-colors">Apply Filters</button>
        </div>

      </div>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <FilterInput label="Source ID" value={d.sourceId} onChange={u('sourceId')} placeholder="AGNI-IND-004821" colSpan />
        <FilterInput label="Location" value={d.location} onChange={u('location')} placeholder="District or state" />
        <FilterInput label="Facility" value={d.facility} onChange={u('facility')} placeholder="Facility name" />
        <FilterInput label="From" value={d.from} onChange={u('from')} type="date" />
        <FilterInput label="To" value={d.to} onChange={u('to')} type="date" />
        <FilterSelect label="Source type" value={d.sourceType} onChange={u('sourceType')} options={sourceTypes} allLabel="All source types" />
        <FilterInput label="Industry type" value={d.industryType} onChange={u('industryType')} placeholder="e.g. Steel Plant" />
        <FilterSelect label="Anomaly level" value={d.anomalyLevel} onChange={u('anomalyLevel')} options={anomalyOptions} allLabel="Any anomaly level" />
        <label className="text-xs font-bold uppercase text-text-secondary">
          Confidence: {d.confidenceLevel ? `${d.confidenceLevel}% min` : 'Any'}
          <input type="range" min="0" max="100" step="1" value={d.confidenceLevel || '0'} onChange={(e) => u('confidenceLevel')(e.target.value === '0' ? '' : e.target.value)} className="mt-3 w-full accent-black" />
        </label>
        <FilterSelect label="Persistence" value={d.persistenceStatus} onChange={u('persistenceStatus')} options={persistOptions} />
      </div>
    </section>
  )
}

