/**
 * Home page — Phase 1 scaffold.
 *
 * Full assessment workspace UI is implemented in Phase 6.
 * This page confirms the app is running and displays a placeholder.
 */
export default function HomePage() {
  const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "IP-SAKTI Sahayak";

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-8">
      {/* Status banner */}
      <div className="mb-8 px-4 py-2 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-sm font-medium">
        Phase 1 Scaffold — Functional
      </div>

      {/* Logo / brand */}
      <div className="text-center max-w-2xl">
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
          {appName}
        </h1>
        <p className="mt-3 text-lg text-slate-500">
          Ayurveda IP &amp; Regulatory Intelligence Platform
        </p>
      </div>

      {/* Description */}
      <div className="mt-10 max-w-xl text-center">
        <p className="text-slate-600 leading-relaxed">
          A multilingual, evidence-first decision-support system for Intellectual
          Property and regulatory guidance in Ayurveda — across national and
          international regimes.
        </p>
        <p className="mt-4 text-xs text-slate-400">
          Decision-support only. Not legal advice or official regulatory
          determination.
        </p>
      </div>

      {/* Phase status */}
      <div className="mt-12 grid grid-cols-3 gap-4 text-center text-sm">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <div className="text-green-600 font-semibold">✓ Backend</div>
          <div className="text-slate-500 mt-1">FastAPI running</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <div className="text-green-600 font-semibold">✓ Frontend</div>
          <div className="text-slate-500 mt-1">Next.js running</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <div className="text-amber-600 font-semibold">⬜ Assessment</div>
          <div className="text-slate-500 mt-1">Phase 5</div>
        </div>
      </div>

      {/* API Link */}
      <div className="mt-8 text-sm text-slate-400">
        Backend API docs:{" "}
        <a
          href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-brand-600 underline hover:text-brand-700"
        >
          {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/docs
        </a>
      </div>
    </main>
  );
}
