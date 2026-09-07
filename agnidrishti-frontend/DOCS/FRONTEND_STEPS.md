# FRONTEND_STEPS.md — AgniDrishti Frontend Build Roadmap

Step-by-step implementation plan derived from `PRD.md`, `TECHSTACK.md`, and `ARCHITECTURE.md`. Each step lists Goal, Files, Implementation, Dependency, Verification, Expected Result.

---

### Step 1 — Project Scaffolding

**Goal:** Create the Vite + React project with the folder structure from `ARCHITECTURE.md` §2.

**Files:** Full `src/` tree (empty folders with `.gitkeep`).

**Implementation:** `npm create vite@latest agnidrishti-frontend -- --template react-ts`. Create all subfolders under `src/` as listed in the architecture doc.

**Dependency:** None.

**Verification:** `npm run dev` shows the default Vite page with no errors.

**Expected Result:** Empty, correctly structured project.

---

### Step 2 — Install Dependencies

**Goal:** Install the full package list from `TECHSTACK.md`.

**Files:** `package.json`

**Implementation:** Install: `react-router-dom`, `leaflet`, `react-leaflet`, `leaflet.markercluster`, `recharts`, `lucide-react`, `zustand`, `@tanstack/react-query`, `framer-motion`, `tailwindcss`, `postcss`, `autoprefixer`.

**Dependency:** Step 1.

**Verification:** `npm install` completes cleanly, no peer-dependency errors.

**Expected Result:** All packages importable.

---

### Step 3 — Tailwind + Design Tokens Setup

**Goal:** Configure Tailwind and implement the light/dark theme CSS variables from `TECHSTACK.md`.

**Files:** `tailwind.config.js`, `src/styles/theme.css`

**Implementation:** Define CSS custom properties for both themes (`--color-bg`, `--color-surface`, `--color-border`, `--color-accent`, `--color-text-primary`, `--color-text-secondary`, `--color-success`, `--color-warning`, `--color-danger`, `--color-info`) under `:root` and `[data-theme="dark"]`. Map Tailwind theme extension to reference these variables. Add Inter + JetBrains Mono via font-face or Google Fonts import.

**Dependency:** Step 2.

**Verification:** Toggling `data-theme` attribute on `<html>` manually in devtools visibly switches all token-based colors.

**Expected Result:** Working dual-theme design system.

---

### Step 4 — App Shell & Routing

**Goal:** Build `AppShell.tsx`, `router.tsx`, and stub pages for all 10 routes from `ARCHITECTURE.md` §3.

**Files:** `src/app/*`, `src/pages/*` (stub content only)

**Implementation:** Set up React Router with all routes. `AppShell` wraps `<Outlet />` with `TopNav`, `Sidebar`, and a mount point for `SourceSnapshotPanel` (empty for now). Each page is a placeholder `<h1>{PageName}</h1>` initially.

**Dependency:** Step 3.

**Verification:** Navigating sidebar links changes the URL and visible page content.

**Expected Result:** Full page skeleton with working navigation.

---

### Step 5 — Zustand Stores

**Goal:** Implement `sourceStore`, `filterStore`, `themeStore`.

**Files:** `src/stores/*`

**Implementation:** `sourceStore`: `selectedSourceId`, `isPanelOpen`, setters. `filterStore`: filter fields matching PRD §4.4, setters, reset. `themeStore`: `theme`, `toggleTheme`, persisted to `localStorage`.

**Dependency:** Step 4.

**Verification:** Theme toggle button (temporary, in TopNav) switches theme and persists on page reload.

**Expected Result:** Working global client state.

---

### Step 6 — API Client & Placeholder Types

**Goal:** Set up `apiClient.ts` and the placeholder types from `ARCHITECTURE.md` §7.

**Files:** `src/lib/apiClient.ts`, `src/types/source.ts`

**Implementation:** `apiClient.ts` wraps `fetch` with base URL from `VITE_API_BASE_URL`, JSON parsing, error handling. Types match §7 exactly. Add a `.env.local.example` documenting `VITE_API_BASE_URL` and `VITE_MAP_TILE_URL`.

**Dependency:** Step 2.

**Verification:** A test call to a mock/dummy JSON file resolves through `apiClient` without runtime errors.

**Expected Result:** Typed API layer ready to be wired to mock or real data.

---

### Step 7 — Mock Data Layer

**Goal:** Create dummy JSON matching the placeholder types, so all components can be built before the backend exists.

**Files:** `src/lib/mockData/*.json`

**Implementation:** Generate representative dummy data: ~30–50 sources spread across the AOI bounding box (21°N–27.3°N, 85.5°E–89.7°E), a few alerts, one detailed source history/fingerprint/anomaly set. Service functions (Step 8) read from these files when `VITE_API_BASE_URL` is unset.

**Dependency:** Step 6.

**Verification:** Mock data validates against TypeScript interfaces with no type errors.

**Expected Result:** Realistic data available for UI development without waiting on backend.

---

### Step 8 — React Query Services

**Goal:** Implement all hooks in `services/*.ts` from `ARCHITECTURE.md` §5.

**Files:** `src/services/*`

**Implementation:** `useSources`, `useSourceDetail`, `useSourceHistory`, `useSourceFingerprint`, `useSourceAnomaly`, `useNearbyFacilities`, `useAlerts` (with `refetchInterval` for polling), `useKPISummary`. Each falls back to mock data (Step 7) if `VITE_API_BASE_URL` is unset.

**Dependency:** Step 7.

**Verification:** React Query devtools show successful queries with mock data populated.

**Expected Result:** Full data-fetching layer, backend-agnostic.

---

### Step 9 — KPI Cards

**Goal:** Build `KPICard.tsx` and wire to `useKPISummary`.

**Files:** `src/components/kpi/KPICard.tsx`

**Implementation:** Magic UI card base; props `label, value, deltaPct, icon`. Render 6 cards on `DashboardPage`.

**Dependency:** Step 8.

**Verification:** Dashboard shows 6 populated KPI cards with correct mock values.

**Expected Result:** P0 feature complete (PRD §4.2).

---

### Step 10 — Interactive Map

**Goal:** Build `ThermalMap.tsx` with clustered, color/shape-coded markers.

**Files:** `src/components/map/ThermalMap.tsx`, `MapLegend.tsx`, `mapColors.ts`

**Implementation:** react-leaflet map with `leaflet.markercluster`. Markers colored per `mapColors.ts` (fixed category constants from `TECHSTACK.md`), shaped per category for color-blind accessibility. Legend component lists all 6 categories. Zoom/pan default controls, satellite/map tile toggle.

**Dependency:** Step 8.

**Verification:** Map renders all mock sources, clusters at low zoom, un-clusters on zoom-in, legend matches marker colors.

**Expected Result:** P0 feature complete (PRD §4.3).

---

### Step 11 — Source Snapshot Panel

**Goal:** Build the slide-in detail panel (confirmed behavior).

**Files:** `src/components/source/SourceSnapshotPanel.tsx`, `DataSourceBadge.tsx`

**Implementation:** Framer Motion slide-in from right, mounted in `AppShell`. Triggered by `sourceStore.selectedSourceId`. Shows all fields from PRD §4.5. Includes `DataSourceBadge` (FIRMS/VNF disclosure, fixed requirement per `TECHSTACK.md`).

**Dependency:** Steps 5, 8, 10.

**Verification:** Clicking any map marker opens the panel with correct mock data; closing returns focus to map.

**Expected Result:** P0 feature complete (PRD §4.5).

---

### Step 12 — Filters Panel

**Goal:** Build `FilterPanel.tsx`, wired to `filterStore`.

**Files:** `src/components/filters/FilterPanel.tsx`

**Implementation:** Origin UI form components (select/dropdown/date-range/slider for confidence). Apply button triggers `useSources` refetch with filter params; Reset clears `filterStore`.

**Dependency:** Steps 5, 8.

**Verification:** Applying a filter visibly reduces markers shown on the map (against mock data).

**Expected Result:** P0 feature complete (PRD §4.4).

---

### Step 13 — Charts (Activity, Fingerprint, Anomaly)

**Goal:** Build the three Recharts-based components.

**Files:** `src/components/charts/*`

**Implementation:** `ActivityTimelineChart` (bar + line combo), `ThermalFingerprintChart` (histogram + best-match label), `AnomalyDetectionChart` (dual-line + severity badge). All render inside `SourceSnapshotPanel` or a dedicated detail view.

**Dependency:** Steps 8, 11.

**Verification:** Selecting a source populates all three charts with its mock history/fingerprint/anomaly data.

**Expected Result:** P0 feature complete (PRD §4.6, 4.7, 4.8).

---

### Step 14 — Nearby Facilities & Satellite Context

**Goal:** Build the remaining P1 components.

**Files:** `src/components/tables/NearbyFacilitiesTable.tsx`, `src/components/satellite/SatelliteContextViewer.tsx`

**Implementation:** Origin UI table for facilities. Satellite viewer shows a static mock image with a thermal-overlay toggle (real Sentinel-2/Prithvi-EO integration is backend/data-dependent, `TBD`).

**Dependency:** Step 11.

**Verification:** Both render correctly inside the Source Snapshot panel or Investigation page with mock data.

**Expected Result:** P1 features complete (PRD §4.9, 4.10).

---

### Step 15 — Alerts Center

**Goal:** Build `AlertsList.tsx` and wire to `useAlerts` polling.

**Files:** `src/components/alerts/AlertsList.tsx`, `src/pages/AlertsPage.tsx`

**Implementation:** Origin UI list/badge components. Poll every 30s via React Query `refetchInterval`. Each alert has an "Investigate" button that sets `sourceStore.selectedSourceId` and opens the panel.

**Dependency:** Steps 5, 8, 11.

**Verification:** Alerts list populates from mock data; clicking "Investigate" opens the correct source's snapshot panel.

**Expected Result:** P1 feature complete (PRD §4.11).

---

### Step 16 — Regional Analytics, Reports, System Status (P2, can be static)

**Goal:** Build simplified/static versions of the three lowest-priority sections.

**Files:** `src/pages/ReportsPage.tsx`, regional analytics components, `src/pages/SystemStatusPage.tsx`

**Implementation:** Static/mock UI matching PRD §4.12–4.14 layouts; export buttons show a "Coming soon" or trigger a mock download; System Status shows hardcoded placeholder health values clearly labeled as illustrative.

**Dependency:** Step 8.

**Verification:** Pages render without errors; clearly does not claim live backend connectivity.

**Expected Result:** P2 features present for demo completeness, not fully functional.

---

### Step 17 — Historical Activity Timeline (Kibo UI)

**Goal:** Build `SourceHistoryTimeline.tsx` for Source Investigation.

**Files:** `src/components/timeline/SourceHistoryTimeline.tsx`

**Implementation:** Kibo UI timeline component showing first detected → status changes → last detected, per PRD §4.6/§4.9 history requirements.

**Dependency:** Step 8.

**Verification:** Renders correctly on `InvestigationPage` with mock history data.

**Expected Result:** Rounds out Source Investigation page.

---

### Step 18 — Polish Pass

**Goal:** Apply the UX/UI polish items already agreed on.

**Files:** Various (no new files)

**Implementation:** Loading skeletons for map/charts, empty-state messaging with Reset Filters, hover tooltips on map markers, consistent card elevation/border (no more neon-per-card borders), tabular-nums/mono font applied to all numeric displays, one Framer Motion fade-in on panel open, at most one React Bits decorative effect.

**Dependency:** Steps 9–17.

**Verification:** Manual visual QA against the polish checklist from earlier review.

**Expected Result:** Demo-ready UI.

---

### Step 19 — Restructure Source Snapshot Panel to Match Reference UI

**Goal:** Match the reference dashboard image exactly: the slide-in Source Snapshot panel stays lightweight (core fields only), while Historical Thermal Activity, Thermal Fingerprint, and Anomaly Analysis move out of the panel and become their own cards directly on the Dashboard page (below the map), updating based on whichever source is currently selected. Only Nearby Industrial Facilities and Satellite Context move to being Investigation-page-only (they do not appear on the Dashboard in the reference image at all).

**Files:** `src/components/source/SourceSnapshotPanel.tsx`, `src/pages/DashboardPage.tsx`, new Dashboard-level chart card components (can reuse the existing `ActivityTimelineChart`, `ThermalFingerprintChart`, `AnomalyDetectionChart` components — just render them on the Dashboard page instead of inside the panel).

**Implementation:**
- **`SourceSnapshotPanel.tsx`** — after this change, contains only: the `DataSourceBadge` (Live: FIRMS · Trained on: VNF), the core fields (Source ID, Classification, Industry Subtype, Confidence Score, Persistence Status, Anomaly Level, First Detected, Last Detected, Location, Coordinates), the classification badges row, and the "View Full Investigation →" button. Remove Historical Activity, Thermal Fingerprint, Anomaly Detection, Nearby Industrial Facilities, and Satellite Context from this file entirely.
- **`DashboardPage.tsx`** — add three new cards below the map, in a row (matching the reference layout: Historical Thermal Activity | Thermal Fingerprint | Anomaly Analysis), reusing the exact same `ActivityTimelineChart`, `ThermalFingerprintChart`, and `AnomalyDetectionChart` components already built in Step 13. These cards read `sourceStore.selectedSourceId` and call the same `useSourceHistory`, `useSourceFingerprint`, `useSourceAnomaly` hooks the panel used to call — so they update automatically to show data for whichever source is currently selected on the map. If no source is selected yet, show a sensible default/empty state (e.g., "Select a source on the map to see its activity").
- **Nearby Industrial Facilities and Satellite Context** — remain Investigation-page-only, exactly as `InvestigationPage.tsx` already renders them (built in Step 14). Do not add these two to the Dashboard.

**CRITICAL constraints:**
- Do NOT duplicate the chart components — reuse the existing `ActivityTimelineChart`, `ThermalFingerprintChart`, `AnomalyDetectionChart` components as-is, just changing where they're rendered from (panel → Dashboard page).
- Do NOT modify `InvestigationPage.tsx` or the underlying chart/table/viewer components' internal logic — only change where three of them are mounted.
- Do NOT touch the map, KPI cards, Filters, or the four below-the-map widgets from Step 20 (Recent Alerts, Regional Thermal Sources, Industrial vs Natural, Source Trend) — those are separate, unrelated to this step.
- The "View Full Investigation" button in the panel must still navigate to `/investigation/:sourceId` and that page must still show all five original sections (Historical Activity, Thermal Fingerprint, Anomaly Detection, Nearby Facilities, Satellite Context) in full, unaffected.

**Dependency:** Steps 11, 13, 14.

**Verification:** Clicking a map marker opens a short Source Snapshot panel (core fields + button only, no charts). The Dashboard page itself, below the map, now shows Historical Thermal Activity, Thermal Fingerprint, and Anomaly Analysis cards that update to reflect whichever source was just clicked. Clicking "View Full Investigation" still shows the complete picture including Nearby Facilities and Satellite Context on the Investigation page.

**Expected Result:** Dashboard matches the reference image exactly — map, KPI cards, Source Snapshot panel (lightweight), and three chart cards below the map, all visible together on one screen.

---

## Dashboard Widget Drill-Down Navigation

Added once the full dashboard (Steps 1–19) was verified working. Goal: keep the Dashboard's visual layout and functionality exactly as-is (it already matches the target UI closely), and add navigation only to the widgets **below the map** — Recent Alerts, Regional Thermal Sources, Industrial vs Natural donut, Source Trend table — so each links through to its own dedicated sidebar page for full detail. **KPI cards and the map itself are explicitly excluded from this — they stay exactly as they are, not clickable**, since a KPI count alone doesn't carry enough specific information to justify a dedicated destination page. Backend Integration remains the final step, Step 23.

**Important correction after verification:** a walkthrough of the actual running app found that the Dashboard page currently ends right after the map (and, once Step 19 is done, the three source-scoped chart cards) — it does **not** yet have standalone Recent Alerts, Regional Thermal Sources, Industrial vs Natural, or Source Trend widgets below that. These are separate, always-visible aggregate widgets (not tied to a selected source) and must be built, as Step 20, before any "View details" links can be added to them.

**Guiding rule for Steps 21–22 below:** once Step 20 builds the widgets, adding their links is wrapping/linking changes only. Do not modify any existing data-fetching logic, hooks, chart internals, component props, KPI cards, the map, or the Source Snapshot panel. Do one step at a time; verify the app works exactly as before, plus the new addition, before moving to the next step.

### Widget → Destination Page Mapping (below-the-map widgets only)

| Dashboard widget | Links to |
|---|---|
| Recent Alerts widget | `/alerts` (Alerts Center) |
| Regional Thermal Sources chart | `/assessment` (Event Assessment) |
| Industrial vs Natural donut | `/assessment` (Event Assessment) |
| Source Trend (30 Days) table | `/assessment` (Event Assessment) or dedicated trend view |

---

### Step 20 — Build Dashboard-Level Aggregate Widgets

**Goal:** Build the four below-the-map widgets as standalone, always-visible Dashboard components — aggregating across *all* sources, not scoped to any single selected source. This is new component work, not a wrapping/linking change.

**Files:** `src/pages/DashboardPage.tsx`, new widget components (e.g., `src/components/dashboard/RecentAlertsWidget.tsx`, `RegionalSourcesChart.tsx`, `IndustrialVsNaturalChart.tsx`, `SourceTrendTable.tsx`)

**Implementation:**
- **Recent Alerts widget** — reuse the existing `useAlerts()` hook (from Step 15); render the latest 4 alerts as a compact list with severity badge, source ID, and timestamp, plus a "View All" link to `/alerts`.
- **Regional Thermal Sources chart** — new aggregate bar/list chart, grouping all mock sources by district/state (derive region the same way `sourceService.ts` already does for `district`/`state` in `useSourceDetail` — reuse the `REGIONS` array and `regionForSource` function, do not duplicate this logic). Count of sources per region must sum to exactly `sources.length` (the true total), since every source is assigned to exactly one region.
- **Industrial vs Natural donut chart** — new aggregate donut, summarizing the full `useSources()` dataset. **Use `sources.length` (all categories combined) as the percentage denominator, not a subset of categories** — this was a bug in the first pass, where only Industrial + Natural + Unknown were summed and used as the total, inflating percentages. The donut must have a slice for every category present in the data, not just three: Industrial, Natural/Biomass, Persistent, Abnormal, Unknown, and Gas Flare/FIRMS (or, if simplifying to 3 visual slices for clarity, the third slice must be explicitly labeled "Other" and its tooltip/legend must state it includes Persistent + Abnormal + Gas Flare + New + true Unknown — never leave an "Other"-sized slice mislabeled as just "Unknown"). All slice percentages must sum to 100%.
- **Source Trend (30 Days) table** — new aggregate table listing **every** source category present in the mock data (Industrial, Natural/Biomass, Persistent, Abnormal, Unknown, Gas Flare/FIRMS Detections, and New — do not omit "New," since sources with category `"new"` exist in the mock data and must be counted somewhere) with a real count computed via `sources.filter(...).length` for each category — **no hardcoded or placeholder zero values for any row**. The sum of all row counts must equal `sources.length`. Trend/% change values may use the deterministic mock-generator pattern from `mockGenerators.ts` (seeded by category name) since a 30-day trend isn't computable from a single data snapshot, but the Count column must always be real.

Place all four in a row below the map, matching the reference layout (Recent Alerts | Regional Thermal Sources | Industrial vs Natural in one row, Source Trend below or alongside per the reference image). Do not touch the map, KPI cards, or Source Snapshot panel while building these — they are new, separate components.

**Dependency:** Steps 8, 13, 15, 16.

**Verification:** Dashboard now shows all four widgets below the map, populated with real aggregate mock data (not tied to any single selected source). Cross-check: Regional Thermal Sources counts sum to exactly `sources.length`; Industrial vs Natural donut percentages sum to 100% with every category accounted for (no mislabeled slice); Source Trend table row counts sum to exactly `sources.length` with no category omitted or hardcoded to zero; these totals should also roughly agree with the KPI cards (e.g., Abnormal Sources KPI count should match the Abnormal row in Source Trend).

**Expected Result:** Dashboard visually and functionally matches the target reference image in full — map, KPI cards, and all four below-the-map widgets present and populated.

---

### Step 21 — Remaining Widget Links (Regional Chart, Analytics Table)

**Goal:** Add "View details →" links to the two below-map Dashboard widgets that don't already have one — Regional Thermal Sources chart and Industrial vs Natural donut chart — matching the exact visual style of the "View All" links on Recent Alerts and Source Trend (30 Days), so all four bottom-row cards look visually consistent.

**Files:** `src/pages/DashboardPage.tsx` (or the specific widget card components built in Step 20) — widget card headers only, no chart internals touched.

**Implementation:** Add a "View details →" link into each card's header, styled identically to the "View All" links (same font size, color, position — small accent-colored text aligned to the top-right of the card header), alongside any existing (i) info icon. Both new links navigate to `/assessment`.

**CRITICAL constraints:**
- Only edit `DashboardPage.tsx` (or its Regional Thermal Sources / Industrial vs Natural widget components).
- Do **NOT** add, modify, or reference these links inside `SourceSnapshotPanel.tsx` in any way — that component is unrelated and must not be touched.
- Do **NOT** modify the map, KPI cards, Source Snapshot panel, or any of the three charts inside the Source Snapshot panel (Historical Activity, Thermal Fingerprint, Anomaly Analysis) — those already have their own navigation via "View Full Investigation."
- Do **NOT** change any existing chart logic, data fetching, or info icons already present.
- Keep the overall Dashboard layout, spacing, and every other element pixel-for-pixel identical to how it renders after Step 20.

**Dependency:** Step 20.

**Verification:** The Dashboard looks exactly as it does after Step 20, except Regional Thermal Sources and Industrial vs Natural now also show a "View details →" link in their header. Clicking it navigates to `/assessment`. Confirm the Source Snapshot panel is completely untouched.

**Expected Result:** All four below-the-map widgets (Recent Alerts, Regional Thermal Sources, Industrial vs Natural, Source Trend) consistently link through to their detail pages; Dashboard's map, KPI row, and Source Snapshot panel remain untouched.

---

### Step 22 — Event Assessment Page Content

**Goal:** Build out `/assessment` (Event Assessment page) to show the expanded/full-size version of the Regional Thermal Sources chart and Industrial vs Natural breakdown that the Dashboard links to.

**Files:** `src/pages/AssessmentPage.tsx`

**Implementation:** Reuse the same chart components built in Step 20 (Regional Thermal Sources bar chart, Industrial vs Natural donut) at a larger size, with more detail/more sources listed than the compact Dashboard preview. No new chart logic — just a fuller render of what already exists.

**Dependency:** Step 21.

**Verification:** Navigating to `/assessment` (via the new "View details" links or directly) shows a working, larger version of these charts, not a blank placeholder.

**Expected Result:** Event Assessment page has real content instead of a stub.

---

### Step 23 — Backend Integration (when available)

**Goal:** Replace mock data with real Backend API calls. This is now the final step — done last, after the entire frontend (including the Dashboard widgets and drill-down navigation above) is complete and working end-to-end in mock-data mode.

**Files:** `src/services/*`, `.env.local`

**Implementation:** Set `VITE_API_BASE_URL` to the real backend. Reconcile placeholder types in `types/source.ts` against the actual OpenAPI schema; adjust field names/shapes as needed. Remove mock-data fallback logic once confidence in the real API is established.

**Dependency:** Backend API must exist (out of scope of this document). All prior steps (1–22) must be complete.

**Verification:** Dashboard shows real data end-to-end; no console errors; all P0/P1 features function against live data, including the Dashboard widgets and Event Assessment page built in Steps 20–22.

**Expected Result:** Fully integrated, demo-ready AgniDrishti dashboard.