export default function SliderControl({
  label,
  value,
  onChange,
  min = 0,
  max = 8,
}) {
  const percentage = ((Number(value) - min) / (max - min)) * 100;

  return (
    <div className="w-full rounded-2xl border border-white/10 bg-slate-950/35 p-4 shadow-inner shadow-black/20">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <label className="block text-sm font-semibold text-slate-100">
            {label}
          </label>
        </div>

        <span className="flex h-8 min-w-10 items-center justify-center rounded-full border border-violet-300/20 bg-violet-300/15 px-3 text-sm font-bold text-violet-100 shadow-sm shadow-violet-950/30">
          {value}
        </span>
      </div>

      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step="1"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="custom-range-slider h-2 w-full cursor-pointer appearance-none rounded-full"
          style={{
            background: `linear-gradient(to right, rgb(167 139 250) 0%, rgb(167 139 250) ${percentage}%, rgb(51 65 85) ${percentage}%, rgb(51 65 85) 100%)`,
          }}
        />

        <div className="mt-3 flex justify-between text-[11px] font-medium text-slate-600">
          <span>{min}</span>
          <span>{max}</span>
        </div>
      </div>
    </div>
  );
}
