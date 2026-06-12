import SectionHeader from './SectionHeader'

const careerOptions = ['DevOps Engineer', 'Data Analyst', 'Backend Developer', 'Cloud Engineer']

export default function ProfileForm({ data, onChange, onSubmit, onCareerToggle, isLoading }) {
  return (
    <section className="glass-panel glass-border animate-fade-up rounded-[1.5rem] p-5 shadow-[0_24px_80px_rgba(15,23,42,0.24)] xl:sticky xl:top-6">
      <SectionHeader
        eyebrow="Career Intake"
        title="Build your profile"
        description="Enter a quick summary of your background and compare the best-fit career paths."
      />

      <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3">
        <div className="flex items-center justify-between gap-4 text-sm">
          <span className="font-medium text-slate-200">Comparison paths selected</span>
          <span className="rounded-full border border-white/10 bg-slate-950/60 px-3 py-1 text-xs font-semibold text-slate-300">
            {data.selectedCareers.length} active
          </span>
        </div>
        <p className="mt-2 text-xs leading-5 text-slate-400">
          These careers feed the comparison table and keep the recommendation focused.
        </p>
      </div>

      <form className="mt-5 space-y-4" onSubmit={onSubmit}>
        <label className="block space-y-2">
          <span className="text-sm font-medium text-slate-200">Education</span>
          <input
            name="education"
            value={data.education}
            onChange={onChange}
            placeholder="BSc Computer Science, Diploma, Self-taught..."
            className="w-full rounded-[1rem] border border-white/10 bg-slate-950/65 px-4 py-3 text-sm text-white outline-none transition-all duration-200 placeholder:text-slate-500 focus:border-cyan-400/60 focus:bg-slate-950/80 focus:ring-2 focus:ring-cyan-400/20"
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-slate-200">Skills</span>
          <textarea
            name="skills"
            value={data.skills}
            onChange={onChange}
            rows="4"
            placeholder="Python, React, SQL, Git, communication..."
            className="w-full resize-none rounded-[1rem] border border-white/10 bg-slate-950/65 px-4 py-3 text-sm text-white outline-none transition-all duration-200 placeholder:text-slate-500 focus:border-cyan-400/60 focus:bg-slate-950/80 focus:ring-2 focus:ring-cyan-400/20"
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-slate-200">Interests</span>
          <textarea
            name="interests"
            value={data.interests}
            onChange={onChange}
            rows="4"
            placeholder="Web apps, AI, data analysis, product design..."
            className="w-full resize-none rounded-[1rem] border border-white/10 bg-slate-950/65 px-4 py-3 text-sm text-white outline-none transition-all duration-200 placeholder:text-slate-500 focus:border-cyan-400/60 focus:bg-slate-950/80 focus:ring-2 focus:ring-cyan-400/20"
          />
        </label>

        <fieldset className="space-y-3 rounded-[1rem] border border-white/10 bg-white/[0.03] p-4">
          <legend className="text-sm font-medium text-slate-200">Career comparison paths</legend>
          <p className="text-xs leading-5 text-slate-400">
            Select the careers you want to compare. If none are selected, the backend compares all four.
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            {careerOptions.map((career) => (
              <label
                key={career}
                className={`flex cursor-pointer items-center gap-3 rounded-[1rem] border px-4 py-3 text-sm transition-all duration-200 ${
                  data.selectedCareers.includes(career)
                    ? 'border-cyan-400/30 bg-cyan-400/10 text-white shadow-[0_10px_24px_rgba(8,145,178,0.12)]'
                    : 'border-white/10 bg-slate-950/45 text-slate-200 hover:border-white/20 hover:bg-white/[0.06]'
                }`}
              >
                <input
                  type="checkbox"
                  checked={data.selectedCareers.includes(career)}
                  onChange={() => onCareerToggle(career)}
                  className="h-4 w-4 rounded border-white/20 bg-slate-950 text-cyan-400 focus:ring-cyan-300"
                />
                <span>{career}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex w-full items-center justify-center gap-3 rounded-[1rem] bg-gradient-to-r from-cyan-300 via-sky-400 to-indigo-500 px-5 py-3.5 text-sm font-semibold text-slate-950 shadow-[0_18px_50px_rgba(14,165,233,0.22)] transition-all duration-200 hover:-translate-y-0.5 hover:scale-[1.01] hover:brightness-110 active:translate-y-0 active:scale-[0.99] focus:outline-none focus:ring-2 focus:ring-cyan-300/60 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0 disabled:hover:scale-100"
        >
          {isLoading ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950/30 border-t-slate-950" />
          ) : null}
          {isLoading ? 'Generating...' : 'Generate Career Plan'}
        </button>
      </form>
    </section>
  )
}