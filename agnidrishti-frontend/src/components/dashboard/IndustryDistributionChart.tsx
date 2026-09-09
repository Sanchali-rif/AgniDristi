import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useClassDistribution } from '../../services/dashboardService'

export function IndustryDistributionChart() {
  const query = useClassDistribution()
  return (
    <section className="border-2 border-text-primary bg-surface p-5" aria-labelledby="industry-distribution-heading">
      <div className="border-b-2 border-text-primary pb-3"><h2 id="industry-distribution-heading" className="text-sm font-black uppercase tracking-wider">Industry distribution</h2><p className="mt-1 text-xs text-text-secondary">Spatial classification labels, {query.data?.count ?? '…'} classes</p></div>
      {query.isLoading && <div className="mt-5 h-64 animate-pulse bg-text-primary/10" role="status"><span className="sr-only">Loading industry distribution</span></div>}
      {query.isError && <div className="grid h-64 place-items-center text-center"><div><p className="text-xs font-bold text-danger">Class distribution could not be loaded.</p><button type="button" onClick={() => query.refetch()} className="mt-3 border-2 border-black px-3 py-1 text-xs font-black uppercase">Retry</button></div></div>}
      {query.data?.classes.length === 0 && <div className="grid h-64 place-items-center text-xs font-bold text-text-secondary">No classifications have been reported.</div>}
      {query.data && query.data.classes.length > 0 && <div className="mt-5 h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={query.data.classes.slice(0, 12)} margin={{ left: 0, right: 8, bottom: 35 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#52525b" strokeOpacity={0.3} /><XAxis dataKey="label" interval={0} angle={-28} textAnchor="end" height={60} tick={{ fontSize: 9, fill: 'currentColor' }} /><YAxis allowDecimals={false} tick={{ fontSize: 10, fill: 'currentColor' }} /><Tooltip cursor={{ fill: 'rgba(255, 255, 255, 0.08)' }} contentStyle={{ backgroundColor: '#18181b', color: '#f4f4f5', border: '2px solid #3f3f46', borderRadius: 0, fontSize: 12, boxShadow: '3px 3px 0 #000' }} itemStyle={{ color: '#d8f5a9', fontWeight: 'bold' }} labelStyle={{ color: '#ffffff', fontWeight: 'bold', marginBottom: '4px' }} /><Bar dataKey="count" fill="#d8f5a9" stroke="#111827" strokeWidth={2} /></BarChart></ResponsiveContainer></div>}
    </section>
  )
}

