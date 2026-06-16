import React, { useState } from "react";
import WaveformCanvas from "./common/WaveformCanvas";
import WaveformModal from "./common/WaveformModal";
import { useWaveform } from "../hooks/useWaveform";

/**
 * Komponent do porównania oscylogramów pliku WAV przed i po kodowaniu
 * Pokazuje waveform oryginalnego i zakodowanego pliku obok siebie
 * Pozwala na powiększenie klikając na oscylogram
 */
export default function WaveformComparison({ originalFile, encodedFile }) {
  const { waveformData: originalWaveform, isLoading: originalLoading } =
    useWaveform(originalFile);
  const { waveformData: encodedWaveform, isLoading: encodedLoading } =
    useWaveform(encodedFile);

  // State dla modala
  const [selectedWaveform, setSelectedWaveform] = useState(null);
  const [selectedTitle, setSelectedTitle] = useState("");
  const [selectedColor, setSelectedColor] = useState("");

  const openModal = (waveform, title, color) => {
    setSelectedWaveform(waveform);
    setSelectedTitle(title);
    setSelectedColor(color);
  };

  const closeModal = () => {
    setSelectedWaveform(null);
    setSelectedTitle("");
    setSelectedColor("");
  };

  if (!originalFile && !encodedFile) {
    return null;
  }

  return (
    <div className="w-full mt-6 space-y-4">
      <h3 className="font-semibold text-lg text-white">
        Porównanie Oscylogramów
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Oscylogram przed */}
        {originalFile && (
          <div className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
            <p className="text-sm font-semibold text-slate-300 mb-2">
              Przed kodowaniem
            </p>
            <div
              className="cursor-pointer"
              onClick={() =>
                openModal(
                  originalWaveform,
                  "Oscylogram - Przed kodowaniem",
                  "#10b981",
                )
              }
            >
              <WaveformCanvas
                waveformData={originalWaveform}
                height={120}
                color="#10b981"
                backgroundColor="#f3f4f6"
                isLoading={originalLoading}
                clickable={true}
              />
            </div>
            <p className="text-xs text-slate-500 mt-2">
              🔍 Kliknij aby powiększyć
            </p>
          </div>
        )}

        {/* Oscylogram po */}
        {encodedFile && (
          <div className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
            <p className="text-sm font-semibold text-slate-300 mb-2">
              Po kodowaniu
            </p>
            <div
              className="cursor-pointer"
              onClick={() =>
                openModal(
                  encodedWaveform,
                  "Oscylogram - Po kodowaniu",
                  "#f59e0b",
                )
              }
            >
              <WaveformCanvas
                waveformData={encodedWaveform}
                height={120}
                color="#f59e0b"
                backgroundColor="#f3f4f6"
                isLoading={encodedLoading}
                clickable={true}
              />
            </div>
            <p className="text-xs text-slate-500 mt-2">
              🔍 Kliknij aby powiększyć
            </p>
          </div>
        )}
      </div>

      {originalFile && encodedFile && (
        <div className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
          <p className="text-xs text-slate-500 text-center">
            💡 Oscylogramy powinny wyglądać prawie identycznie - steganografia
            LSB zmienia tylko najmniej znaczące bity
          </p>
        </div>
      )}

      {/* Modal z powiększonym oscylogramem */}
      <WaveformModal
        isOpen={selectedWaveform !== null}
        onClose={closeModal}
        title={selectedTitle}
      >
        <div className="rounded-lg bg-white p-4">
          <WaveformCanvas
            waveformData={selectedWaveform}
            height={300}
            color={selectedColor}
            backgroundColor="#f3f4f6"
            isLoading={false}
          />
        </div>
      </WaveformModal>
    </div>
  );
}
