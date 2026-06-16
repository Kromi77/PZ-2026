export default function Header({ title, subtitle, badge }) {
  return (
    <header className="relative border-b border-white/10 bg-slate-950/55 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            {badge && (
              <span className="mb-4 inline-flex rounded-full border border-violet-300/20 bg-violet-300/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-violet-100">
                {badge}
              </span>
            )}

            <h1 className="text-4xl font-black tracking-tight text-white sm:text-5xl">
              {title}
            </h1>

            {subtitle && (
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
                {subtitle}
              </p>
            )}
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/4 px-4 py-3 text-sm text-slate-300 shadow-xl shadow-black/20">
            <span className="text-slate-500">Tryb:</span>{" "}
            <span className="font-semibold text-emerald-200">BMP / WAV</span>
          </div>
        </div>
      </div>
    </header>
  );
}
