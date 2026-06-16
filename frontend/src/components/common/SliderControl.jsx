export default function SliderControl({
  label,
  value,
  onChange,
  min = 0,
  max = 8,
}) {
  return (
    <label className="rounded-2xl border border-white/10 bg-white/3 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <span className="text-sm font-semibold text-slate-200">{label}</span>
        <span className="rounded-full bg-violet-300/10 px-3 py-1 text-xs font-bold text-violet-100">
          {value}
        </span>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full cursor-pointer"
      />
    </label>
  );
}
