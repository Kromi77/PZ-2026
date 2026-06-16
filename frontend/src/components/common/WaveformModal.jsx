import React, { useEffect } from "react";

/**
 * Modal do wyświetlania powiększonego oscylogramu
 * Obsługuje zamykanie po Escape i kliknięciu na tło
 */
export default function WaveformModal({ isOpen, onClose, title, children }) {
  useEffect(() => {
    if (!isOpen) return;

    // Zamknij modal na Escape
    const handleEscape = (e) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    // Zapobiegaj scrollowaniu strony gdy modal jest otwarty
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      {/* Tło - zamyka modal po kliknięciu */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Zawartość modala */}
      <div className="relative z-10 w-full max-w-4xl mx-4 rounded-lg bg-slate-900 shadow-2xl border border-white/10">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 p-5 sm:p-6">
          <h2 className="text-xl font-bold text-white">{title}</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition rounded-lg p-1 hover:bg-white/10"
            aria-label="Zamknij"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Zawartość */}
        <div className="p-5 sm:p-6 overflow-y-auto max-h-[80vh]">
          {children}
        </div>

        {/* Hint */}
        <div className="border-t border-white/10 px-5 py-3 sm:px-6 bg-slate-950/50 text-center">
          <p className="text-xs text-slate-500">
            Kliknij poza oscylogram lub naciśnij{" "}
            <kbd className="px-2 py-1 rounded bg-white/10 text-slate-300 font-mono text-xs">
              ESC
            </kbd>{" "}
            aby zamknąć
          </p>
        </div>
      </div>
    </div>
  );
}
