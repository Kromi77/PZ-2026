export default function FormField({ label, hint, children }) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-sm font-semibold text-slate-200">{label}</span>
      {children}
      {hint && <span className="text-xs leading-relaxed text-slate-400">{hint}</span>}
    </label>
  )
}
