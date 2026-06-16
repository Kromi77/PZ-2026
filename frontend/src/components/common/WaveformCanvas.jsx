import { useEffect, useRef } from "react";

/**
 * Komponent do rysowania oscylogramu (waveform) pliku audio
 * Pokazuje amplitudę próbek audio w osi czasu
 */
export default function WaveformCanvas({
  waveformData,
  height = 150,
  color = "#3b82f6",
  backgroundColor = "#f3f4f6",
  isLoading = false,
  onClick = null,
  clickable = false,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !waveformData || waveformData.length === 0) {
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.offsetWidth;
    const dpr = window.devicePixelRatio || 1;

    // Ustaw rozmiar canvas z uwzględnieniem DPR dla ostre krawędziach
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    // Wyczyść canvas
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, width, height);

    // Rysuj waveform
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    const samplesPerPixel = Math.max(
      1,
      Math.floor(waveformData.length / width),
    );
    const centerY = height / 2;
    const scale = (height / 2) * 0.9; // 90% skali dla marginesu

    ctx.beginPath();
    ctx.moveTo(0, centerY);

    // Rysuj linie dla każdego piksela
    for (let x = 0; x < width; x++) {
      let max = 0;

      // Znajdź maksymalną amplitudę dla tego piksela
      for (let i = 0; i < samplesPerPixel; i++) {
        const sampleIndex = x * samplesPerPixel + i;
        if (sampleIndex < waveformData.length) {
          const sample = Math.abs(waveformData[sampleIndex]);
          if (sample > max) max = sample;
        }
      }

      const y = centerY - max * scale;
      ctx.lineTo(x, y);
    }

    ctx.stroke();

    // Rysuj linię środkową
    ctx.strokeStyle = "rgba(0, 0, 0, 0.1)";
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();
  }, [waveformData, height, color, backgroundColor]);

  return (
    <div className="w-full">
      {isLoading && (
        <div
          className="flex items-center justify-center"
          style={{ height: `${height}px` }}
        >
          <span className="text-gray-500">Ładowanie oscylogramu...</span>
        </div>
      )}
      {!isLoading && waveformData && (
        <canvas
          ref={canvasRef}
          onClick={onClick}
          className={`w-full border rounded shadow ${
            clickable
              ? "cursor-pointer hover:border-white/50 transition hover:shadow-lg"
              : ""
          }`}
          style={{ height: `${height}px`, display: "block" }}
        />
      )}
    </div>
  );
}
