const inputCls = 'mt-1 w-full rounded-none border-2 border-black bg-surface px-3 py-2 text-xs font-bold font-mono text-text-primary outline-none focus:bg-zinc-100 transition-colors'

type FilterInputProps = {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  type?: string
  colSpan?: boolean
}

export function FilterInput({ label, value, onChange, placeholder, type = 'text', colSpan }: FilterInputProps) {
  return (
    <label className={`text-xs font-bold uppercase tracking-wider text-text-secondary${colSpan ? ' sm:col-span-2' : ''}`}>
      {label}
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className={inputCls} />
    </label>
  )
}

type FilterSelectProps = {
  label: string
  value: string
  onChange: (v: string) => void
  options: [string, string][]
  allLabel?: string
}

export function FilterSelect({ label, value, onChange, options, allLabel = 'Any' }: FilterSelectProps) {
  return (
    <label className="text-xs font-bold uppercase tracking-wider text-text-secondary">
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)} className={inputCls}>
        <option value="">{allLabel}</option>
        {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
      </select>
    </label>
  )
}

