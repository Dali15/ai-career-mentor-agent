function SkeletonLine({ className = '' }) {
  return <div className={`animate-pulse rounded-full bg-white/10 ${className}`} />
}

function SkeletonCard({ className = '' }) {
  return (
    <div className={`glass-panel glass-border rounded-[1.5rem] p-5 ${className}`} aria-hidden="true">
      <div className="mb-5 flex items-center gap-3">
        <SkeletonLine className="h-3 w-3 rounded-full bg-white/20" />
        <SkeletonLine className="h-4 w-32" />
      </div>
      <div className="space-y-3">
        <SkeletonLine className="h-7 w-3/5" />
        <SkeletonLine className="h-4 w-full" />
        <SkeletonLine className="h-4 w-11/12" />
      </div>
    </div>
  )
}

export default function ResultsSkeleton() {
  return (
    <div className="space-y-6" aria-label="Loading career results">
      <div className="glass-panel glass-border animate-fade-up rounded-[1.5rem] p-5" aria-hidden="true">
        <div className="flex flex-col gap-6 lg:grid lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)] lg:items-center">
          <div className="mx-auto h-32 w-32 rounded-full bg-white/10 md:h-36 md:w-36" />
          <div className="space-y-3">
            <SkeletonLine className="h-3 w-44" />
            <SkeletonLine className="h-8 w-64 rounded-2xl" />
            <SkeletonLine className="h-4 w-full" />
            <SkeletonLine className="h-4 w-5/6" />
            <div className="grid gap-3 sm:grid-cols-3">
              <SkeletonLine className="h-20 rounded-[1rem]" />
              <SkeletonLine className="h-20 rounded-[1rem]" />
              <SkeletonLine className="h-20 rounded-[1rem]" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <SkeletonCard className="xl:col-span-2" />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard className="xl:col-span-2" />
        <SkeletonCard className="xl:col-span-2" />
      </div>
    </div>
  )
}