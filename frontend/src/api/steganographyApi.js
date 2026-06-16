import { API_BASE_URL, MEDIA_TYPES } from '../config/appConfig'
import { CIPHER_TYPES } from '../config/ciphers'

async function getApiError(response, fallbackMessage) {
  try {
    const error = await response.json()
    return error.detail || error.message || fallbackMessage
  } catch {
    return fallbackMessage
  }
}

async function ensureSuccessfulResponse(response, fallbackMessage) {
  if (!response.ok) {
    throw new Error(await getApiError(response, fallbackMessage))
  }
}

function getResponseOutput(data, fallbackMessage) {
  const output = data.output ?? data.result ?? data.text ?? data.message ?? data.decrypted_text

  if (typeof output !== 'string') {
    throw new Error(fallbackMessage)
  }

  return output
}

function normalizeMediaType(mediaType) {
  const value = String(mediaType || '').toLowerCase()

  if (value === String(MEDIA_TYPES.BMP).toLowerCase() || value === 'bmp' || value.includes('bmp')) {
    return 'bmp'
  }

  if (value === String(MEDIA_TYPES.WAV).toLowerCase() || value === 'wav' || value.includes('wav') || value.includes('audio')) {
    return 'wav'
  }

  return value
}

function normalizeDeploymentMode(deploymentMode) {
  const value = String(deploymentMode ?? '').toLowerCase()

  if (value === '1' || value.includes('uniform') || value.includes('równomier')) {
    return '1'
  }

  return '0'
}

const HEADER_CIPHER_VALUES = {
  [CIPHER_TYPES.CEZAR]: 'Szyfr Cezara',
  [CIPHER_TYPES.VIGENERE]: "Szyfr Vigenere'a",
  [CIPHER_TYPES.XOR]: 'Szyfr XOR',
  [CIPHER_TYPES.ATBASH]: 'Szyfr Atbash',
  [CIPHER_TYPES.ROT13]: 'ROT13',
  [CIPHER_TYPES.RAIL_FENCE]: 'Szyfr płotkowy',
  [CIPHER_TYPES.COLUMNAR]: 'Szyfr kolumnowy',
}

function getHeaderCipherValue(cipher) {
  return HEADER_CIPHER_VALUES[cipher] ?? cipher
}

function buildEncryptionPayload(cipher, text, key) {
  const body = { text }

  switch (cipher) {
    case CIPHER_TYPES.CEZAR:
      return {
        endpoint: '/caesar/encrypt',
        body: { ...body, shift: parseInt(key, 10) },
      }

    case CIPHER_TYPES.VIGENERE:
      return {
        endpoint: '/vinegre/encrypt',
        body: { ...body, key: String(key) },
      }

    case CIPHER_TYPES.XOR:
      return {
        endpoint: '/encrypt/xor',
        body: { ...body, key: String(key) },
      }

    case CIPHER_TYPES.ATBASH:
      return {
        endpoint: '/atbash/encrypt',
        body,
      }

    case CIPHER_TYPES.ROT13:
      return {
        endpoint: '/rot13/process',
        body,
      }

    case CIPHER_TYPES.RAIL_FENCE:
      return {
        endpoint: '/railfence/encrypt',
        body: { ...body, rails: parseInt(key, 10) },
      }

    case CIPHER_TYPES.COLUMNAR:
      return {
        endpoint: '/columnar/encrypt',
        body: { ...body, key: String(key) },
      }

    default:
      throw new Error(`Unsupported cipher: ${cipher}`)
  }
}

function buildDecryptionPayload(cipher, text, key) {
  const body = { text }

  switch (cipher) {
    case CIPHER_TYPES.CEZAR:
      return {
        endpoints: ['/caesar/decrypt'],
        body: { ...body, shift: parseInt(key, 10) },
      }

    case CIPHER_TYPES.VIGENERE:
      return {
        endpoints: ['/vinegre/decrypt'],
        body: { ...body, key: String(key) },
      }

    case CIPHER_TYPES.XOR:
      return {
        endpoints: ['/decrypt/xor', '/encrypt/xor'],
        body: { ...body, key: String(key) },
      }

    case CIPHER_TYPES.ATBASH:
      return {
        endpoints: ['/atbash/decrypt', '/atbash/encrypt'],
        body,
      }

    case CIPHER_TYPES.ROT13:
      return {
        endpoints: ['/rot13/process'],
        body,
      }

    case CIPHER_TYPES.RAIL_FENCE:
      return {
        endpoints: ['/railfence/decrypt'],
        body: { ...body, rails: parseInt(key, 10) },
      }

    case CIPHER_TYPES.COLUMNAR:
      return {
        endpoints: ['/columnar/decrypt'],
        body: { ...body, key: String(key) },
      }

    default:
      throw new Error(`Unsupported cipher: ${cipher}`)
  }
}

async function postJson(endpoint, body, fallbackMessage) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  await ensureSuccessfulResponse(response, fallbackMessage)
  return response.json()
}

async function postJsonWithFallback(endpoints, body, fallbackMessage) {
  let lastError = null

  for (const endpoint of endpoints) {
    try {
      return await postJson(endpoint, body, fallbackMessage)
    } catch (error) {
      lastError = error
    }
  }

  throw lastError || new Error(fallbackMessage)
}

export async function encryptText(cipher, text, key) {
  const { endpoint, body } = buildEncryptionPayload(cipher, text, key)
  const data = await postJson(endpoint, body, 'Encryption failed')

  return getResponseOutput(data, 'Encryption response does not contain output')
}

export async function decryptText(cipher, text, key) {
  const { endpoints, body } = buildDecryptionPayload(cipher, text, key)
  const data = await postJsonWithFallback(endpoints, body, 'Decryption failed')

  return getResponseOutput(data, 'Decryption response does not contain output')
}

export async function hideSteganography(file, encryptedMessage, mediaType, deploymentMode = 0) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('encrypted_message', encryptedMessage)
  formData.append('media_type', normalizeMediaType(mediaType))
  formData.append('deployment_mode', normalizeDeploymentMode(deploymentMode))

  const response = await fetch(`${API_BASE_URL}/steganography/hide`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Steganography hide failed')

  return response.blob()
}

export async function extractSteganography(file, mediaType, deploymentMode = 0) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('media_type', normalizeMediaType(mediaType))
  formData.append('deployment_mode', normalizeDeploymentMode(deploymentMode))

  const response = await fetch(`${API_BASE_URL}/steganography/extract`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Steganography extract failed')

  const data = await response.json()
  const message = data.message

  if (typeof message !== 'string') {
    throw new Error('Steganography extract response does not contain message')
  }

  return data
}

// Funkcja zostaje w API na przyszłość, ale obecny stabilny flow jej nie wywołuje.
// Wariant z nagłówkiem/hash wymaga poprawnego backendowego /header/inject-*.
export async function injectHeader(file, cipher, sliders, bits, deploymentMode, mediaType) {
  const normalizedMediaType = normalizeMediaType(mediaType)

  const formData = new FormData()
  formData.append('file', file)
  formData.append('cipher', getHeaderCipherValue(cipher))

  if (normalizedMediaType === 'bmp') {
    formData.append('sliderR', sliders[0] || 0)
    formData.append('sliderG', sliders[1] || 0)
    formData.append('sliderB', sliders[2] || 0)
  } else {
    formData.append('slider', sliders[0] || 0)
  }

  formData.append('bits', bits)
  formData.append('deployment_mode', normalizeDeploymentMode(deploymentMode))

  const endpoint = normalizedMediaType === 'bmp' ? '/header/inject-bmp/' : '/header/inject-wav/'

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Header injection failed')

  return response.blob()
}

// Stary automatyczny dekoder oparty o nagłówek/hash.
// Nie używaj dla plików generowanych bez injectHeader.
export async function decodeFile(file, mediaType, key = '') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('media_type', normalizeMediaType(mediaType))
  formData.append('key', key)

  const response = await fetch(`${API_BASE_URL}/decoder/process`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Decoding failed')

  return response.json()
}
