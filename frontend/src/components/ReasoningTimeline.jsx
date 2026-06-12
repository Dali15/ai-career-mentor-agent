import ResultCard from './ResultCard'

export default function ReasoningTimeline({ steps }) {
  return (
    <div className="space-y-4">
      <ol className="relative space-y-3 border-l border-white/10 pl-5">
        {steps?.map((step, index) => (
          <li key={step} className="relative">
            <span className="absolute -left-[29px] top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-gradient-to-r from-fuchsia-400 to-violet-500 ring-4 ring-slate-950" />
            <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] px-4 py-4 text-sm leading-6 text-slate-200 transition-colors duration-200 hover:border-white/20 hover:bg-white/[0.06]">
              <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                Step {index + 1}
              </span>
              <p className="text-slate-100">{step}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}