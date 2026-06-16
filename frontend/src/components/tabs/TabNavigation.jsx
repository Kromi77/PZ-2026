export default function TabNavigation({ tabs, activeTab, onTabChange }) {
  return (
    <nav className="rounded-2xl border border-white/10 bg-slate-950/55 p-1.5 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="grid grid-cols-2 gap-1.5">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id

          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`rounded-xl px-4 py-3 text-sm font-bold transition-all duration-200 sm:text-base ${
                isActive
                  ? 'bg-white text-slate-950 shadow-lg shadow-black/20'
                  : 'text-slate-400 hover:bg-white/10 hover:text-slate-100'
              }`}
            >
              {tab.label}
            </button>
          )
        })}
      </div>
    </nav>
  )
}
