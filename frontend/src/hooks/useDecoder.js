import { useState } from 'react'
import { CIPHER_TYPES, getDefaultKeyForCipher } from '../config/ciphers'
import { decryptText, extractSteganography } from '../api/steganographyApi'
import { validateCipherKey } from '../utils/validateCipherKey'
import { useMediaFile } from './useMediaFile'
import { UI_TEXT } from '../i18n'

export function useDecoder() {
  const [cipher, setCipher] = useState(CIPHER_TYPES.CEZAR)
  const [key, setKey] = useState(getDefaultKeyForCipher(CIPHER_TYPES.CEZAR))
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
      const extractedResult = await extractSteganography(file, mediaType)
      const encryptedMessage = extractedResult.message

      if (!encryptedMessage) {
        throw new Error('Nie znaleziono ukrytej wiadomości w pliku')
      }

      const decryptedText = await decryptText(cipher, encryptedMessage, key)
      const encryptedMessageBits = new Blob([encryptedMessage]).size * 8 + 32

      setResult({
        message_detected: true,
        cipher_used: cipher,
        deployment_mode: 'continuous',
        bits_extracted: encryptedMessageBits,
        encrypted_text: encryptedMessage,
        decrypted_text: decryptedText,
      })
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
    loading,
    error,
    result,
    handleDecode,
  }
}
