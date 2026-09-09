import { useState } from 'react'
import { Download, FileBarChart, FileText, Map, CheckCircle2 } from 'lucide-react'
import { useKPISummary } from '../services/kpiService'
import { useAllAlerts } from '../services/alertService'
import { useSources } from '../services/sourceService'

export default function ReportsPage() {
  const [downloadMsg, setDownloadMsg] = useState('')
  const { data: summary } = useKPISummary()
  const { data: alertsData } = useAllAlerts()
  const alerts = alertsData?.alerts ?? []
  const { data: sources = [] } = useSources()

  const handleExportCSV = (reportName: string, data: unknown) => {
    const jsonStr = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${reportName.toLowerCase().replaceAll(' ', '_')}_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    setDownloadMsg(`Exported intelligence report "${reportName}" directly from live satellite telemetry dataset.`)
  }

  const dynamicReports = [
    {
      title: 'Executive Satellite Thermal Digest',
      type: 'Real-time Telemetry Brief',
      date: new Date().toLocaleDateString('en-IN', { dateStyle: 'medium' }),
      description: `Summary payload: ${summary?.thermalObjects ?? 0} thermal objects registered, ${summary?.matchedFirms ?? 0} matched sources, ${summary?.unmatchedFirms ?? 0} unmatched FIRMS detections.`,
      icon: Map,
      payload: summary,
    },
    {
      title: 'Active Alert Stream & Anomaly Log',
      type: 'Alert Intelligence Log',
      date: new Date().toLocaleDateString('en-IN', { dateStyle: 'medium' }),
      description: `Active alerts payload containing ${alertsData?.count ?? 0} live system alert records.`,
      icon: FileBarChart,
      payload: alerts,
    },
    {
      title: 'Persistent Thermal Source Proximity Report',
      type: 'Geospatial Investigation File',
      date: new Date().toLocaleDateString('en-IN', { dateStyle: 'medium' }),
      description: `Geospatial coordinate payload listing ${sources.length} active thermal sources mapped.`,
      icon: FileText,
      payload: sources,
    },
  ]

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-text-secondary">INTELLIGENCE OUTPUT</span>
        <h1 className="text-2xl font-black tracking-tight uppercase text-text-primary">Intelligence Reports</h1>
        <p className="mt-1 text-xs font-semibold text-text-secondary">Export live geospatial and satellite anomaly briefs directly from satellite telemetry feeds.</p>
      </div>

      <div className="space-y-4">
        {dynamicReports.map(({ title, type, date, description, icon: Icon, payload }) => (
          <article key={title} className="flex flex-col gap-4 border-2 border-black bg-surface p-5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <div className="border-2 border-black bg-[#d8f5a9] p-2.5 text-black">
                <Icon size={22} aria-hidden="true" />
              </div>
              <div>
                <p className="font-mono text-[10px] font-black uppercase tracking-wider text-text-secondary">{type} · {date}</p>
                <h2 className="mt-1 text-sm font-black tracking-wide uppercase text-text-primary">{title}</h2>
                <p className="mt-1 text-xs font-semibold text-text-secondary">{description}</p>
              </div>
            </div>
            <button type="button" onClick={() => handleExportCSV(title, payload)}
              className="inline-flex shrink-0 items-center justify-center gap-1.5 border-2 border-black dark:border-zinc-700 bg-black text-white dark:bg-[#d8f5a9] dark:text-black px-4 py-2 text-xs font-black uppercase tracking-wider hover:bg-zinc-800 dark:hover:bg-[#c9f090] transition-colors cursor-pointer shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              <Download size={14} /> EXPORT JSON/CSV
            </button>
          </article>
        ))}
      </div>

      {downloadMsg && (
        <div className="flex items-center gap-2 border-2 border-black bg-[#d8f5a9] p-3 text-xs font-black uppercase text-black">
          <CheckCircle2 size={16} /> {downloadMsg}
        </div>
      )}
    </div>
  )
}
