import { Building2, Navigation } from 'lucide-react'
import { useNearbyFacilities } from '../../services/facilityService'

export function NearbyFacilitiesTable({ sourceId }: { sourceId?: string }) {
  const { data: facilities = [], isLoading, isError } = useNearbyFacilities(sourceId)

  return (
    <section aria-labelledby="nearby-facilities-heading">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 id="nearby-facilities-heading" className="flex items-center gap-2 text-sm font-semibold text-text-primary">
            <Building2 size={16} aria-hidden="true" />
            Nearby industrial facilities
          </h3>
          <p className="mt-1 text-xs text-text-secondary">
            Derived from backend detections near {sourceId ?? 'the selected source'}
          </p>
        </div>
        <span className="shrink-0 rounded-full bg-bg px-2 py-1 text-xs font-medium text-text-secondary">
          {facilities.length} found
        </span>
      </div>

      {isLoading && <p className="mt-4 text-xs text-text-secondary">Loading nearby facilities...</p>}
      {isError && <p className="mt-4 text-xs text-danger">Unable to load nearby facilities.</p>}
      {!isLoading && !isError && <div className="mt-4 overflow-x-auto rounded-lg border border-border">
        <table className="w-full min-w-[720px] text-left text-xs">
          <caption className="sr-only">Facilities near {sourceId ?? 'the selected source'}</caption>
          <thead className="bg-bg text-[10px] uppercase tracking-wide text-text-secondary">
            <tr>
              <th scope="col" className="px-3 py-2.5 font-medium">Facility</th>
              <th scope="col" className="px-3 py-2.5 font-medium">Type</th>
              <th scope="col" className="px-3 py-2.5 font-medium">Industry</th>
              <th scope="col" className="px-3 py-2.5 font-medium">Distance</th>
              <th scope="col" className="px-3 py-2.5 font-medium">Direction</th>
              <th scope="col" className="px-3 py-2.5 font-medium">Nearby infrastructure</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-surface">
            {facilities.map((facility) => (
              <tr key={facility.name} className="hover:bg-bg">
                <th scope="row" className="px-3 py-3 font-medium text-text-primary">{facility.name}</th>
                <td className="px-3 py-3 text-text-secondary">{facility.type}</td>
                <td className="px-3 py-3 text-text-secondary">{facility.industry}</td>
                <td className="px-3 py-3 font-mono text-text-primary">{facility.distanceKm.toFixed(1)} km</td>
                <td className="px-3 py-3"><span className="inline-flex items-center gap-1 font-mono text-text-primary"><Navigation size={12} aria-hidden="true" />{facility.direction}</span></td>
                <td className="px-3 py-3 text-text-secondary">{facility.nearbyInfrastructure}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>}
    </section>
  )
}
