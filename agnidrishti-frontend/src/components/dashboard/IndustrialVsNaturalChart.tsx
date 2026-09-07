import { Link } from 'react-router-dom'
import { useSources } from '../../services/sourceService'
import type { SourceCategory } from '../../types/source'

const categoryDetails: { category: SourceCategory; label: string; color: string }[] = [
  { category: 'industrial', label: 'Industrial', color: '#000000' },
  { category: 'natural_biomass', label: 'Natural / Biomass', color: '#16a34a' },
  { category: 'persistent', label: 'Persistent', color: '#2563eb' },
  { category: 'abnormal', label: 'Abnormal', color: '#dc2626' },
  { category: 'unknown', label: 'Unknown', color: '#71717a' },
  { category: 'gas_flare', label: 'Gas Flare / FIRMS', color: '#9333ea' },
  { category: 'new', label: 'New', color: '#d97706' },
]

export function IndustrialVsNaturalChart({ expanded = false, showDetailsLink = true }: { expanded?: boolean; showDetailsLink?: boolean }) {
  const { data: sources = [], isLoading } = useSources()
  const total = sources.length
  const slices = categoryDetails.map((detail) => ({ ...detail, count: sources.filter((source) => source.category === detail.category).length, percentage: total ? (sources.filter((source) => source.category === detail.category).length / total) * 100 : 0 }))
  const gradient = slices.reduce<{ offset: number; parts: string[] }>((result, slice) => {
    const start = result.offset
    const end = start + slice.percentage
    return { offset: end, parts: [...result.parts, `${slice.color} ${start}% ${end}%`] }
  }, { offset: 0, parts: [] }).parts.join(', ')

  return (
    <section className="rounded-none border-2 border-black bg-surface p-5 shadow-sm" aria-labelledby="source-breakdown-heading">
      <div className="flex items-center justify-between gap-3 border-b-2 border-black pb-3">
        <h2 id="source-breakdown-heading" className="text-sm font-black uppercase tracking-wider text-text-primary">Industrial vs Natural</h2>
        {showDetailsLink && <Link to="/assessment" className="text-xs font-bold uppercase tracking-wider text-text-primary hover:underline">View details →</Link>}
      </div>
      {isLoading ? <div className="mt-5 h-32 animate-pulse bg-zinc-200" role="status" /> : (
        <div className={`${expanded ? 'mt-8 gap-10 flex-wrap' : 'mt-5 gap-5'} flex items-center justify-center`}>
          <div className={`relative ${expanded ? 'h-48 w-48' : 'h-32 w-32'} shrink-0 rounded-full border-2 border-black`} style={{ background: `conic-gradient(${gradient || 'var(--color-border) 0 100%'})` }} role="img">
            <div className={`${expanded ? 'inset-8' : 'inset-5'} absolute flex items-center justify-center rounded-full border-2 border-black bg-surface`}><span className={`${expanded ? 'text-2xl' : 'text-lg'} font-mono font-black text-text-primary`}>{total}</span></div>
          </div>
          <div className={`${expanded ? 'gap-3 text-xs' : 'gap-2 text-[10px]'} grid text-text-secondary`}>
            {slices.map((slice) => <p key={slice.category} className="font-semibold uppercase"><span className="mr-1.5 inline-block h-2 w-2 border border-black" style={{ backgroundColor: slice.color }} />{slice.label} <span className="font-mono text-text-primary">{slice.percentage.toFixed(1)}%</span></p>)}
          </div>
        </div>
      )}
    </section>
  )
}

