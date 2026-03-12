import { Outlet } from "react-router-dom";

export default function AppShell() {
  return (
    <div className="min-h-screen bg-sand text-ink">
      <div className="pointer-events-none fixed inset-0 bg-grid bg-[size:42px_42px] opacity-40" />
      <div className="pointer-events-none fixed inset-x-0 top-0 h-80 bg-[radial-gradient(circle_at_top,rgba(217,122,58,0.22),transparent_55%)]" />
      <div className="pointer-events-none fixed inset-y-0 right-0 w-80 bg-[radial-gradient(circle_at_center,rgba(31,108,99,0.16),transparent_60%)]" />
      <Outlet />
    </div>
  );
}
