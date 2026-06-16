export default function Alert({ message }) {
  if (!message) {
    return null
  }

  return (
    <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100 shadow-[0_0_40px_rgba(244,63,94,0.08)]">
      <div className="flex gap-3">
        <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-rose-300" />
        <p>{message}</p>
      </div>
    </div>
  )
}
