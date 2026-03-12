export function LoadingScreen({ label = "Loading application..." }: { label?: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="panel flex w-full max-w-md flex-col items-center gap-4 p-8 text-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-ink/10 border-t-ember" />
        <p className="font-display text-2xl font-bold">Resume Analyzer</p>
        <p className="text-sm text-ink/60">{label}</p>
      </div>
    </div>
  );
}
