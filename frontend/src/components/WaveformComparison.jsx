import React, { useState } from "react";
import WaveformCanvas from "./common/WaveformCanvas";
import WaveformModal from "./common/WaveformModal";
import { useWaveform } from "../hooks/useWaveform";

function WaveformCard({
  title,
  waveformData,
  isLoading,
  error,
  color,
  onOpen,
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
      <p className="mb-2 text-sm font-semibold text-slate-300">{title}</p>

      <button
        type="button"
        onClick={onOpen}
        disabled={isLoading || !waveformData}
        className="block w-full rounded-md transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-70"
      >
        <WaveformCanvas
          waveformData={waveformData}
          height={120}
          color={color}
          backgroundColor="#f3f4f6"
          isLoading={isLoading}
          clickable={Boolean(waveformData)}
        />
      </button>

      {error ? (
        <p className="mt-2 text-xs leading-relaxed text-red-400">{error}</p>
      ) : (
        <p className="mt-2 text-xs text-slate-500">🔍 Kliknij aby powiększyć</p>
      )}
    </div>
  );
}

export default function WaveformComparison({ originalFile, encodedFile }) {
  const {
    waveformData: originalWaveform,
    isLoading: originalLoading,
    error: originalError,
  } = useWaveform(originalFile);

  const {
    waveformData: encodedWaveform,
    isLoading: encodedLoading,
    error: encodedError,
  } = useWaveform(encodedFile);

  const [selectedWaveform, setSelectedWaveform] = useState(null);
  const [selectedTitle, setSelectedTitle] = useState("");
  const [selectedColor, setSelectedColor] = useState("#3b82f6");
  const [selectedLoading, setSelectedLoading] = useState(false);
  const [selectedError, setSelectedError] = useState(null);

  function openModal({ waveform, title, color, isLoading, error }) {
    setSelectedWaveform(waveform);
    setSelectedTitle(title);
    setSelectedColor(color);
    setSelectedLoading(isLoading);
    setSelectedError(error);
  }

  function closeModal() {
    setSelectedWaveform(null);
    setSelectedTitle("");
    setSelectedColor("#3b82f6");
    setSelectedLoading(false);
    setSelectedError(null);
  }

  if (!originalFile && !encodedFile) {
    return null;
  }

  const hasBothFiles = originalFile && encodedFile;

  return (
    <div className="mt-6 w-full space-y-4">
      <h3 className="text-lg font-semibold text-white">Porównanie Oscylogramów</h3>

      <div className={hasBothFiles ? "grid grid-cols-1 gap-4 lg:grid-cols-2" : "grid grid-cols-1 gap-4"}>
        {originalFile && (
          <WaveformCard
            title="Przed kodowaniem"
            waveformData={originalWaveform}
            isLoading={originalLoading}
            error={originalError}
            color="#10b981"
            onOpen={() =>
              openModal({
                waveform: originalWaveform,
                title: "Oscylogram - Przed kodowaniem",
                color: "#10b981",
                isLoading: originalLoading,
                error: originalError,
              })
            }
          />
        )}

        {encodedFile && (
          <WaveformCard
            title="Po kodowaniu"
            waveformData={encodedWaveform}
            isLoading={encodedLoading}
            error={encodedError}
            color="#f59e0b"
            onOpen={() =>
              openModal({
                waveform: encodedWaveform,
                title: "Oscylogram - Po kodowaniu",
                color: "#f59e0b",
                isLoading: encodedLoading,
                error: encodedError,
              })
            }
          />
        )}
      </div>

      {originalFile && encodedFile && (
        <div className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
          <p className="text-center text-xs text-slate-500">
            💡 Oscylogramy powinny wyglądać prawie identycznie - steganografia LSB zmienia tylko najmniej znaczące bity
          </p>
        </div>
      )}

      <WaveformModal
        isOpen={selectedWaveform !== null}
        onClose={closeModal}
        title={selectedTitle}
      >
        <div className="rounded-lg bg-white p-4">
          {selectedError ? (
            <p className="text-sm text-red-600">{selectedError}</p>
          ) : (
            <WaveformCanvas
              waveformData={selectedWaveform}
              height={320}
              color={selectedColor}
              backgroundColor="#f3f4f6"
              isLoading={selectedLoading}
            />
          )}
        </div>
      </WaveformModal>
    </div>
  );
}
