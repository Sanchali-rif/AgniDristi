type SectionHeadingProps = {
  num: string
  title: string
  subtitle?: string
}

export function SectionHeading({ num, title, subtitle }: SectionHeadingProps) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3 border-b-2 border-text-primary pb-3">
      <div className="flex items-baseline gap-3">
        <span className="font-mono text-sm font-black tracking-widest text-text-secondary">{num}</span>
        <h2 className="text-xl sm:text-2xl font-black uppercase tracking-[0.12em] text-text-primary leading-tight">{title}</h2>
      </div>
      {subtitle && <p className="text-xs font-semibold uppercase tracking-wider text-text-secondary">{subtitle}</p>}
    </div>
  )
}

