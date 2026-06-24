import { useState } from "react";
import { DEPLOYMENT_MODES } from "../config/appConfig";
import { CIPHER_TYPES, getDefaultKeyForCipher } from "../config/ciphers";
import {
  buildRestoredFile,
  decryptText,
  extractHeader,
  extractSteganography,
  normalizeDeploymentMode,
  normalizeMediaType,
  normalizeSliders,
  restoreCarrierFile,
} from "../api/steganographyApi";
import { validateCipherKey } from "../utils/validateCipherKey";
import { useMediaFile } from "./useMediaFile";
import { UI_TEXT } from "../i18n";
import { logger } from "../utils/logger";

function readHeaderSliders(header, mediaType, fallbackSliders = [1, 1, 1]) {
  const normalizedMediaType = normalizeMediaType(mediaType);

  if (!header) {
    return normalizeSliders(normalizedMediaType, fallbackSliders);
  }

  if (normalizedMediaType === "bmp" && Array.isArray(header.sliders)) {
    return normalizeSliders(normalizedMediaType, header.sliders);
  }

  if (
    normalizedMediaType === "wav" &&
    header.slider !== undefined &&
    header.slider !== null
  ) {
    return normalizeSliders(normalizedMediaType, [header.slider]);
  }

  return normalizeSliders(normalizedMediaType, fallbackSliders);
}

function getDeploymentModeLabel(deploymentMode) {
  return Number(normalizeDeploymentMode(deploymentMode)) ===
    DEPLOYMENT_MODES.UNIFORM
    ? "Równomierne"
    : "Ciągłe";
}

export function useDecoder() {
  const [cipher, setCipher] = useState(CIPHER_TYPES.CEZAR);
  const [key, setKey] = useState(getDefaultKeyForCipher(CIPHER_TYPES.CEZAR));
  const [sliders, setSliders] = useState([1, 1, 1]);
  const [deploymentMode, setDeploymentMode] = useState(
    DEPLOYMENT_MODES.CONTINUOUS,
  );
  const [detectedHeader, setDetectedHeader] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const { file, mediaType, handleFileChange } = useMediaFile({
    onFileSelected: () => {
      setError("");
      setResult(null);
      setDetectedHeader(null);
    },
  });

  function handleCipherChange(nextCipher) {
    logger.info("Cipher changed", { cipher: nextCipher });
    setCipher(nextCipher);
    setKey(getDefaultKeyForCipher(nextCipher));
    setError("");
    setResult(null);
  }

  function handleSliderChange(index, value) {
    const parsedValue = parseInt(value, 10);
    logger.debug(`Slider ${index} changed`, { value: parsedValue });

    setSliders((currentSliders) => {
      const nextSliders = [...currentSliders];
      nextSliders[index] = Number.isNaN(parsedValue)
        ? 1
        : Math.min(8, Math.max(0, parsedValue));
      return nextSliders;
    });

    setError("");
    setResult(null);
  }

  function handleDeploymentModeChange(nextDeploymentMode) {
    logger.debug("Deployment mode changed", { mode: nextDeploymentMode });
    setDeploymentMode(nextDeploymentMode);
    setError("");
    setResult(null);
  }

  async function handleDecode() {
    if (!file) {
      logger.warn("Decoding failed: missing file");
      setError(UI_TEXT.errors.missingFile);
      return;
    }

    logger.info("Decoding started", { mediaType });
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Finalny flow deterministyczny:
      // 1. Odczytaj nagłówek.
      // 2. Zweryfikuj klucz na podstawie szyfru z nagłówka.
      // 3. Usuń dodatkowy nagłówek z nośnika.
      // 4. Wyciągnij wiadomość LSB.
      // 5. Odszyfruj wiadomość.
      const header = await extractHeader(file, mediaType);
      logger.debug("Header extracted", { header });

      const effectiveCipher = header.cipher;
      const effectiveDeploymentMode = Number(
        normalizeDeploymentMode(header.deployment_mode),
      );
      const effectiveSliders = readHeaderSliders(header, mediaType, sliders);
      const totalBits = Number(header.bits);

      setDetectedHeader(header);
      setCipher(effectiveCipher);
      setDeploymentMode(effectiveDeploymentMode);
      setSliders((currentSliders) => {
        const normalizedMediaType = normalizeMediaType(mediaType);
        return normalizedMediaType === "bmp"
          ? effectiveSliders
          : [
              effectiveSliders[0],
              currentSliders[1] ?? 1,
              currentSliders[2] ?? 1,
            ];
      });

      const keyError = validateCipherKey(effectiveCipher, key);

      if (keyError) {
        logger.error("Decoding failed: key validation error", {
          cipher: effectiveCipher,
        });
        throw new Error(
          `${effectiveCipher} wymaga podania poprawnego klucza deszyfrowania.`,
        );
      }

      logger.debug("Restoring carrier file...", { mediaType, bits: totalBits });
      const restoredBlob = await restoreCarrierFile(file, mediaType);
      const restoredFile = buildRestoredFile(file, restoredBlob, mediaType);

      const extractedResult = await extractSteganography(
        restoredFile,
        mediaType,
        effectiveDeploymentMode,
        effectiveSliders,
        totalBits,
      );

      const encryptedMessage = extractedResult.message;

      if (!encryptedMessage) {
        logger.error("Decoding failed: no hidden message found");
        throw new Error("Nie znaleziono ukrytej wiadomości w pliku");
      }

      logger.debug("Message extracted, decrypting...", {
        messageLength: encryptedMessage.length,
      });
      const decryptedText = await decryptText(
        effectiveCipher,
        encryptedMessage,
        key,
      );

      logger.info("Decoding completed successfully", {
        cipher: effectiveCipher,
        messageLength: decryptedText.length,
      });
      setResult({
        status: "success",
        message_detected: true,
        cipher_used: effectiveCipher,
        deployment_mode: getDeploymentModeLabel(effectiveDeploymentMode),
        bits_extracted: totalBits,
        decrypted_text: decryptedText,
        encrypted_text: encryptedMessage,
        header,
        restoredFile,
      });
    } catch (err) {
      logger.error("Decoding failed", { error: err.message });
      setError(err.message || UI_TEXT.errors.decodingFailed);
    } finally {
      setLoading(false);
    }
  }

  return {
    file,
    mediaType,
    handleFileChange,
    cipher,
    handleCipherChange,
    key,
    setKey,
    sliders,
    handleSliderChange,
    deploymentMode,
    setDeploymentMode,
    handleDeploymentModeChange,
    detectedHeader,
    loading,
    error,
    result,
    handleDecode,
  };
}
