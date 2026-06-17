import React, { useEffect } from "react";
import { createPortal } from "react-dom";

export default function WaveformModal({
  isOpen,
  onClose,
  title,
  children,
  panelClassName = "",
  bodyClassName = "",
}) {
  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    const previousOverflow = document.body.style.overflow;

    function handleEscape(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("keydown", handleEscape);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = previousOverflow;
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  function handleBackdropMouseDown(event) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }

  const modal = (
    <div
      className="fixed inset-0 z-[999999] flex items-center justify-center overflow-hidden bg-black/80 p-4 backdrop-blur-sm"
      style={{
        width: "100vw",
        height: "100dvh",
      }}
      onMouseDown={handleBackdropMouseDown}
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div
        className={`flex max-h-[calc(100dvh-2rem)] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-white/10 bg-slate-900 shadow-2xl shadow-black/60 ${panelClassName}`}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex shrink-0 items-center justify-between border-b border-white/10 px-5 py-4 sm:px-6">
          <h2 className="text-xl font-bold text-white">{title}</h2>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 transition hover:bg-white/10 hover:text-white"
            aria-label="Zamknij"
          >
            <svg
              className="h-6 w-6"
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

        <div
          className={`min-h-0 flex-1 overflow-auto px-5 py-5 sm:px-6 ${bodyClassName}`}
        >
          {children}
        </div>
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}
