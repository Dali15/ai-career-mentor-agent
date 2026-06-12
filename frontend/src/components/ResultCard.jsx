import SectionHeader from './SectionHeader'

export default function ResultCard({ title, eyebrow = 'Analysis', description, accent, className = '', children }) {
  return (
    <article className={`group relative overflow-hidden rounded-[1.5rem] border border-white/10 bg-white/[0.05] p-6 shadow-[0_24px_80px_rgba(15,23,42,0.22)] transition-all duration-300 hover:-translate-y-0.5 hover:border-white/20 hover:bg-white/[0.07] animate-fade-up ${className}`}>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.08),transparent_38%)] opacity-80" />
      <div className="relative">
        <SectionHeader eyebrow={eyebrow} title={title} description={description} accent={accent} />
        <div className="mt-5">{children}</div>
      </div>
    </article>
  )
}