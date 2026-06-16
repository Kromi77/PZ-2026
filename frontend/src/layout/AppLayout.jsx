import Header from "./Header";

export default function AppLayout({ title, subtitle, badge, children }) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute -left-40 -top-40 h-96 w-96 rounded-full bg-violet-500/20 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-48 -right-32 h-112 w-md rounded-full bg-emerald-400/10 blur-3xl" />

      <div className="relative z-10 flex min-h-screen flex-col">
        <Header title={title} subtitle={subtitle} badge={badge} />

        <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-5 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          {children}
        </main>
      </div>
    </div>
  );
}
