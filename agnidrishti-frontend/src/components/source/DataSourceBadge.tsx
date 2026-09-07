export function DataSourceBadge() {
  return (
    <div
      className="rounded-lg border border-info/30 bg-info/10 px-3 py-2 text-xs text-text-secondary"
      title="FIRMS is a live daily monitoring feed with approximately 7-10 hour latency and 375-750m resolution. VNF is training-only data and is not live."
    >
      <span className="font-medium text-info">Live: FIRMS</span>
      <span aria-hidden="true"> · </span>
      <span>Trained on: VNF</span>
    </div>
  )
}
