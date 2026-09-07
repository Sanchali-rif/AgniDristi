import { Layers3, Satellite, Thermometer } from 'lucide-react'
import { useState } from 'react'

export function SatelliteContextViewer({ sourceId }: { sourceId?: string }) {
  const [showThermalOverlay, setShowThermalOverlay] = useState(false)

  return (
    <section aria-labelledby="satellite-context-heading">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 id="satellite-context-heading" className="flex items-center gap-2 text-sm font-semibold text-text-primary">
            <Satellite size={16} aria-hidden="true" />
            Satellite context
          </h3>
          <p className="mt-1 text-xs text-text-secondary">Static preview centered on {sourceId ?? 'the selected source'}</p>
        </div>
        <span className="rounded-full bg-warning/10 px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-warning">Preview</span>
      </div>

      <div className="relative mt-4 overflow-hidden rounded-lg border border-border bg-slate-900">
        <img
          src="/satellite-context.svg"
          alt="Mock satellite view showing a thermal source and nearby industrial structures"
          className="block aspect-[16/9] w-full object-cover"
        />
        {showThermalOverlay && <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_54%_48%,rgba(239,68,68,.85),rgba(249,115,22,.48)_12%,transparent_34%)] mix-blend-screen" aria-hidden="true" />}
        <div className="absolute left-3 top-3 flex items-center gap-1.5 rounded bg-slate-950/75 px-2 py-1 text-[10px] text-white">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" />
          {sourceId ?? 'Selected source'}
        </div>
        <div className="absolute bottom-3 left-3 rounded bg-slate-950/75 px-2 py-1 text-[10px] text-white">N ↑ · 500 m</div>
      </div>

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <p className="flex items-center gap-1.5 text-xs text-text-secondary"><Layers3 size={14} aria-hidden="true" /> Sentinel-2 / Prithvi-EO · TBD</p>
        <button
          type="button"
          role="switch"
          aria-checked={showThermalOverlay}
          onClick={() => setShowThermalOverlay((visible) => !visible)}
          className="inline-flex items-center gap-2 rounded-md border border-border px-2.5 py-1.5 text-xs font-medium text-text-primary hover:bg-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <Thermometer size={14} aria-hidden="true" />
          Thermal overlay
          <span className={`h-4 w-7 rounded-full p-0.5 transition-colors ${showThermalOverlay ? 'bg-accent' : 'bg-border'}`} aria-hidden="true">
            <span className={`block h-3 w-3 rounded-full bg-white transition-transform ${showThermalOverlay ? 'translate-x-3' : ''}`} />
          </span>
        </button>
      </div>
      <p className="mt-2 text-[11px] text-text-secondary">Imagery is a static mock. Live satellite and thermal layers are backend-dependent.</p>
    </section>
  )
}
