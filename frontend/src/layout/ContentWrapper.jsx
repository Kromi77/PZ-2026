export default function ContentWrapper({ children }) {
  return (
    <section className="overflow-hidden rounded-4xl border border-white/10 bg-slate-900/80 shadow-2xl shadow-black/40 backdrop-blur-xl">
      {children}
    </section>
  );
}
