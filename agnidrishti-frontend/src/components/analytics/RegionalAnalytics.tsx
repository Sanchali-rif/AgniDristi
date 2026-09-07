import { BarChart3, Flame, MapPinned } from 'lucide-react'

const regions = [
  { name: 'Jharkhand', sources: 148, share: 82, trend: '+12%' },
  { name: 'West Bengal', sources: 96, share: 53, trend: '+8%' },
  { name: 'Bihar', sources: 74, share: 41, trend: '+5%' },
  { name: 'Odisha', sources: 51, share: 28, trend: '+3%' },
]

const industries = [
  ['Steel & metals', 42, 'bg-accent'],
  ['Power generation', 31, 'bg-info'],
  ['Brick kilns', 18, 'bg-warning'],
  ['Fuel processing', 9, 'bg-danger'],
] as const

export function RegionalAnalytics() {
  return (
    <section aria-labelledby="regional-analytics-heading">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 id="regional-analytics-heading" className="flex items-center gap-2 text-lg font-semibold text-text-primary">
            <MapPinned size={19} aria-hidden="true" />
            Regional analytics
          </h2>
          <p className="mt-1 text-sm text-text-secondary">Illustrative aggregate view using demo data, not live regional reporting.</p>
        </div>
        <span className="rounded-full bg-warning/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-warning">Demo data</span>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <article className="rounded-lg border border-border bg-surface p-4">
          <Flame size={18} className="text-accent" aria-hidden="true" />
          <p className="mt-3 text-xs text-text-secondary">Sources monitored</p>
          <p className="mt-1 font-mono text-2xl font-semibold text-text-primary">369</p>
        </article>
        <article className="rounded-lg border border-border bg-surface p-4">
          <BarChart3 size={18} className="text-info" aria-hidden="true" />
          <p className="mt-3 text-xs text-text-secondary">Persistent share</p>
          <p className="mt-1 font-mono text-2xl font-semibold text-text-primary">64%</p>
        </article>
        <article className="rounded-lg border border-border bg-surface p-4">
          <MapPinned size={18} className="text-success" aria-hidden="true" />
          <p className="mt-3 text-xs text-text-secondary">Regions covered</p>
          <p className="mt-1 font-mono text-2xl font-semibold text-text-primary">4</p>
        </article>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <article className="rounded-lg border border-border bg-surface p-5">
          <h3 className="text-sm font-semibold text-text-primary">Sources by region</h3>
          <div className="mt-5 space-y-4">
            {regions.map((region) => (
              <div key={region.name}>
                <div className="flex justify-between text-xs"><span className="font-medium text-text-primary">{region.name}</span><span className="font-mono text-text-secondary">{region.sources} <span className="text-success">{region.trend}</span></span></div>
                <div className="mt-2 h-2 rounded-full bg-bg"><div className="h-2 rounded-full bg-accent" style={{ width: `${region.share}%` }} /></div>
              </div>
            ))}
          </div>
        </article>
        <article className="rounded-lg border border-border bg-surface p-5">
          <h3 className="text-sm font-semibold text-text-primary">Sources by industry</h3>
          <div className="mt-5 space-y-4">
            {industries.map(([name, value, color]) => (
              <div key={name}>
                <div className="flex justify-between text-xs"><span className="font-medium text-text-primary">{name}</span><span className="font-mono text-text-secondary">{value}%</span></div>
                <div className="mt-2 h-2 rounded-full bg-bg"><div className={`h-2 rounded-full ${color}`} style={{ width: `${value}%` }} /></div>
              </div>
            ))}
          </div>
          <div className="mt-6 flex items-center gap-3 border-t border-border pt-4 text-xs text-text-secondary"><span className="h-2.5 w-2.5 rounded-full bg-success" /> Industrial 71% <span className="h-2.5 w-2.5 rounded-full bg-slate-300" /> Natural / other 29%</div>
        </article>
      </div>
    </section>
  )
}
