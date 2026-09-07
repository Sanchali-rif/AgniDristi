# PRD.md — AgniDrishti Frontend

## 1. Product Summary

AgniDrishti is an AI-enabled geospatial dashboard for detecting and classifying industrial fires and persistent thermal sources (SIH 2026, PS ID 26162, NTRO). This document scopes the **frontend dashboard only** — the operator-facing web application that visualizes output from the Backend API (FastAPI), which itself sits on top of the DBSCAN → thermal fingerprinting → Mann-Kendall → KNN/XGBoost ensemble pipeline defined in the Technical Approach.

The frontend does not run any ML/geospatial processing itself. It consumes structured JSON from the Backend API and renders it as an interactive intelligence dashboard for NTRO/CPCB/SPCB/NDMA users.

## 2. Target Users

| User | Need |
|---|---|
| NTRO analyst | Monitor persistent/abnormal thermal sources near critical infrastructure |
| CPCB/SPCB officer | Verify industrial compliance, flag unregistered facilities |
| NDMA / disaster management | Early risk detection, regional situation overview |
| SIH evaluators/judges | See a working, coherent, credible demo of the full pipeline's output |

## 3. Scope (Frontend Only)

In scope: dashboard UI, map visualization, filters/search, charts, alerts, static/mock intelligence reports, admin/model status display.
Out of scope: backend API implementation, ML training/inference, database design, auth server (frontend assumes a login screen exists but auth logic is `TBD` pending backend).

## 4. Feature List

Derived directly from the confirmed 15-section feature list. Each maps to one or more frontend components (see `ARCHITECTURE.md` §5).

### 4.1 Top Navigation Bar
- Logo/name, dashboard title, global search, notifications bell, admin profile, system status indicator.

### 4.2 KPI Cards
- Total Sources, Persistent Sources, New Sources, Abnormal Sources, Industrial Sources, High-Risk Alerts. Each shows value + trend delta.

### 4.3 Interactive GIS Map
- Renders FIRMS thermal detections color/shape-coded by category: Industrial, Persistent, New, Abnormal, Natural/Biomass, Gas Flare, Unknown.
- Zoom/pan, satellite/map layer toggle, legend, marker clustering (1,000+ points expected).

### 4.4 Search & Filters
- Source ID / location / facility search, date range, source type, industry type, anomaly level, confidence level, persistence status. Apply/Reset.

### 4.5 Source Snapshot
- Detail panel/modal on marker click: Source ID, classification, industry subtype, confidence score, persistence status, anomaly level, first/last detected, coordinates, district/state, "View Full Investigation" link.

### 4.6 Historical Activity
- Detection frequency + avg temperature over time, daily/monthly toggle, trend line.

### 4.7 Thermal Fingerprint
- Temperature-bin histogram, normalized distribution, best-matching industry label, similarity score, classification confidence.

### 4.8 Anomaly Detection
- Historical baseline vs. current activity line chart, anomaly score, severity badge, trend indicator.

### 4.9 Nearby Industrial Facilities
- Table: facility name, type, industry, distance, direction, nearby infrastructure.

### 4.10 Satellite Context
- Sentinel-2 / Prithvi-EO image viewer for the selected source, with thermal overlay toggle.

### 4.11 Alerts
- List: high anomaly, new persistent source, unusual pattern, new industrial source, low-confidence classification. Each with severity, timestamp, source ID, "Investigate" action.

### 4.12 Intelligence Reports
- Regional reports, source investigation reports, anomaly reports. Export: GIS (GeoJSON), CSV, PDF. **Note:** actual export generation is backend-driven; frontend triggers request + downloads result. Marked `TBD` pending backend contract — build as a static/mock UI first.

### 4.13 Regional Analytics
- Sources by region, sources by industry, industrial vs. natural split, persistent vs. transient, abnormal-source stats, thermal activity trends. Chart-heavy, aggregate view.

### 4.14 Admin / Model Status
- Data status (FIRMS last update, satellite data availability), API status, DB status, model version, classification performance (accuracy/precision/recall/F1), system health. **Note:** mostly backend-reported; build as a static/mock status panel first.

### 4.15 Sidebar Navigation
- Dashboard, Search & Discovery, Source Investigation, Event Assessment, Change & Anomaly, Intelligence Reports, Alerts, Data Layers, System/Model.

## 5. Priority for Build (Hackathon Time Constraint)

| Priority | Sections |
|---|---|
| P0 (must work, fully interactive) | 4.1–4.8 (nav, KPIs, map, filters, snapshot, activity, fingerprint, anomaly) |
| P1 (should work) | 4.9, 4.10, 4.11 (nearby facilities, satellite context, alerts) |
| P2 (can be static/mock for demo) | 4.12, 4.13, 4.14 (reports, regional analytics, admin/model status) |
| P3 (structural, low effort) | 4.15 (sidebar nav) |

## 6. Data Source Disclosure Requirement

Per project constraints already established: the dashboard must visually distinguish **FIRMS (daily monitoring feed)** from **VNF (training-only, not live)**, and must not imply real-time or sub-750m-resolution detection anywhere in the UI (tooltips/labels required — see `ARCHITECTURE.md` §4 Design System).

## 7. Open Items (TBD)

- Design tokens: proposed in `ARCHITECTURE.md` §4, pending final confirmation.
- Backend API contract / data shape: no sample response available yet; placeholder TypeScript types defined in `ARCHITECTURE.md` §7, to be replaced once backend is ready.
- Auth flow: login screen assumed to exist; token handling `TBD` pending backend.
- Component-to-UI-library mapping: proposed in `ARCHITECTURE.md` §6, pending confirmation.
