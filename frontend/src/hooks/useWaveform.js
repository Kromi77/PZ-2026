import { useState, useEffect, useRef } from "react";

/**
 * Hook do ekstrakcji i analizy danych audio z pliku WAV
 * Zwraca amplitudy próbek audio do rysowania oscylogramu
 */
export function useWaveform(file) {
  const [waveformData, setWaveformData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (!file) {
      setWaveformData(null);
      setError(null);
      return;
    }

    if (!file.type.includes("audio")) {
      setError("To nie jest plik audio");
      return;
    }

    // Anuluj poprzednią operację jeśli istnieje
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    const extractWaveform = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const arrayBuffer = await file.arrayBuffer();

        // Stwórz AudioContext
        const audioContext = new (
          window.AudioContext || window.webkitAudioContext
        )();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        // Pobierz dane z pierwszego kanału
        const rawData = audioBuffer.getChannelData(0);

        // Zmniejsz ilość próbek do 2000 dla wydajności
        const samplesPerPixel = Math.max(1, Math.floor(rawData.length / 2000));
        const waveformSamples = [];

        for (let i = 0; i < rawData.length; i += samplesPerPixel) {
          waveformSamples.push(rawData[i]);
        }

        setWaveformData(waveformSamples);
        setIsLoading(false);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError("Błąd podczas analizy pliku audio: " + err.message);
          setIsLoading(false);
        }
      }
    };

    extractWaveform();

    // Cleanup
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [file]);

  return { waveformData, isLoading, error };
}
