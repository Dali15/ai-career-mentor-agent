import SectionHeader from './SectionHeader'

const PIPELINE_STEPS = [
  {
    id: 'intent',
    name: 'Intent Detection',
    description: 'Parse raw input into canonical skill tokens',
    icon: '🎯',
  },
  {
    id: 'extraction',
    name: 'Skill Extraction',
    description: 'Normalize skills with synonyms & validation',
    icon: '🔍',
  },
  {
    id: 'vector',
    name: 'Vector Construction',
    description: 'Build semantic vectors across 18 dimensions',
    icon: '📊',
  },
  {
    id: 'similarity',
    name: 'Similarity Analysis',
    description: 'Compute cosine similarity (55% weight)',
    icon: '↔️',
  },
  {
    id: 'coverage',
    name: 'Coverage Validation',
    description: 'Check skill coverage (30% weight)',
    icon: '✓',
  },
  {
    id: 'alignment',
    name: 'Alignment Bonus',
    description: 'Apply interest matching (15% weight)',
    icon: '⭐',
  },
  {
    id: 'explanation',
    name: 'Explanation Generation',
    description: 'Build reasoning summaries',
    icon: '💬',
  },
  {
    id: 'recommendation',
    name: 'Final Recommendation',
    description: 'Rank careers & generate roadmap',
    icon: '🎓',
  },
]

export default function PipelineVisualization({ className = '' }) {
  return (
    <section className={`animate-fade-up ${className}`}>
      <SectionHeader
        eyebrow="How It Works"
        title="Recommendation Pipeline"
        description="The multi-stage process that transforms your profile into personalized career recommendations."
      />

      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {PIPELINE_STEPS.map((step, idx) => (
          <div key={step.id} className="relative">
            {/* Card */}
            <div
              className="glass-panel glass-border group relative overflow-hidden rounded-lg p-4 transition-all duration-300 hover:shadow-lg hover:shadow-blue-950/30 h-full"
              style={{
                animationDelay: `${idx * 100}ms`,
              }}
            >
              {/* Step Number */}
              <div className="mb-3 inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-500/20 border border-blue-500/40">
                <span className="text-sm font-bold text-blue-300">{idx + 1}</span>
              </div>

              {/* Icon */}
              <div className="text-3xl mb-2">{step.icon}</div>

              {/* Title */}
              <h4 className="text-sm font-semibold text-white">{step.name}</h4>

              {/* Description */}
              <p className="mt-2 text-xs leading-relaxed text-slate-400">
                {step.description}
              </p>

              {/* Hover effect */}
              <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-blue-500/0 via-transparent to-white/0 opacity-0 transition-opacity duration-300 group-hover:opacity-10" />
            </div>

            {/* Connector Arrow - only for non-last items */}
            {idx < PIPELINE_STEPS.length - 1 && (
              <div className="hidden lg:block absolute -right-4 top-1/2 -translate-y-1/2">
                <div className="w-8 h-0.5 bg-gradient-to-r from-blue-500/50 to-transparent" />
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-blue-500" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Scoring Formula */}
      <div className="mt-8 glass-panel glass-border rounded-lg p-6">
        <h4 className="font-semibold text-white mb-4">Hybrid Scoring Formula</h4>
        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded bg-blue-500/20 text-blue-300 font-semibold text-xs">55%</span>
            <span className="text-slate-300"><strong>Cosine Similarity:</strong> How well your vector aligns with the career vector</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded bg-green-500/20 text-green-300 font-semibold text-xs">30%</span>
            <span className="text-slate-300"><strong>Coverage Score:</strong> How many required dimensions you cover</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center justify-center h-8 w-8 rounded bg-yellow-500/20 text-yellow-300 font-semibold text-xs">15%</span>
            <span className="text-slate-300"><strong>Alignment Bonus:</strong> Boost if interests match, max +5 points if within 10 points</span>
          </div>
        </div>
      </div>
    </section>
  )
}
