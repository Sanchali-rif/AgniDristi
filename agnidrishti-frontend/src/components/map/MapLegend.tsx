import {
  getShapeClipPath,
  MAP_CATEGORY_COLORS,
  MAP_CATEGORY_LABELS,
  MAP_CATEGORY_SHAPES,
} from '../../lib/mapColors'

export function MapLegend() {
  return (
    <div className="absolute bottom-4 left-4 z-[1000] rounded-lg border border-border bg-surface/95 p-3 shadow-sm">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-secondary">Categories</p>
      <ul className="grid grid-cols-2 gap-x-4 gap-y-2">
        {(Object.keys(MAP_CATEGORY_COLORS) as Array<keyof typeof MAP_CATEGORY_COLORS>).map((category) => (
          <li key={category} className="flex items-center gap-2 text-xs text-text-primary">
            <span
              aria-hidden="true"
              className="h-3 w-3 shrink-0"
              style={{
                backgroundColor: MAP_CATEGORY_COLORS[category],
                clipPath: getShapeClipPath(MAP_CATEGORY_SHAPES[category]),
              }}
            />
            {MAP_CATEGORY_LABELS[category]}
          </li>
        ))}
      </ul>
    </div>
  )
}
