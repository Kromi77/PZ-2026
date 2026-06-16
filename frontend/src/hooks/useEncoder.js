import { useState } from 'react'
import { CIPHER_TYPES, getDefaultKeyForCipher } from '../config/ciphers'
import { encryptText, hideSteganography } from '../api/steganographyApi'
import { validateCipherKey } from '../utils/validateCipherKey'
import { useMediaFile } from './useMediaFile'
import { UI_TEXT } from '../i18n'

export function useEncoder() {
  const [text, setText] = useState('')
  const [cipher, setCipher] = useState(CIPHER_TYPES.CEZAR)
  const [key, setKey] = useState(getDefaultKeyForCipher(CIPHER_TYPES.CEZAR))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resultFile, setResultFile] = useState(null)

  const { file, mediaType, handleFileChange } = useMediaFile({
    onFileSelected: () => {
      setError('')
      setResultFile(null)
    },
  })

  function handleCipherChange(nextCipher) {
    setCipher(nextCipher)
    setKey(getDefaultKeyForCipher(nextCipher))
    setError('')
  }

  async function handleEncode() {
    if (!text.trim()) {
      setError(UI_TEXT.errors.missingText)
      return
    }

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
    setResultFile(null)

    try {
      const encryptedText = await encryptText(cipher, text, key)
      const modifiedMediaBlob = await hideSteganography(file, encryptedText, mediaType)

      const finalFile = new File([modifiedMediaBlob], `encoded_${file.name}`, {
        type: file.type,
      })

      setResultFile(finalFile)
    } catch (err) {
      setError(err.message || UI_TEXT.errors.encodingFailed)
    } finally {
      setLoading(false)
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
    loading,
    error,
    resultFile,
    handleEncode,
  }
}
