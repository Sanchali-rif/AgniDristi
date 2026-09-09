import { useMemo, useState } from 'react'
import { Flame, Radar, ScanSearch, Zap } from 'lucide-react'
import { KPICard } from '../components/kpi/KPICard'
import { SectionHeading } from '../components/common/SectionHeading'
import { IndustryDistributionChart } from '../components/dashboard/IndustryDistributionChart'
import { RecentAlertsWidget } from '../components/dashboard/RecentAlertsWidget'
import { ThermalObjectExplorer } from '../components/dashboard/ThermalObjectExplorer'
import { useDashboardMap, useMapDates } from '../services/dashboardService'

export type MapDatasetMode = 'firms' | 'vnf'

export default function DashboardPage() {
  const datesQuery = useMapDates(30)
  const [requestedDate, setRequestedDate] = useState<string | null>(null)
  const [datasetMode, setDatasetMode] = useState<MapDatasetMode>('firms')
  const mapQuery = useDashboardMap(requestedDate, 'all', 0)
  const mapData = mapQuery.data
  const availableDates = datesQuery.data?.dates ?? []
  const selectedDate = requestedDate ?? mapData?.selected_date ?? availableDates[0]?.date ?? null
  const matchedObjectCount = useMemo(
    () => new Set((mapData?.firms ?? []).map((detection) => detection.matched_object_uid).filter(Boolean)).size,
    [mapData?.firms],
  )
  const cards = [
    { label: 'FIRMS detections', value: mapData?.counts.firms, icon: Radar },
    { label: 'Matched FIRMS', value: mapData?.counts.matched_firms, icon: ScanSearch },
    { label: 'Unmatched FIRMS', value: mapData?.counts.unmatched_firms, icon: Zap },
    { label: 'Matched objects', value: matchedObjectCount, icon: Flame },
  ]

  return (
    <div className="space-y-9 pb-12">
      <header className="flex flex-wrap items-end justify-between gap-4 border-b-2 border-text-primary pb-5">
        <div><div className="inline-flex items-center gap-2 border-2 border-black bg-black px-3 py-1 text-[11px] font-black uppercase tracking-widest text-[#d8f5a9]"><span className="h-2 w-2 bg-[#d8f5a9]" />System intelligence</div><h1 className="mt-3 text-3xl font-black uppercase tracking-[0.12em] text-text-primary sm:text-4xl">Thermal source intelligence</h1><p className="mt-2 text-xs font-bold uppercase tracking-widest text-text-secondary">Telemetry thermal objects, FIRMS detections, and flare assessments</p></div>
        {mapQuery.isFetching && <span role="status" className="text-xs font-black uppercase text-text-secondary">Refreshing...</span>}
      </header>

      <section aria-label="Selected-date operational summary">
        <SectionHeading num="01" title="Operational summary" subtitle={selectedDate ? `FIRMS activity for ${selectedDate}` : 'Selected-date FIRMS activity'} />
        <div className="mb-4 -mt-2 flex justify-end">
          <label className="text-[10px] font-black uppercase tracking-wider text-text-secondary">Observation date
            <select
              value={selectedDate ?? ''}
              disabled={datesQuery.isLoading || datesQuery.isError || availableDates.length === 0}
              onChange={(event) => setRequestedDate(event.target.value || null)}
              className="ml-2 border-2 border-black bg-surface px-3 py-2 font-mono text-xs font-bold text-text-primary outline-none focus:ring-2 focus:ring-text-primary"
            >
              {datesQuery.isLoading && <option value="">Loading dates...</option>}
              {datesQuery.isError && <option value="">Dates unavailable</option>}
              {!datesQuery.isLoading && !datesQuery.isError && availableDates.length === 0 && <option value="">No FIRMS dates</option>}
              {availableDates.map((entry) => <option key={entry.date} value={entry.date}>{entry.date} | {entry.firms_count} hits</option>)}
            </select>
          </label>
        </div>
        {mapQuery.isError ? <div className="border-2 border-black bg-surface p-5"><p className="text-sm font-bold text-danger">Selected-date summary could not be loaded.</p><button type="button" onClick={() => { void mapQuery.refetch() }} className="mt-3 border-2 border-black bg-black px-3 py-1.5 text-xs font-black uppercase text-white">Retry</button></div> : <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{cards.map((card) => <KPICard key={card.label} label={card.label} value={mapQuery.isLoading ? '...' : card.value ?? 'Not available'} icon={card.icon} />)}</div>}
      </section>

      <section aria-label="Spatial object explorer"><SectionHeading num="02" title="Spatial object explorer" subtitle="Switch between selected-date FIRMS matches and VNF source history" /><ThermalObjectExplorer requestedDate={requestedDate} selectedDate={selectedDate} datasetMode={datasetMode} onDatasetModeChange={setDatasetMode} /></section>

      <section aria-label="Distribution and alerts"><SectionHeading num="03" title="Distribution and alerts" subtitle="Industry classifications and current operational alerts" /><div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]"><IndustryDistributionChart /><RecentAlertsWidget /></div></section>
    </div>
  )
}
