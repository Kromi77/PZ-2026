import { useState } from 'react'
import { DEPLOYMENT_MODES } from '../config/appConfig'
import { CIPHER_OPTIONS, CIPHER_TYPES, getDefaultKeyForCipher } from '../config/ciphers'
import {
  decodeFile,
  decryptText,
  extractHeader,
  extractSteganography,
  normalizeDeploymentMode,
  normalizeMediaType,
  normalizeSliders,
} from '../api/steganographyApi'
import { validateCipherKey } from '../utils/validateCipherKey'
import { useMediaFile } from './useMediaFile'
import { UI_TEXT } from '../i18n'

function getCipherLabel(cipher) {
  return CIPHER_OPTIONS.find((option) => option.id === cipher)?.label ?? cipher
}

function getDeploymentModeLabel(deploymentMode) {
  return Number(normalizeDeploymentMode(deploymentMode)) === DEPLOYMENT_MODES.UNIFORM
    ? 'Równomierne'
    : 'Ciągłe'
}

function readHeaderDeploymentMode(header) {
  return Number(normalizeDeploymentMode(header?.deployment_mode))
}

function readHeaderBits(header) {
  const bits = Number(header?.bits)
  return Number.isFinite(bits) && bits > 0 ? bits : null
}

function readHeaderSliders(header, mediaType) {
  const normalizedMediaType = normalizeMediaType(mediaType)

  if (!header) {
    return null
  }

  if (normalizedMediaType === 'bmp' && Array.isArray(header.sliders)) {
    return normalizeSliders(normalizedMediaType, header.sliders)
  }

  if (normalizedMediaType === 'wav' && header.slider !== undefined && header.slider !== null) {
    return normalizeSliders(normalizedMediaType, [header.slider])
  }

  return null
}

function createCandidateKey(candidate) {
  return JSON.stringify({
    deploymentMode: Number(normalizeDeploymentMode(candidate.deploymentMode)),
    sliders: candidate.sliders,
    totalBits: candidate.totalBits ?? null,
  })
}

function createFallbackCandidates({ mediaType, selectedDeploymentMode, selectedSliders, header }) {
  const normalizedMediaType = normalizeMediaType(mediaType)
  const manualSliders = normalizeSliders(normalizedMediaType, selectedSliders)
  const defaultSliders = normalizeSliders(normalizedMediaType, [1, 1, 1])
  const headerSliders = readHeaderSliders(header, normalizedMediaType)
  const headerDeploymentMode = readHeaderDeploymentMode(header)
  const totalBits = readHeaderBits(header)

  const rawCandidates = [
    {
      label: 'ręczne suwaki + tryb z UI',
      deploymentMode: selectedDeploymentMode,
      sliders: manualSliders,
      totalBits,
    },
    {
      label: 'ręczne suwaki + tryb z nagłówka',
      deploymentMode: headerDeploymentMode,
      sliders: manualSliders,
      totalBits,
    },
    headerSliders && {
      label: 'suwaki i tryb z nagłówka',
      deploymentMode: headerDeploymentMode,
      sliders: headerSliders,
      totalBits,
    },
    {
      label: 'domyślne suwaki 1 + tryb z nagłówka',
      deploymentMode: headerDeploymentMode,
      sliders: defaultSliders,
      totalBits,
    },
    {
      label: 'domyślne suwaki 1 + tryb z UI',
      deploymentMode: selectedDeploymentMode,
      sliders: defaultSliders,
      totalBits,
    },
  ].filter(Boolean)

  const seen = new Set()

  return rawCandidates.filter((candidate) => {
    const key = createCandidateKey(candidate)

    if (seen.has(key)) {
      return false
    }

    seen.add(key)
    return true
  })
}

export function useDecoder() {
  const [cipher, setCipher] = useState(CIPHER_TYPES.CEZAR)
  const [key, setKey] = useState(getDefaultKeyForCipher(CIPHER_TYPES.CEZAR))
  const [sliders, setSliders] = useState([1, 1, 1])
  const [deploymentMode, setDeploymentMode] = useState(DEPLOYMENT_MODES.CONTINUOUS)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const { file, mediaType, handleFileChange } = useMediaFile({
    onFileSelected: () => {
      setError('')
      setResult(null)
    },
  })

  function handleCipherChange(nextCipher) {
    setCipher(nextCipher)
    setKey(getDefaultKeyForCipher(nextCipher))
    setError('')
    setResult(null)
  }

  function handleSliderChange(index, value) {
    const parsedValue = parseInt(value, 10)

    setSliders((currentSliders) => {
      const nextSliders = [...currentSliders]
      nextSliders[index] = Number.isNaN(parsedValue) ? 1 : Math.min(8, Math.max(0, parsedValue))
      return nextSliders
    })

    setError('')
    setResult(null)
  }

  function handleDeploymentModeChange(nextDeploymentMode) {
    setDeploymentMode(nextDeploymentMode)
    setError('')
    setResult(null)
  }

  async function handleDecode() {
    if (!file) {
      setError(UI_TEXT.errors.missingFile)
      return
    }

    const keyError = validateCipherKey(cipher, key)

    if (keyError) {
      setError(keyError)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      console.groupCollapsed('[DECODE flow] dane wejściowe')
      console.log({
        file: {
          name: file.name,
          type: file.type,
          size: file.size,
        },
        mediaType,
        cipher,
        key,
        sliders,
        deploymentMode,
      })
      console.groupEnd()

      try {
        const decodedResult = await decodeFile(file, mediaType, key)

        console.groupCollapsed('[DECODE flow] wynik /decoder/process')
        console.log(decodedResult)
        console.groupEnd()

        setResult(decodedResult)
        return
      } catch (decoderError) {
        console.warn('[DECODE flow] /decoder/process nie odczytał wiadomości, przechodzę na fallback z nagłówka + LSB', decoderError)
      }

      const header = await extractHeader(file, mediaType)
      const candidates = createFallbackCandidates({
        mediaType,
        selectedDeploymentMode: deploymentMode,
        selectedSliders: sliders,
        header,
      })

      let lastError = null

      for (const candidate of candidates) {
        try {
          console.groupCollapsed(`[DECODE fallback] próba: ${candidate.label}`)
          console.log(candidate)
          console.groupEnd()

          const extractedResult = await extractSteganography(
            file,
            mediaType,
            candidate.deploymentMode,
            candidate.sliders,
            candidate.totalBits,
          )

          const encryptedMessage = extractedResult.message

          if (!encryptedMessage) {
            throw new Error('Nie znaleziono ukrytej wiadomości w pliku')
          }

          const decryptedText = await decryptText(cipher, encryptedMessage, key)

          const fallbackResult = {
            status: 'success',
            message_detected: true,
            cipher_used: getCipherLabel(cipher),
            deployment_mode: getDeploymentModeLabel(candidate.deploymentMode),
            bits_extracted: candidate.totalBits ?? new TextEncoder().encode(encryptedMessage).length * 8 + 32,
            decrypted_text: decryptedText,
            encrypted_text: encryptedMessage,
          }

          console.groupCollapsed('[DECODE fallback] wynik końcowy')
          console.log(fallbackResult)
          console.groupEnd()

          setResult(fallbackResult)
          return
        } catch (candidateError) {
          lastError = candidateError
          console.warn(`[DECODE fallback] nieudana próba: ${candidate.label}`, candidateError)
        }
      }

      throw lastError || new Error('Nie udało się odkodować pliku żadną dostępną metodą')
    } catch (err) {
      setError(err.message || UI_TEXT.errors.decodingFailed)
    } finally {
      setLoading(false)
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
    loading,
    error,
    result,
    handleDecode,
  }
}
