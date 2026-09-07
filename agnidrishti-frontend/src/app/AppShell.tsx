import { Outlet } from 'react-router-dom'
import { SourceSnapshotPanel } from '../components/source/SourceSnapshotPanel'
import { Sidebar } from './Sidebar'
import { TopNav } from './TopNav'

export function AppShell() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-bg text-text-primary">
      <div className="z-50 shrink-0">
        <TopNav />
      </div>
      <div className="flex min-h-0 flex-1">
        <Sidebar />
        <main className="main-content-scroll min-h-0 min-w-0 flex-1 overflow-y-auto p-6 md:p-8">
          <Outlet />
        </main>
        <div id="source-snapshot-panel" aria-label="Source snapshot panel">
          <SourceSnapshotPanel />
        </div>
      </div>
    </div>
  )
}
