import { Link } from 'react-router-dom'
import { useSources } from '../../services/sourceService'

const REGIONS = ['Jharkhand', 'Bihar', 'West Bengal', 'Odisha', 'Chhattisgarh', 'Other']

function regionForCoord(lat: number, lon: number): string {
  if (lat >= 22 && lat <= 24.5 && lon >= 83 && lon <= 88) return 'Jharkhand'
  if (lat >= 24 && lat <= 27.5 && lon >= 83 && lon <= 89) return 'Bihar'
  if (lat >= 21 && lat <= 27.5 && lon >= 86 && lon <= 90) return 'West Bengal'
  if (lat >= 17.5 && lat <= 23 && lon >= 81 && lon <= 87.5) return 'Odisha'
  if (lat >= 17.5 && lat <= 24.5 && lon >= 80 && lon <= 84) return 'Chhattisgarh'
  return 'Other'
}

export function RegionalSourcesChart({ expanded = false, showDetailsLink = true }: { expanded?: boolean; showDetailsLink?: boolean }) {
  const { data: sources = [], isLoading } = useSources()
  const regionCounts = REGIONS.map((r) => ({
    region: r,
    count: sources.filter((s) => regionForCoord(s.lat, s.lon) === r).length,
  }))
  const maxCount = Math.max(...regionCounts.map((r) => r.count), 1)

  return (
    <section className="rounded-none border-2 border-black bg-surface p-5 shadow-sm" aria-labelledby="regional-sources-heading">
      <div className="flex items-center justify-between gap-3 border-b-2 border-black pb-3">
        <h2 id="regional-sources-heading" className="text-sm font-black uppercase tracking-wider text-text-primary">Regional Thermal Sources</h2>
        {showDetailsLink && <Link to="/assessment" className="text-xs font-bold uppercase tracking-wider text-text-primary hover:underline">View details →</Link>}
      </div>
      {isLoading ? <div className="mt-5 h-40 animate-pulse bg-zinc-200" /> : (
        <div className={`mt-5 grid grid-cols-2 gap-x-5 ${expanded ? 'gap-y-7 sm:grid-cols-3' : 'gap-y-4'}`}>
          {regionCounts.map((r) => (
            <div key={r.region}>
              <div className="flex items-center justify-between gap-2 text-[10px]">
                <span className="font-bold text-text-primary uppercase tracking-wider">{r.region}</span>
                <span className="font-mono font-bold text-text-primary">{r.count}</span>
              </div>
              <div className="mt-1.5 h-2.5 border border-black bg-zinc-200">
                <div className="h-full bg-black" style={{ width: `${(r.count / maxCount) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
      {!isLoading && <p className="mt-4 text-right font-mono text-[10px] font-bold text-text-secondary uppercase">{sources.length} SOURCES TOTAL</p>}
    </section>
  )
}

