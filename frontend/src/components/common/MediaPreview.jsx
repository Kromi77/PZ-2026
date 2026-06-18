import React, { useEffect, useMemo, useState } from "react";
import { UI_TEXT } from "../../i18n";
import { useWaveform } from "../../hooks/useWaveform";
import WaveformCanvas from "./WaveformCanvas";
import WaveformModal from "./WaveformModal";

function normalizeMediaType(mediaType) {
  return String(mediaType || "").toLowerCase();
}

function isWavHeader(bytes) {
  if (bytes.length < 12) {
    return false;
  }

  const riff = String.fromCharCode(...bytes.slice(0, 4));
  const wave = String.fromCharCode(...bytes.slice(8, 12));

  return (riff === "RIFF" || riff === "RIFX") && wave === "WAVE";
}

function stripAdhrChunkFromWavBuffer(arrayBuffer) {
  const bytes = new Uint8Array(arrayBuffer);

  if (!isWavHeader(bytes)) {
    return arrayBuffer;
  }

  let adhrIndex = -1;

  for (let i = 12; i <= bytes.length - 4; i += 1) {
    const isAdhr =
      bytes[i] === 0x61 &&
      bytes[i + 1] === 0x64 &&
      bytes[i + 2] === 0x68 &&
      bytes[i + 3] === 0x72;

    if (isAdhr) {
      adhrIndex = i;
      break;
    }
  }

  if (adhrIndex === -1 || adhrIndex + 8 > bytes.length) {
    return arrayBuffer;
  }

  const view = new DataView(arrayBuffer);
  const chunkSize = view.getUint32(adhrIndex + 4, true);
  const chunkTotalSize = 8 + chunkSize;

  if (adhrIndex + chunkTotalSize > bytes.length) {
    return arrayBuffer;
  }

  const restored = new Uint8Array(bytes.length - chunkTotalSize);

  restored.set(bytes.slice(0, adhrIndex), 0);
  restored.set(bytes.slice(adhrIndex + chunkTotalSize), adhrIndex);

  const restoredView = new DataView(restored.buffer);
  const originalRiffSize = view.getUint32(4, true);
  restoredView.setUint32(4, originalRiffSize - chunkTotalSize, true);

  return restored.buffer;
}

export default function MediaPreview({ file, label, mediaType }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);

  const normalizedMediaType = normalizeMediaType(mediaType);

  const isBmp =
    normalizedMediaType === "bmp" ||
    normalizedMediaType.includes("bmp") ||
    normalizedMediaType.includes("image");

  const isWav =
    normalizedMediaType === "wav" ||
    normalizedMediaType.includes("wav") ||
    normalizedMediaType.includes("audio");

  useEffect(() => {
    let cancelled = false;

    async function preparePreviewFile() {
      if (!file) {
        setPreviewFile(null);
        return;
      }

      if (!isWav) {
        setPreviewFile(file);
        return;
      }

      try {
        const arrayBuffer = await file.arrayBuffer();
        const previewBuffer = stripAdhrChunkFromWavBuffer(arrayBuffer);

        if (cancelled) {
          return;
        }

        setPreviewFile(
          new File([previewBuffer], file.name, {
            type: file.type || "audio/wav",
          }),
        );
      } catch {
        if (!cancelled) {
          setPreviewFile(file);
        }
      }
    }

    preparePreviewFile();

    return () => {
      cancelled = true;
    };
  }, [file, isWav]);

  const fileUrl = useMemo(() => {
    if (!previewFile) {
      return null;
    }

    return URL.createObjectURL(previewFile);
  }, [previewFile]);

  const { waveformData, isLoading, error } = useWaveform(
    isWav ? previewFile : null,
  );

  useEffect(() => {
    return () => {
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
      }
    };
  }, [fileUrl]);

  useEffect(() => {
    setIsModalOpen(false);
  }, [file]);

  if (!file || !previewFile || !fileUrl) {
    return null;
  }

  return (
    <>
      <div className="mt-4 flex w-full flex-col items-center gap-2">
        <h3 className="text-lg font-semibold">{label}</h3>

        {isBmp ? (
          <div className="w-full">
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="group flex w-full items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-slate-950/40 p-2 transition hover:border-violet-300/40 hover:bg-white/5"
            >
              <img
                src={fileUrl}
                alt={label}
                className="mx-auto block max-h-[300px] max-w-full rounded-xl object-contain shadow"
              />
            </button>

            <p className="mt-2 text-center text-xs text-slate-500">
              🔍 Kliknij aby powiększyć
            </p>
          </div>
        ) : isWav ? (
          <div className="w-full">
            {error && <div className="mb-2 text-sm text-red-500">{error}</div>}

            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="block w-full cursor-pointer rounded-2xl border border-white/10 bg-slate-950/40 p-2 transition hover:border-violet-300/40 hover:bg-white/5"
            >
              <WaveformCanvas
                waveformData={waveformData}
                height={150}
                color="#3b82f6"
                isLoading={isLoading}
                clickable
              />
            </button>

            <p className="mt-1 text-center text-xs text-slate-500">
              🔍 Kliknij aby powiększyć
            </p>

            <audio controls src={fileUrl} className="mt-3 w-full">
              {UI_TEXT.mediaPreview.audioNotSupported}
            </audio>
          </div>
        ) : (
          <audio controls src={fileUrl} className="mt-2 w-full">
            {UI_TEXT.mediaPreview.audioNotSupported}
          </audio>
        )}
      </div>

      <WaveformModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={label}
        panelClassName={isBmp ? "max-w-[min(94vw,1100px)]" : ""}
        bodyClassName={isBmp ? "flex items-center justify-center" : ""}
      >
        {isBmp ? (
          <div className="flex h-full max-h-[calc(100dvh-8rem)] w-full items-center justify-center overflow-auto rounded-2xl bg-white/5 p-4">
            <img
              src={fileUrl}
              alt={label}
              className="block h-auto max-h-[calc(100dvh-12rem)] max-w-full rounded-xl object-contain shadow-2xl"
            />
          </div>
        ) : (
          <div className="rounded-lg bg-white p-4">
            <WaveformCanvas
              waveformData={waveformData}
              height={300}
              color="#3b82f6"
              backgroundColor="#f3f4f6"
              isLoading={isLoading}
            />
          </div>
        )}
      </WaveformModal>
    </>
  );
}
