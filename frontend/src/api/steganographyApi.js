import { API_BASE_URL, MEDIA_TYPES } from '../config/appConfig'
import { CIPHER_TYPES } from '../config/ciphers'

async function getApiError(response, fallbackMessage) {
  try {
    const error = await response.json()
    return error.detail || fallbackMessage
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
        endpoint: '/caesar/decrypt',
        body: { ...body, shift: parseInt(key, 10) },
      }

    case CIPHER_TYPES.VIGENERE:
      return {
        endpoint: '/vinegre/decrypt',
        body: { ...body, key: String(key) },
      }

    case CIPHER_TYPES.XOR:
      // XOR jest symetryczny, więc ten sam endpoint może działać jako szyfrowanie i deszyfrowanie.
      return {
        endpoint: '/encrypt/xor',
        body: { ...body, key: String(key) },
      }

    case CIPHER_TYPES.ATBASH:
      // Atbash jest symetryczny.
      return {
        endpoint: '/atbash/encrypt',
        body,
      }

    case CIPHER_TYPES.ROT13:
      // ROT13 jest symetryczny.
      return {
        endpoint: '/rot13/process',
        body,
      }

    case CIPHER_TYPES.RAIL_FENCE:
      return {
        endpoint: '/railfence/decrypt',
        body: { ...body, rails: parseInt(key, 10) },
      }

    case CIPHER_TYPES.COLUMNAR:
      return {
        endpoint: '/columnar/decrypt',
        body: { ...body, key: String(key) },
      }

    default:
      throw new Error(`Unsupported cipher: ${cipher}`)
  }
}

export async function encryptText(cipher, text, key) {
  const { endpoint, body } = buildEncryptionPayload(cipher, text, key)

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  await ensureSuccessfulResponse(response, 'Encryption failed')

  const data = await response.json()
  return getResponseOutput(data, 'Encryption response does not contain output')
}

export async function decryptText(cipher, text, key) {
  const { endpoint, body } = buildDecryptionPayload(cipher, text, key)

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  await ensureSuccessfulResponse(response, 'Decryption failed')

  const data = await response.json()
  return getResponseOutput(data, 'Decryption response does not contain output')
}

export async function hideSteganography(file, encryptedMessage, mediaType) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('encrypted_message', encryptedMessage)
  formData.append('media_type', mediaType)

  const response = await fetch(`${API_BASE_URL}/steganography/hide`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Steganography hide failed')

  return response.blob()
}

export async function extractSteganography(file, mediaType) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('media_type', mediaType)

  const response = await fetch(`${API_BASE_URL}/steganography/extract`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Steganography extract failed')

  return response.json()
}

// Zostawione tylko dla starego wariantu z nagłówkiem. Obecny przepływ go nie używa,
// ponieważ /header/inject-bmp/ i /header/inject-wav/ psuły plik binarny.
export async function injectHeader(file, cipher, sliders, bits, deploymentMode, mediaType) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('cipher', cipher)

  if (mediaType === MEDIA_TYPES.BMP) {
    formData.append('sliderR', sliders[0] || 0)
    formData.append('sliderG', sliders[1] || 0)
    formData.append('sliderB', sliders[2] || 0)
  } else {
    formData.append('slider', sliders[0] || 0)
  }

  formData.append('bits', bits)
  formData.append('deployment_mode', deploymentMode)

  const endpoint = mediaType === MEDIA_TYPES.BMP ? '/header/inject-bmp/' : '/header/inject-wav/'

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Header injection failed')

  return response.blob()
}

// Stary automatyczny dekoder oparty o nagłówek/hash. Nie używaj dla plików
// generowanych bez injectHeader, bo zwróci hash verification failed.
export async function decodeFile(file, mediaType, key = '') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('media_type', mediaType)
  formData.append('key', key)

  const response = await fetch(`${API_BASE_URL}/decoder/process`, {
    method: 'POST',
    body: formData,
  })

  await ensureSuccessfulResponse(response, 'Decoding failed')

  return response.json()
}
