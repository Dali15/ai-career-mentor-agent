import SectionHeader from './SectionHeader'

export default function LoadingState({ steps = [], activeStep = 0 }) {
  const progress = steps.length > 1 ? ((activeStep + 1) / steps.length) * 100 : 25

  return (
    <section className="glass-panel glass-border animate-fade-up rounded-[1.5rem] border-cyan-400/20 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.24)]">
      <SectionHeader
        eyebrow="Processing"
        title="Building a structured career plan"
        description="The agent is analyzing strengths, gaps, career fit, and a learning roadmap."
      />

      <div className="mt-5">
        <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-sky-400 to-indigo-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4" aria-live="polite" aria-busy="true">
          {steps.map((step, index) => {
            const isActive = index === activeStep
            const isComplete = index < activeStep

            return (
              <div
                key={step}
                className={`animate-fade-up rounded-[1rem] border px-4 py-4 transition-all duration-200 ${
                  isActive ? 'border-cyan-400/30 bg-cyan-400/10 shadow-[0_12px_30px_rgba(8,145,178,0.12)]' : 'border-white/10 bg-white/[0.04]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${
                      isComplete ? 'bg-emerald-400/20 text-emerald-200' : isActive ? 'bg-cyan-400/20 text-cyan-100' : 'bg-white/5 text-slate-400'
                    }`}
                  >
                    {index + 1}
                  </span>
                  <div>
                    <p className={`text-sm font-medium ${isActive ? 'text-white' : 'text-slate-300'}`}>{step}</p>
                    <p className="text-xs leading-5 text-slate-400">
                      {isComplete ? 'Completed' : isActive ? 'In progress' : 'Queued'}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <p className="mt-4 text-xs leading-5 text-slate-400">
          The stepper mirrors the backend reasoning flow so the loading state feels like an active agent.
        </p>
      </div>
    </section>
  )
}