import SectionHeader from './SectionHeader'

function getStrokeColor(score) {
  if (score >= 80) return 'from-emerald-300 to-cyan-300'
  if (score >= 60) return 'from-cyan-300 to-sky-400'
  if (score >= 40) return 'from-amber-300 to-orange-400'
  return 'from-rose-300 to-orange-400'
}

export default function CareerMatchScore({ score = 0, explanation = '', confidenceScore, jobReadyTime, marketDemand, className = '' }) {
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0))
  const strokeOffset = 314 - (314 * safeScore) / 100
  const accent = getStrokeColor(safeScore)

  return (
    <section className={`glass-panel glass-border animate-fade-up rounded-[1.5rem] p-5 shadow-[0_24px_80px_rgba(15,23,42,0.24)] ${className}`}>
      <SectionHeader
        eyebrow="Career Match Score"
        title="Career readiness"
        description="A quick signal of how closely your current profile matches the selected career path."
      />

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)] lg:items-center">
        <div
          className="relative mx-auto h-32 w-32 md:h-36 md:w-36"
          role="progressbar"
          aria-label={`Career readiness ${safeScore} out of 100`}
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={safeScore}
        >
          <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90 transform">
            <circle cx="60" cy="60" r="50" className="fill-none stroke-white/10" strokeWidth="10" />
            <circle
              cx="60"
              cy="60"
              r="50"
              stroke="url(#career-match-gradient)"
              className="fill-none transition-all duration-700 ease-out"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray="314"
              strokeDashoffset={strokeOffset}
              pathLength="314"
            />
            <defs>
              <linearGradient id="career-match-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop
                  offset="0%"
                  stopColor={safeScore >= 80 ? '#86efac' : safeScore >= 60 ? '#67e8f9' : safeScore >= 40 ? '#fcd34d' : '#fda4af'}
                />
                <stop
                  offset="100%"
                  stopColor={safeScore >= 80 ? '#67e8f9' : safeScore >= 60 ? '#38bdf8' : safeScore >= 40 ? '#fb923c' : '#fb7185'}
                />
              </linearGradient>
            </defs>
          </svg>

          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-4xl font-semibold tracking-tight text-white md:text-5xl">{safeScore}</span>
            <span className="text-[0.7rem] font-medium uppercase tracking-[0.24em] text-slate-400">Score</span>
          </div>
        </div>

        <div className="space-y-4">
          <div className={`inline-flex rounded-full bg-gradient-to-r px-3 py-1 text-xs font-semibold tracking-wide text-slate-950 ${accent}`}>
            {safeScore >= 80 ? 'High match' : safeScore >= 60 ? 'Good match' : safeScore >= 40 ? 'Developing match' : 'Early-stage match'}
          </div>

          <p className="max-w-2xl text-sm leading-6 text-slate-300">
            {explanation || 'The profile has been evaluated against the selected career path.'}
          </p>

          <div className="grid gap-3 sm:grid-cols-3">
            {typeof confidenceScore === 'number' ? (
              <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Confidence</p>
                <p className="mt-1 text-lg font-semibold text-white">{confidenceScore}%</p>
              </div>
            ) : null}
            {jobReadyTime ? (
              <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Job-ready</p>
                <p className="mt-1 text-lg font-semibold text-white">{jobReadyTime}</p>
              </div>
            ) : null}
            {marketDemand ? (
              <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Demand</p>
                <p className="mt-1 text-lg font-semibold text-white">{marketDemand}</p>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  )
}