import { useEffect, useState } from "react";

function readAscii(bytes, start, length) {
  return String.fromCharCode(...bytes.slice(start, start + length));
}

function isWavBuffer(arrayBuffer) {
  const bytes = new Uint8Array(arrayBuffer);

  if (bytes.length < 12) {
    return false;
  }

  const riff = readAscii(bytes, 0, 4);
  const wave = readAscii(bytes, 8, 4);

  return (riff === "RIFF" || riff === "RIFX") && wave === "WAVE";
}

function findChunk(bytes, chunkName) {
  const target = Array.from(chunkName).map((char) => char.charCodeAt(0));

  for (let i = 12; i <= bytes.length - 4; i += 1) {
    if (
      bytes[i] === target[0] &&
      bytes[i + 1] === target[1] &&
      bytes[i + 2] === target[2] &&
      bytes[i + 3] === target[3]
    ) {
      return i;
    }
  }

  return -1;
}

function stripAdhrChunk(arrayBuffer) {
  const bytes = new Uint8Array(arrayBuffer);

  if (!isWavBuffer(arrayBuffer)) {
    return arrayBuffer;
  }

  const adhrIndex = findChunk(bytes, "adhr");

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

function downsample(samples, maxSamples = 2000) {
  if (!samples.length) {
    return [];
  }

  const step = Math.max(1, Math.floor(samples.length / maxSamples));
  const result = [];

  for (let i = 0; i < samples.length; i += step) {
    result.push(samples[i]);
  }

  return result;
}

function parseWavManually(arrayBuffer) {
  const bytes = new Uint8Array(arrayBuffer);
  const view = new DataView(arrayBuffer);

  if (!isWavBuffer(arrayBuffer)) {
    throw new Error("To nie jest poprawny plik WAV");
  }

  const fmtIndex = findChunk(bytes, "fmt ");
  const dataIndex = findChunk(bytes, "data");

  if (fmtIndex === -1) {
    throw new Error("Nie znaleziono sekcji fmt w pliku WAV");
  }

  if (dataIndex === -1) {
    throw new Error("Nie znaleziono sekcji data w pliku WAV");
  }

  const audioFormat = view.getUint16(fmtIndex + 8, true);
  const channels = view.getUint16(fmtIndex + 10, true);
  const bitsPerSample = view.getUint16(fmtIndex + 22, true);

  const dataSize = view.getUint32(dataIndex + 4, true);
  const dataStart = dataIndex + 8;
  const dataEnd = Math.min(dataStart + dataSize, bytes.length);

  if (channels < 1) {
    throw new Error("Nieprawidłowa liczba kanałów audio");
  }

  const bytesPerSample = bitsPerSample / 8;
  const frameSize = bytesPerSample * channels;

  if (!Number.isInteger(bytesPerSample) || bytesPerSample <= 0) {
    throw new Error("Nieobsługiwana głębia bitowa WAV");
  }

  const samples = [];

  for (
    let offset = dataStart;
    offset + frameSize <= dataEnd;
    offset += frameSize
  ) {
    let sample = 0;

    if (audioFormat === 1 && bitsPerSample === 8) {
      sample = (view.getUint8(offset) - 128) / 128;
    } else if (audioFormat === 1 && bitsPerSample === 16) {
      sample = view.getInt16(offset, true) / 32768;
    } else if (audioFormat === 1 && bitsPerSample === 24) {
      const b0 = view.getUint8(offset);
      const b1 = view.getUint8(offset + 1);
      const b2 = view.getUint8(offset + 2);

      let value = b0 | (b1 << 8) | (b2 << 16);

      if (value & 0x800000) {
        value |= 0xff000000;
      }

      sample = value / 8388608;
    } else if (audioFormat === 1 && bitsPerSample === 32) {
      sample = view.getInt32(offset, true) / 2147483648;
    } else if (audioFormat === 3 && bitsPerSample === 32) {
      sample = view.getFloat32(offset, true);
    } else {
      throw new Error(
        `Nieobsługiwany format WAV: audioFormat=${audioFormat}, bitsPerSample=${bitsPerSample}`,
      );
    }

    samples.push(Math.max(-1, Math.min(1, sample)));
  }

  return downsample(samples);
}

async function decodeWithAudioContext(arrayBuffer) {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;

  if (!AudioContextClass) {
    throw new Error("AudioContext nie jest dostępny w tej przeglądarce");
  }

  const audioContext = new AudioContextClass();

  try {
    const audioBuffer = await audioContext.decodeAudioData(
      arrayBuffer.slice(0),
    );
    const rawData = audioBuffer.getChannelData(0);

    return downsample(rawData);
  } finally {
    if (typeof audioContext.close === "function") {
      audioContext.close();
    }
  }
}

export function useWaveform(file) {
  const [waveformData, setWaveformData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function extractWaveform() {
      if (!file) {
        setWaveformData(null);
        setError(null);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      setWaveformData(null);

      try {
        const originalBuffer = await file.arrayBuffer();
        const previewBuffer = stripAdhrChunk(originalBuffer);

        let samples;

        try {
          samples = await decodeWithAudioContext(previewBuffer);
        } catch {
          samples = parseWavManually(previewBuffer);
        }

        if (!cancelled) {
          setWaveformData(samples);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setWaveformData(null);
          setError(`Błąd podczas analizy pliku audio: ${err.message}`);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    extractWaveform();

    return () => {
      cancelled = true;
    };
  }, [file]);

  return { waveformData, isLoading, error };
}
