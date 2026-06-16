export default function TabNavigation({ tabs, activeTab, onTabChange }) {
  return (
    <nav className="rounded-2xl border border-white/10 bg-slate-950/60 p-1.5 shadow-xl shadow-black/20 backdrop-blur-xl">
      <div
        className="grid gap-1.5"
        style={{
          gridTemplateColumns: `repeat(${tabs.length}, minmax(0, 1fr))`,
        }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              type="button"
              aria-pressed={isActive}
              onClick={() => onTabChange(tab.id)}
              className={`group relative overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold tracking-tight transition-all duration-300 sm:text-base ${
                isActive
                  ? "bg-white/8 text-white shadow-inner shadow-white/5"
                  : "text-slate-400 hover:bg-white/6 hover:text-slate-100"
              }`}
            >
              <span className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                <span className="absolute inset-x-6 top-0 h-px bg-linear-to-r from-transparent via-white/25 to-transparent" />
                <span className="absolute inset-x-8 bottom-0 h-px bg-linear-to-r from-transparent via-violet-400/25 to-transparent" />
              </span>

              <span className="relative z-10 transition-transform duration-300 group-hover:-translate-y-px">
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
