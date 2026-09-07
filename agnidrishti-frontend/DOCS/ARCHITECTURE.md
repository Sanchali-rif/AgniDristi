# ARCHITECTURE.md — AgniDrishti Frontend

This document defines exactly how the AgniDrishti frontend is structured. It is built directly on top of `PRD.md` and `TECHSTACK.md`. Backend (FastAPI) is out of scope and treated as an external REST API consumed via `services/`.

---

## 1. High-Level Flow

```text
User (browser)
   │
   ▼
React Router (page-level routes, one per sidebar item)
   │
   ▼
Page component
   │  reads/writes via hooks
   ▼
React Query hooks (services/*.ts) ──► Backend API (FastAPI) [external, TBD contract]
   │
   ▼
Zustand stores (selected source, active filters, theme) ── local UI state, not server state
   │
   ▼
Component tree (map, charts, tables, cards) renders combined server + client state
```

### Request Flow
```text
Page mounts → useQuery hook (e.g. useSources) → services/sourceService.ts
   → fetch(`${API_BASE_URL}/sources`) → JSON response
   → React Query cache → component re-renders with data
```

### Selection Flow (Map click → Source Snapshot)
```text
User clicks map marker
   → onClick handler sets selectedSourceId in useSourceStore (Zustand)
   → SourceSnapshotPanel reads selectedSourceId
   → useQuery(['source', selectedSourceId]) fetches detail
   → Panel slides in (Framer Motion) with data once loaded
```

### Theme Flow
```text
User toggles theme
   → useThemeStore.toggle() (Zustand, persisted to localStorage... 
     NOTE: browser storage restrictions apply only inside Artifacts sandboxes;
     this is a standalone app, so localStorage is fine here)
   → data-theme attribute updated on <html>
   → Tailwind CSS variables switch (see TECHSTACK.md Design Tokens)
```

---

## 2. Project Structure

```text
agnidrishti-frontend/
├── src/
│   ├── app/              # App shell: router, providers, layout
│   ├── pages/            # One file per sidebar route
│   ├── components/       # Reusable UI, organized by section
│   ├── features/         # Feature-scoped logic (map, filters, alerts)
│   ├── services/         # API call functions (React Query hooks live here)
│   ├── stores/           # Zustand stores
│   ├── types/            # Placeholder TypeScript interfaces (TBD backend contract)
│   ├── lib/               # Constants, formatters, map colors, API client
│   ├── styles/            # Tailwind config, theme CSS variables
│   └── main.tsx
├── public/
├── index.html
├── tailwind.config.js
├── vite.config.ts
├── package.json
└── README.md
```

---

## 3. Page Structure (React Router, multi-page, confirmed)

| Route | Page | Sidebar item |
|---|---|---|
| `/` → redirect to `/dashboard` | — | — |
| `/dashboard` | Dashboard (map + KPIs + snapshot panel) | Dashboard |
| `/search` | Search & Discovery | Search & Discovery |
| `/investigation/:sourceId?` | Source Investigation | Source Investigation |
| `/assessment` | Event Assessment | Event Assessment |
| `/anomaly` | Change & Anomaly | Change & Anomaly |
| `/reports` | Intelligence Reports | Intelligence Reports |
| `/alerts` | Alerts Center | Alerts |
| `/data-layers` | Data Layers | Data Layers |
| `/system` | System / Model Status | System / Model |
| `/login` | Login (auth flow `TBD`) | — |

**Source Snapshot** is not a route — it is a **slide-in side panel** (confirmed), mounted at the app-shell level (`app/AppShell.tsx`) so it can be triggered from any page (Dashboard map, Search results, Alerts list) without losing the underlying page's state. Controlled by `useSourceStore.selectedSourceId`.

---

## 4. Component Architecture

```text
components/
├── layout/
│   ├── TopNav.tsx              # logo, search, notifications, profile, system status (Origin UI base)
│   ├── Sidebar.tsx             # 9-item nav (Origin UI base)
│   └── AppShell.tsx            # wraps pages, mounts SourceSnapshotPanel globally
├── kpi/
│   └── KPICard.tsx             # Magic UI base; props: label, value, delta, icon
├── map/
│   ├── ThermalMap.tsx          # react-leaflet map, marker clustering
│   ├── MapLegend.tsx           # category color + shape legend
│   └── mapColors.ts            # fixed category color constants (see TECHSTACK.md)
├── filters/
│   └── FilterPanel.tsx         # Origin UI form components; writes to useFilterStore
├── source/
│   ├── SourceSnapshotPanel.tsx # Framer Motion slide-in; Origin UI card/dialog base
│   └── DataSourceBadge.tsx     # FIRMS/VNF disclosure tooltip (fixed requirement)
├── charts/
│   ├── ActivityTimelineChart.tsx   # Recharts bar+line combo
│   ├── ThermalFingerprintChart.tsx # Recharts histogram
│   └── AnomalyDetectionChart.tsx   # Recharts dual-line
├── tables/
│   └── NearbyFacilitiesTable.tsx   # Origin UI table
├── satellite/
│   └── SatelliteContextViewer.tsx  # image + overlay toggle
├── alerts/
│   └── AlertsList.tsx          # Origin UI list/badge components
├── timeline/
│   └── SourceHistoryTimeline.tsx   # Kibo UI timeline component
└── ui/                          # vendored Origin UI / Magic UI / Kibo UI / React Bits primitives
```

| Component | Responsibility | Data source |
|---|---|---|
| `ThermalMap` | Render all sources as clustered, color/shape-coded markers | `useSources()` (React Query) |
| `KPICard` ×6 | Display one aggregate metric + trend | `useKPISummary()` |
| `SourceSnapshotPanel` | Show full detail for `selectedSourceId` | `useSourceDetail(id)` |
| `FilterPanel` | Collect filter state, does not fetch itself | writes to `useFilterStore` (Zustand) |
| `ActivityTimelineChart` | 12-month detection/temp trend for selected source | `useSourceHistory(id)` |
| `ThermalFingerprintChart` | Histogram + best-match label | `useSourceFingerprint(id)` |
| `AnomalyDetectionChart` | Baseline vs current + anomaly score | `useSourceAnomaly(id)` |
| `NearbyFacilitiesTable` | Facilities within radius of selected source | `useNearbyFacilities(id)` |
| `SatelliteContextViewer` | Sentinel-2/Prithvi-EO image for selected source | `useSatelliteContext(id)` |
| `AlertsList` | Recent alerts feed | `useAlerts()` (polled) |

---

## 5. State Management

**Zustand (client-only UI state):**
```text
stores/
├── sourceStore.ts     # selectedSourceId, panel open/closed
├── filterStore.ts     # active filters (time range, type, industry, anomaly level, confidence)
└── themeStore.ts      # light/dark toggle, persisted to localStorage
```

**React Query (server state):**
```text
services/
├── apiClient.ts         # fetch wrapper, base URL from env
├── sourceService.ts      # useSources, useSourceDetail, useSourceHistory, useSourceFingerprint, useSourceAnomaly
├── facilityService.ts    # useNearbyFacilities
├── alertService.ts       # useAlerts (polling via refetchInterval)
├── kpiService.ts         # useKPISummary
└── reportService.ts      # useGenerateReport (TBD — mock until backend ready)
```

Rule: **Zustand never stores server data.** Any data that came from `services/` lives in the React Query cache only; Zustand only stores "what the user is currently looking at / has selected."

---

## 6. Component-to-Library Mapping (confirmed)

| Section | Library |
|---|---|
| Tables, forms, dropdowns, dialogs | Origin UI |
| Historical Activity timeline | Kibo UI |
| Nav bar / sidebar | Origin UI |
| KPI/stat cards | Magic UI |
| Buttons, badges, alerts | Origin UI |
| Decorative animation (sparing, 1–2 uses max) | React Bits |
| Structural transitions (panel slide-in, page transitions) | Framer Motion |

---

## 7. Data Shape (Placeholder — TBD pending Backend API contract)

No sample API response has been provided yet. The following placeholder TypeScript interfaces are used so frontend work can proceed independently of the backend. **These must be reconciled against the real FastAPI OpenAPI schema once available** — treat as a first draft, not a fixed contract.

```typescript
// types/source.ts

export type SourceCategory =
  | "industrial" | "persistent" | "new" | "abnormal"
  | "natural_biomass" | "gas_flare" | "unknown";

export interface SourceSummary {
  id: string;                    // e.g. "AGNI-IND-004821"
  category: SourceCategory;
  industrySubtype: string | null; // e.g. "Steel Plant"
  confidence: number;             // 0-100
  status: "persistent" | "new" | "transient";
  anomalyLevel: "low" | "medium" | "high";
  lat: number;
  lon: number;
}

export interface SourceDetail extends SourceSummary {
  firstDetected: string;   // ISO date
  lastDetected: string;    // ISO date
  district: string;
  state: string;
}

export interface KPISummary {
  totalSources: number;
  persistentSources: number;
  newSources: number;
  abnormalSources: number;
  industrialSources: number;
  highRiskAlerts: number;
  // each paired with a deltaPercent field, e.g.:
  totalSourcesDeltaPct: number;
}

export interface ActivityPoint {
  month: string;       // "2026-01"
  detections: number;
  avgTempK: number;
}

export interface ThermalFingerprint {
  bins: { tempK: number; normalizedFreq: number }[];
  bestMatchIndustry: string;
  similarityScore: number; // 0-100
}

export interface AnomalyPoint {
  date: string;
  baseline: number;
  current: number;
}

export interface Alert {
  id: string;
  sourceId: string;
  type: "high_anomaly" | "new_persistent" | "unusual_pattern" | "new_industrial" | "low_confidence";
  severity: "low" | "medium" | "high";
  timestamp: string;
}
```

---

## 8. Environment & Configuration

```text
.env.local (gitignored)
```

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Base URL for Backend API (FastAPI) — `TBD` until backend is deployed/local |
| `VITE_MAP_TILE_URL` | Leaflet tile provider URL (default: OSM public tile server) |

---

## 9. Final Frontend Repository Tree

```text
agnidrishti-frontend/
├── src/
│   ├── app/
│   │   ├── AppShell.tsx
│   │   ├── router.tsx
│   │   └── providers.tsx        # React Query + theme provider wrapper
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── SearchPage.tsx
│   │   ├── InvestigationPage.tsx
│   │   ├── AssessmentPage.tsx
│   │   ├── AnomalyPage.tsx
│   │   ├── ReportsPage.tsx
│   │   ├── AlertsPage.tsx
│   │   ├── DataLayersPage.tsx
│   │   ├── SystemStatusPage.tsx
│   │   └── LoginPage.tsx        # TBD auth
│   ├── components/
│   │   ├── layout/
│   │   ├── kpi/
│   │   ├── map/
│   │   ├── filters/
│   │   ├── source/
│   │   ├── charts/
│   │   ├── tables/
│   │   ├── satellite/
│   │   ├── alerts/
│   │   ├── timeline/
│   │   └── ui/
│   ├── services/
│   ├── stores/
│   ├── types/
│   ├── lib/
│   │   ├── apiClient.ts
│   │   ├── mapColors.ts
│   │   └── formatters.ts
│   ├── styles/
│   │   └── theme.css             # CSS variables for light/dark tokens
│   └── main.tsx
├── public/
├── index.html
├── tailwind.config.js
├── vite.config.ts
├── package.json
├── .env.local
└── README.md
```
