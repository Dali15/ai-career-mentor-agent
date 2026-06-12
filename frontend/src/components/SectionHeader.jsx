export default function SectionHeader({ eyebrow, title, description, className = '', actions = null }) {
  return (
    <div className={`flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between ${className}`}>
      <div className="space-y-2">
        {eyebrow ? <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200/80">{eyebrow}</p> : null}
        <h2 className="text-xl font-semibold tracking-tight text-white sm:text-[1.45rem]">{title}</h2>
        {description ? <p className="max-w-3xl text-sm leading-6 text-slate-400">{description}</p> : null}
      </div>
      {actions ? <div className="shrink-0">{actions}</div> : null}
    </div>
  )
}