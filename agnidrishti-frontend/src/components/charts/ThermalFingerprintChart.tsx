import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useSourceFingerprint } from '../../services/sourceService'

export function ThermalFingerprintChart({ sourceId }: { sourceId: string }) {
  const { data, isLoading, isError } = useSourceFingerprint(sourceId)

  return (
    <section aria-label="Thermal fingerprint">
      <div className="flex items-baseline justify-between gap-3 border-b border-black/10 dark:border-zinc-800 pb-2">
        <h3 className="text-xs font-black uppercase tracking-wider text-text-primary">Thermal Fingerprint</h3>
        {data && <span className="font-mono text-[10px] font-bold text-text-secondary">Match: <strong className="text-text-primary">{data.similarityScore}%</strong></span>}
      </div>
      {data && <p className="mt-1 text-[11px] font-mono font-bold text-text-secondary uppercase truncate">Subtype: <span className="text-text-primary">{data.bestMatchIndustry}</span></p>}
      {isLoading && <div className="mt-3 h-36 animate-pulse bg-zinc-200 dark:bg-zinc-800" role="status" aria-label="Loading fingerprint" />}
      {isError && <p className="mt-3 text-xs font-bold text-danger">Unable to load fingerprint.</p>}
      {data && !isError && (
        <div className="mt-2 h-36 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.bins} margin={{ top: 4, right: 4, bottom: 0, left: -22 }}>
              <CartesianGrid stroke="#71717a" strokeDasharray="2 2" strokeOpacity={0.3} />
              <XAxis dataKey="tempK" tick={{ fontSize: 9, fill: 'currentColor' }} tickLine={false} />
              <YAxis tick={{ fontSize: 9, fill: 'currentColor' }} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(255, 255, 255, 0.08)' }} contentStyle={{ backgroundColor: '#18181b', color: '#fff', border: '1px solid #3f3f46', fontSize: '11px', borderRadius: '0px' }} />
              <Bar dataKey="normalizedFreq" name="Norm. Frequency %" fill="#3b82f6" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
