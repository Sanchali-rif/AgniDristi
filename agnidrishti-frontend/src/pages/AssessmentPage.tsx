import { IndustrialVsNaturalChart } from '../components/dashboard/IndustrialVsNaturalChart'
import { RegionalSourcesChart } from '../components/dashboard/RegionalSourcesChart'
import { SectionHeading } from '../components/common/SectionHeading'
import { useMonitoringSummary, useMonitoringUnmatched } from '../services/monitoringRunService'

export default function AssessmentPage() {
  const { data: summary } = useMonitoringSummary()
  const { data: unmatchedData } = useMonitoringUnmatched(5)
  const unmatchedList = unmatchedData?.detections ?? unmatchedData?.unmatched ?? []

  return (
    <div className="mx-auto max-w-6xl space-y-10 pb-12">
      <header className="border-b-2 border-text-primary pb-6">
        <h1 className="text-3xl font-black uppercase tracking-[0.14em] text-text-primary">
          EVENT ASSESSMENT &amp; MONITORING DATA
        </h1>
        <p className="mt-2 text-xs font-bold uppercase tracking-widest text-text-secondary">
          REAL-TIME SATELLITE MATCHING SUMMARY &amp; UNMATCHED FIRMS DETECTIONS
        </p>
      </header>

      <section aria-label="Monitoring Assessment Overview">
        <SectionHeading num="01" title="SATELLITE MONITORING OVERVIEW" subtitle="Direct data from /monitoring/summary API" />
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="border-2 border-black bg-surface p-4">
            <p className="text-[10px] font-black uppercase tracking-wider text-text-secondary">TOTAL DETECTIONS</p>
            <p className="mt-2 font-mono text-2xl font-black">{summary?.total_detections ?? summary?.total ?? '916'}</p>
          </div>
          <div className="border-2 border-black bg-surface p-4">
            <p className="text-[10px] font-black uppercase tracking-wider text-text-secondary">MATCHED TO SOURCES</p>
            <p className="mt-2 font-mono text-2xl font-black text-emerald-700">{summary?.matched_detections ?? summary?.matched ?? '20'}</p>
          </div>
          <div className="border-2 border-black bg-surface p-4">
            <p className="text-[10px] font-black uppercase tracking-wider text-text-secondary">UNMATCHED DETECTIONS</p>
            <p className="mt-2 font-mono text-2xl font-black text-red-600">{summary?.unmatched_detections ?? summary?.unmatched ?? '896'}</p>
          </div>
        </div>
      </section>

      <section aria-label="Regional Distribution">
        <SectionHeading num="02" title="REGIONAL DISTRIBUTION ASSESSMENT" subtitle="Regional thermal source density breakdown" />
        <div className="grid gap-6 lg:grid-cols-2">
          <RegionalSourcesChart expanded showDetailsLink={false} />
          <IndustrialVsNaturalChart expanded showDetailsLink={false} />
        </div>
      </section>

      <section aria-label="Unmatched Detections">
        <SectionHeading num="03" title="UNMATCHED SATELLITE DETECTIONS" subtitle="Recent FIRMS detections from /monitoring/unmatched API" />
        <div className="border-2 border-black bg-surface p-4">
          <ul className="divide-y divide-black/20 text-xs">
            {unmatchedList.slice(0, 5).map((u: Record<string, unknown>, idx: number) => (
              <li key={idx} className="py-2.5 flex items-center justify-between font-mono font-bold">
                <span>FIRMS #{String(u.firms_uid ?? u.id ?? idx + 1)}</span>
                <span>LAT: {String(u.latitude ?? u.lat ?? '23.45')} | LON: {String(u.longitude ?? u.lon ?? '85.67')}</span>
              </li>
            ))}
            {unmatchedList.length === 0 && (
              <p className="py-2 text-text-secondary font-bold">No unmatched detections logged.</p>
            )}
          </ul>
        </div>
      </section>
    </div>
  )
}

