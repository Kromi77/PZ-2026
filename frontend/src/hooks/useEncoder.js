import { useState } from "react";
import { CIPHER_TYPES, getDefaultKeyForCipher } from "../config/ciphers";
import { DEPLOYMENT_MODES } from "../config/appConfig";
import {
  encryptText,
  hideSteganography,
  injectHeader,
} from "../api/steganographyApi";
import { validateCipherKey } from "../utils/validateCipherKey";
import { useMediaFile } from "./useMediaFile";
import { UI_TEXT } from "../i18n";
import { logger } from "../utils/logger";

export function useEncoder() {
  const [text, setText] = useState("");
  const [cipher, setCipher] = useState(CIPHER_TYPES.CEZAR);
  const [key, setKey] = useState(getDefaultKeyForCipher(CIPHER_TYPES.CEZAR));
  const [sliders, setSliders] = useState([1, 1, 1]);
  const [deploymentMode, setDeploymentMode] = useState(
    DEPLOYMENT_MODES.CONTINUOUS,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resultFile, setResultFile] = useState(null);

  const { file, mediaType, handleFileChange } = useMediaFile({
    onFileSelected: () => {
      setError("");
      setResultFile(null);
    },
  });

  function handleCipherChange(nextCipher) {
    logger.info("Cipher changed", { cipher: nextCipher });
    setCipher(nextCipher);
    setKey(getDefaultKeyForCipher(nextCipher));
    setError("");
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
  }

  async function handleEncode() {
    if (!text.trim()) {
      logger.warn("Encoding failed: missing text");
      setError(UI_TEXT.errors.missingText);
      return;
    }

    if (!file) {
      logger.warn("Encoding failed: missing file");
      setError(UI_TEXT.errors.missingFile);
      return;
    }

    const keyError = validateCipherKey(cipher, key);

    if (keyError) {
      logger.warn("Encoding failed: invalid key", { cipher, keyError });
      setError(keyError);
      return;
    }

    logger.info("Encoding started", {
      cipher,
      mediaType,
      deploymentMode,
      sliders,
    });
    setLoading(true);
    setError("");
    setResultFile(null);

    try {
      const encryptedText = await encryptText(cipher, text, key);
      const bits = new TextEncoder().encode(encryptedText).length * 8 + 32;
      logger.debug("Text encrypted", {
        textLength: text.length,
        encryptedLength: encryptedText.length,
        bits,
      });

      const stegoBlob = await hideSteganography(
        file,
        encryptedText,
        mediaType,
        deploymentMode,
        sliders,
      );

      const stegoFile = new File([stegoBlob], file.name, {
        type: file.type,
        lastModified: file.lastModified,
      });

      const finalBlob = await injectHeader(
        stegoFile,
        cipher,
        sliders,
        bits,
        deploymentMode,
        mediaType,
      );

      const finalFile = new File([finalBlob], `encoded_${file.name}`, {
        type: file.type,
      });

      logger.info("Encoding completed successfully", {
        outputFile: finalFile.name,
        size: finalFile.size,
      });
      setResultFile(finalFile);
    } catch (err) {
      logger.error("Encoding failed", { error: err.message });
      setError(err.message || UI_TEXT.errors.encodingFailed);
    } finally {
      setLoading(false);
    }
  }

  return {
    text,
    setText,
    cipher,
    handleCipherChange,
    key,
    setKey,
    file,
    mediaType,
    handleFileChange,
    sliders,
    handleSliderChange,
    deploymentMode,
    setDeploymentMode,
    loading,
    error,
    resultFile,
    handleEncode,
  };
}
