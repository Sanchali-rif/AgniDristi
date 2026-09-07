import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useSourceFingerprint } from '../../services/sourceService'

export function ThermalFingerprintChart({ sourceId }: { sourceId: string }) {
  const { data, isLoading, isError } = useSourceFingerprint(sourceId)

  return (
    <section aria-label="Thermal fingerprint">
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="text-sm font-semibold text-text-primary">Thermal fingerprint</h3>
        {data && <span className="text-xs text-text-secondary">Similarity: <strong className="text-text-primary">{data.similarityScore}%</strong></span>}
      </div>
      {data && <p className="mt-1 text-xs text-text-secondary">Best match: <span className="font-medium text-text-primary">{data.bestMatchIndustry}</span></p>}
       {isLoading && <div className="mt-3 h-40 animate-pulse rounded-lg bg-bg" role="status" aria-label="Loading fingerprint" />}
      {isError && <p className="mt-3 text-xs text-danger">Unable to load fingerprint.</p>}
      {data && !isError && (
        <div className="mt-3 h-40 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.bins} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" />
              <XAxis dataKey="tempK" tick={{ fontSize: 10 }} tickLine={false} />
              <YAxis tick={{ fontSize: 10 }} tickLine={false} />
              <Tooltip />
              <Bar dataKey="normalizedFreq" name="Frequency" fill="var(--color-info)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
