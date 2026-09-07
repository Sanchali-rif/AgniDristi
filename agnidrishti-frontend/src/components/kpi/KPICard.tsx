import type { LucideIcon } from 'lucide-react'

type KPICardProps = {
  label: string
  value: number | string
  icon: LucideIcon
}

export function KPICard({ label, value, icon: Icon }: KPICardProps) {
  const isLongText = typeof value === 'string' && value.length > 5
  return (
    <article className="group relative min-w-0 overflow-hidden rounded-none border-2 border-text-primary bg-surface p-3.5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:hover:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]">
      <p className="truncate text-[10px] font-black uppercase tracking-wider text-text-secondary" title={label}>
        {label}
      </p>
      <div className="mt-2.5 flex items-center gap-2 min-w-0">
        <Icon className="text-text-primary stroke-[2.2] shrink-0 transition-transform group-hover:scale-110" size={20} aria-hidden="true" />
        <p className={`font-mono font-black tabular-nums tracking-tight text-text-primary leading-none min-w-0 truncate ${isLongText ? 'text-xs sm:text-sm lg:text-base' : 'text-xl sm:text-2xl'}`} title={String(value)}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
      </div>
    </article>
  )
}



