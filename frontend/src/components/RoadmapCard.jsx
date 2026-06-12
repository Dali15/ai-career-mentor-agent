import ResultCard from './ResultCard'

function RoadmapMonth({ title, items }) {
  return (
    <div className="rounded-[1rem] border border-white/10 bg-white/[0.04] p-4">
      <div className="flex items-center gap-3">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-r from-sky-400 to-indigo-500 text-xs font-semibold text-slate-950">
          {title.split(' ')[1]}
        </span>
        <div>
          <h4 className="text-sm font-semibold text-white">{title}</h4>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Roadmap stage</p>
        </div>
      </div>
      <ul className="mt-4 space-y-2 text-sm leading-6 text-slate-200">
        {items?.map((item) => (
          <li key={item} className="flex items-start gap-3">
            <span className="mt-2 h-2 w-2 rounded-full bg-sky-300" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function RoadmapCard({ roadmap, className = '' }) {
  return (
    <ResultCard
      eyebrow="Plan"
      title="Learning roadmap"
      description="A simple monthly plan that turns the recommendation into visible progress."
      accent="from-sky-400 to-indigo-500"
      className={className}
    >
      <div className="grid gap-4 md:grid-cols-3">
        <RoadmapMonth title="Month 1" items={roadmap?.month_1} />
        <RoadmapMonth title="Month 2" items={roadmap?.month_2} />
        <RoadmapMonth title="Month 3" items={roadmap?.month_3} />
      </div>
    </ResultCard>
  )
}