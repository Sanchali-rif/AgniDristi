import { Outlet } from 'react-router-dom'
import { SourceSnapshotPanel } from '../components/source/SourceSnapshotPanel'
import { Sidebar } from './Sidebar'
import { TopNav } from './TopNav'

export function AppShell() {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-bg text-text-primary">
      <div className="z-50 shrink-0">
        <TopNav />
      </div>
      <div className="flex flex-1 min-h-0">
        <Sidebar />
        <main className="flex-1 min-w-0 min-h-0 p-6 overflow-y-auto main-content-scroll md:p-8">
          <Outlet />
        </main>
        <div id="source-snapshot-panel" aria-label="Source snapshot panel">
          <SourceSnapshotPanel />
        </div>
      </div>
    </div>
  )
}
