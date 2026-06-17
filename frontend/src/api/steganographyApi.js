import { API_BASE_URL, MEDIA_TYPES } from "../config/appConfig";
import { CIPHER_TYPES } from "../config/ciphers";

function describeFile(file) {
  if (!file) return null;

  return {
    name: file.name,
    type: file.type,
    size: file.size,
    lastModified: file.lastModified,
  };
}

async function getApiError(response, fallbackMessage) {
  try {
    const error = await response.json();
    return error.detail || error.message || fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}

async function ensureSuccessfulResponse(response, fallbackMessage) {
  if (!response.ok) {
    throw new Error(await getApiError(response, fallbackMessage));
  }
}

function getResponseOutput(data, fallbackMessage) {
  const output =
    data.output ??
    data.result ??
    data.text ??
    data.message ??
    data.decrypted_text;

  if (typeof output !== "string") {
    throw new Error(fallbackMessage);
  }

  return output;
}

export function normalizeMediaType(mediaType) {
  const value = String(mediaType || "").toLowerCase();

  if (
    value === String(MEDIA_TYPES.BMP).toLowerCase() ||
    value === "bmp" ||
    value.includes("bmp") ||
    value.includes("image")
  ) {
    return "bmp";
  }

  if (
    value === String(MEDIA_TYPES.WAV).toLowerCase() ||
    value === "wav" ||
    value.includes("wav") ||
    value.includes("audio")
  ) {
    return "wav";
  }

  return value;
}

export function normalizeDeploymentMode(deploymentMode) {
  const value = String(deploymentMode ?? "").toLowerCase();

  if (
    value === "1" ||
    value.includes("uniform") ||
    value.includes("równomier")
  ) {
    return "1";
  }

  return "0";
}

export function normalizeSliderValue(value, fallback = 1) {
  const parsedValue = parseInt(value, 10);

  if (Number.isNaN(parsedValue)) {
    return fallback;
  }

  return Math.min(8, Math.max(0, parsedValue));
}

export function normalizeSliders(mediaType, sliders = [1, 1, 1]) {
  const normalizedMediaType = normalizeMediaType(mediaType);

  if (normalizedMediaType === "bmp") {
    return [
      normalizeSliderValue(sliders[0]),
      normalizeSliderValue(sliders[1]),
      normalizeSliderValue(sliders[2]),
    ];
  }

  return [normalizeSliderValue(sliders[0])];
}

function getSliderPayload(mediaType, sliders = [1, 1, 1]) {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const normalizedSliders = normalizeSliders(normalizedMediaType, sliders);

  if (normalizedMediaType === "bmp") {
    return {
      sliderR: normalizedSliders[0],
      sliderG: normalizedSliders[1],
      sliderB: normalizedSliders[2],
    };
  }

  return {
    slider: normalizedSliders[0],
  };
}

function appendSlidersToFormData(formData, mediaType, sliders = [1, 1, 1]) {
  const sliderPayload = getSliderPayload(mediaType, sliders);

  Object.entries(sliderPayload).forEach(([key, value]) => {
    formData.append(key, String(value));
  });
}

export function getBackendCipherValue(cipher) {
  return String(cipher || "");
}

function buildEncryptionPayload(cipher, text, key) {
  const body = { text };

  switch (cipher) {
    case CIPHER_TYPES.CEZAR:
      return {
        endpoint: "/caesar/encrypt",
        body: { ...body, shift: parseInt(key, 10) },
      };

    case CIPHER_TYPES.VIGENERE:
      return {
        endpoint: "/vinegre/encrypt",
        body: { ...body, key: String(key) },
      };

    case CIPHER_TYPES.XOR:
      return {
        endpoint: "/encrypt/xor",
        body: { ...body, key: String(key) },
      };

    case CIPHER_TYPES.ATBASH:
      return {
        endpoint: "/atbash/encrypt",
        body,
      };

    case CIPHER_TYPES.ROT13:
      return {
        endpoint: "/rot13/process",
        body,
      };

    case CIPHER_TYPES.RAIL_FENCE:
      return {
        endpoint: "/railfence/encrypt",
        body: { ...body, rails: parseInt(key, 10) },
      };

    case CIPHER_TYPES.COLUMNAR:
      return {
        endpoint: "/columnar/encrypt",
        body: { ...body, key: String(key) },
      };

    default:
      throw new Error(`Unsupported cipher: ${cipher}`);
  }
}

function buildDecryptionPayload(cipher, text, key) {
  const body = { text };

  switch (cipher) {
    case CIPHER_TYPES.CEZAR:
      return {
        endpoint: "/caesar/decrypt",
        body: { ...body, shift: parseInt(key, 10) },
      };

    case CIPHER_TYPES.VIGENERE:
      return {
        endpoint: "/vinegre/decrypt",
        body: { ...body, key: String(key) },
      };

    case CIPHER_TYPES.XOR:
      return {
        endpoint: "/decrypt/xor",
        body: { ...body, key: String(key) },
      };

    case CIPHER_TYPES.ATBASH:
      return {
        endpoint: "/atbash/decrypt",
        body,
      };

    case CIPHER_TYPES.ROT13:
      return {
        endpoint: "/rot13/process",
        body,
      };

    case CIPHER_TYPES.RAIL_FENCE:
      return {
        endpoint: "/railfence/decrypt",
        body: { ...body, rails: parseInt(key, 10) },
      };

    case CIPHER_TYPES.COLUMNAR:
      return {
        endpoint: "/columnar/decrypt",
        body: { ...body, key: String(key) },
      };

    default:
      throw new Error(`Unsupported cipher: ${cipher}`);
  }
}

async function postJson(endpoint, body, fallbackMessage) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  await ensureSuccessfulResponse(response, fallbackMessage);
  const data = await response.json();

  return data;
}

export async function encryptText(cipher, text, key) {
  const { endpoint, body } = buildEncryptionPayload(cipher, text, key);
  const data = await postJson(endpoint, body, "Encryption failed");

  return getResponseOutput(data, "Encryption response does not contain output");
}

export async function decryptText(cipher, text, key) {
  const { endpoint, body } = buildDecryptionPayload(cipher, text, key);
  const data = await postJson(endpoint, body, "Decryption failed");

  return getResponseOutput(data, "Decryption response does not contain output");
}

export async function hideSteganography(
  file,
  encryptedMessage,
  mediaType,
  deploymentMode = 0,
  sliders = [1, 1, 1],
) {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const normalizedDeploymentMode = normalizeDeploymentMode(deploymentMode);
  const sliderPayload = getSliderPayload(normalizedMediaType, sliders);
  const endpoint = "/steganography/hide";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("encrypted_message", encryptedMessage);
  formData.append("media_type", normalizedMediaType);
  formData.append("deployment_mode", normalizedDeploymentMode);
  appendSlidersToFormData(formData, normalizedMediaType, sliders);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  await ensureSuccessfulResponse(response, "Steganography hide failed");
  const blob = await response.blob();

  return blob;
}

export async function injectHeader(
  file,
  cipher,
  sliders,
  bits,
  deploymentMode,
  mediaType,
) {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const normalizedDeploymentMode = normalizeDeploymentMode(deploymentMode);
  const backendCipher = getBackendCipherValue(cipher);
  const sliderPayload = getSliderPayload(normalizedMediaType, sliders);
  const endpoint =
    normalizedMediaType === "bmp"
      ? "/header/inject-bmp/"
      : "/header/inject-wav/";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("cipher", backendCipher);
  formData.append("bits", String(bits));
  formData.append("deployment_mode", normalizedDeploymentMode);
  appendSlidersToFormData(formData, normalizedMediaType, sliders);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  await ensureSuccessfulResponse(response, "Header injection failed");
  const blob = await response.blob();

  return blob;
}

export async function extractHeader(file, mediaType) {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const endpoint =
    normalizedMediaType === "bmp"
      ? "/header/extract-bmp-header/"
      : "/header/extract-wav-header/";

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  await ensureSuccessfulResponse(response, "Header extraction failed");
  const data = await response.json();

  return data;
}

export async function restoreCarrierFile(file, mediaType) {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const endpoint =
    normalizedMediaType === "bmp"
      ? "/header/extract-bmp/"
      : "/header/extract-wav/";

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  await ensureSuccessfulResponse(response, "Header restore failed");
  const blob = await response.blob();

  return blob;
}

export async function extractSteganography(
  file,
  mediaType,
  deploymentMode = 0,
  sliders = [1, 1, 1],
  totalBits = null,
) {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const normalizedDeploymentMode = normalizeDeploymentMode(deploymentMode);
  const sliderPayload = getSliderPayload(normalizedMediaType, sliders);
  const endpoint = "/steganography/extract";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("media_type", normalizedMediaType);
  formData.append("deployment_mode", normalizedDeploymentMode);
  appendSlidersToFormData(formData, normalizedMediaType, sliders);

  if (totalBits !== null && totalBits !== undefined && totalBits !== "") {
    formData.append("total_bits", String(totalBits));
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  await ensureSuccessfulResponse(response, "Steganography extract failed");
  const data = await response.json();

  const message = data.message;

  if (typeof message !== "string") {
    throw new Error("Steganography extract response does not contain message");
  }

  return data;
}

export function buildRestoredFile(originalFile, restoredBlob, mediaType) {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const defaultType = normalizedMediaType === "wav" ? "audio/wav" : "image/bmp";

  return new File([restoredBlob], originalFile.name, {
    type: originalFile.type || defaultType,
    lastModified: originalFile.lastModified,
  });
}

export async function decodeEncodedFile(file, mediaType, key = "") {
  const normalizedMediaType = normalizeMediaType(mediaType);
  const header = await extractHeader(file, normalizedMediaType);
  const deploymentMode = Number(
    normalizeDeploymentMode(header.deployment_mode),
  );
  const sliders =
    normalizedMediaType === "bmp"
      ? normalizeSliders(normalizedMediaType, header.sliders)
      : normalizeSliders(normalizedMediaType, [header.slider]);
  const totalBits = Number(header.bits);

  const restoredBlob = await restoreCarrierFile(file, normalizedMediaType);
  const restoredFile = buildRestoredFile(
    file,
    restoredBlob,
    normalizedMediaType,
  );
  const extracted = await extractSteganography(
    restoredFile,
    normalizedMediaType,
    deploymentMode,
    sliders,
    totalBits,
  );
  const encryptedText = extracted.message;
  const decryptedText = await decryptText(header.cipher, encryptedText, key);

  return {
    status: "success",
    message_detected: true,
    cipher_used: header.cipher,
    deployment_mode: deploymentMode === 1 ? "Równomierne" : "Ciągłe",
    bits_extracted: totalBits,
    decrypted_text: decryptedText,
    encrypted_text: encryptedText,
    header,
    restoredFile,
  };
}

// Alias dla starych importów: korzysta z deterministycznego flow po nagłówku.
export async function decodeFile(file, mediaType, key = "") {
  return decodeEncodedFile(file, mediaType, key);
}
