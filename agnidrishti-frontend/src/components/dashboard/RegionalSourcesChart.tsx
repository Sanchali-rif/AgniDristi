import { Link } from 'react-router-dom'
import { useSources } from '../../services/sourceService'

function regionForCoord(lat: number, lon: number): string {
  if (lat >= 21.8 && lat <= 25.5 && lon >= 83.2 && lon <= 88.0) return 'Jharkhand'
  if (lat >= 24.2 && lat <= 27.8 && lon >= 83.2 && lon <= 88.5) return 'Bihar'
  if (lat >= 21.5 && lat <= 27.5 && lon >= 85.8 && lon <= 89.8) return 'West Bengal'
  if (lat >= 17.5 && lat <= 22.8 && lon >= 81.2 && lon <= 87.5) return 'Odisha'
  if (lat >= 17.5 && lat <= 24.5 && lon >= 80.0 && lon <= 84.5) return 'Chhattisgarh'
  if (lat >= 23.5 && lat <= 30.5 && lon >= 68.0 && lon <= 75.5) return 'Rajasthan / NW'
  if (lat >= 23.8 && lat <= 31.5 && lon >= 77.0 && lon <= 84.5) return 'Uttar Pradesh'
  if (lat >= 21.0 && lat <= 26.8 && lon >= 74.0 && lon <= 82.5) return 'Madhya Pradesh'
  if (lat >= 20.0 && lat <= 24.8 && lon >= 68.0 && lon <= 74.5) return 'Gujarat'
  if (lat >= 15.5 && lat <= 22.0 && lon >= 72.5 && lon <= 80.5) return 'Maharashtra'
  if (lat >= 8.0 && lat <= 19.5 && lon >= 74.0 && lon <= 85.0) return 'South India'
  if (lat >= 22.0 && lat <= 29.5 && lon >= 89.8 && lon <= 97.5) return 'NE India'
  if (lat >= 28.0 && lat <= 37.5 && lon >= 73.0 && lon <= 81.0) return 'North India'
  return 'Central / Other'
}

const ALL_REGIONS = ['Jharkhand', 'Bihar', 'West Bengal', 'Odisha', 'Chhattisgarh', 'Rajasthan / NW', 'Uttar Pradesh', 'Madhya Pradesh', 'Gujarat', 'Maharashtra', 'South India', 'NE India', 'North India', 'Central / Other']

export function RegionalSourcesChart({ expanded = false, showDetailsLink = true }: { expanded?: boolean; showDetailsLink?: boolean }) {
  const { data: sources = [], isLoading } = useSources()
  const map = new Map<string, number>()
  sources.forEach((s) => {
    const r = regionForCoord(s.lat, s.lon)
    map.set(r, (map.get(r) ?? 0) + 1)
  })

  const sortedRegions = ALL_REGIONS.map((r) => ({ region: r, count: map.get(r) ?? 0 }))
    .filter((r) => expanded ? r.count > 0 || ['Jharkhand', 'Bihar', 'West Bengal', 'Odisha', 'Chhattisgarh', 'Rajasthan / NW'].includes(r.region) : r.count > 0)
    .sort((a, b) => b.count - a.count)

  const regionCounts = expanded ? sortedRegions : sortedRegions.slice(0, 6)
  const maxCount = Math.max(...regionCounts.map((r) => r.count), 1)

  return (
    <section className="rounded-none border-2 border-black dark:border-zinc-700 bg-surface p-5 shadow-sm" aria-labelledby="regional-sources-heading">
      <div className="flex items-center justify-between gap-3 border-b-2 border-black dark:border-zinc-700 pb-3">
        <h2 id="regional-sources-heading" className="text-sm font-black uppercase tracking-wider text-text-primary">Regional Thermal Sources</h2>
        {showDetailsLink && <Link to="/assessment" className="text-xs font-bold uppercase tracking-wider text-text-primary hover:underline">View details →</Link>}
      </div>
      {isLoading ? <div className="mt-5 h-40 animate-pulse bg-zinc-200 dark:bg-zinc-800" /> : (
        <div className={`mt-5 grid grid-cols-2 gap-x-5 ${expanded ? 'gap-y-6 sm:grid-cols-3' : 'gap-y-4'}`}>
          {regionCounts.map((r) => (
            <div key={r.region}>
              <div className="flex items-center justify-between gap-2 text-[10px]">
                <span className="font-bold text-text-primary uppercase tracking-wider">{r.region}</span>
                <span className="font-mono font-bold text-text-primary">{r.count}</span>
              </div>
              <div className="mt-1.5 h-2.5 border border-black dark:border-zinc-700 bg-zinc-200 dark:bg-zinc-800">
                <div className="h-full bg-black dark:bg-[#d8f5a9]" style={{ width: `${(r.count / maxCount) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
      {!isLoading && <p className="mt-4 text-right font-mono text-[10px] font-bold text-text-secondary uppercase">{sources.length} SOURCES TOTAL</p>}
    </section>
  )
}
