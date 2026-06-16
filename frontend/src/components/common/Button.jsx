const VARIANT_CLASSES = {
  primary:
    "bg-violet-500 text-white shadow-lg shadow-violet-950/30 hover:bg-violet-400 focus-visible:ring-violet-300",
  success:
    "bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-950/20 hover:bg-emerald-400 focus-visible:ring-emerald-300",
  secondary:
    "border border-white/10 bg-white/10 text-slate-100 hover:bg-white/20 focus-visible:ring-slate-300",
};

export default function Button({
  children,
  type = "button",
  variant = "primary",
  disabled = false,
  className = "",
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={`cursor-pointer inline-flex items-center justify-center rounded-xl px-5 py-3 text-sm font-semibold tracking-wide transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50 ${VARIANT_CLASSES[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
