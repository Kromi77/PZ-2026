import { useState } from 'react'
import { CIPHER_TYPES, getDefaultKeyForCipher } from '../config/ciphers'
import { DEPLOYMENT_MODES } from '../config/appConfig'
import { encryptText, hideSteganography, injectHeader } from '../api/steganographyApi'
import { validateCipherKey } from '../utils/validateCipherKey'
import { useMediaFile } from './useMediaFile'
import { UI_TEXT } from '../i18n'

export function useEncoder() {
  const [text, setText] = useState('')
  const [cipher, setCipher] = useState(CIPHER_TYPES.CEZAR)
  const [key, setKey] = useState(getDefaultKeyForCipher(CIPHER_TYPES.CEZAR))
  const [sliders, setSliders] = useState([0, 0, 0])
  const [deploymentMode, setDeploymentMode] = useState(DEPLOYMENT_MODES.CONTINUOUS)
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

  function handleSliderChange(index, value) {
    const parsedValue = parseInt(value, 10)

    setSliders((currentSliders) => {
      const nextSliders = [...currentSliders]
      nextSliders[index] = Number.isNaN(parsedValue) ? 0 : parsedValue
      return nextSliders
    })
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
      const bits = new Blob([encryptedText]).size * 8 + 32

      const modifiedMediaBlob = await hideSteganography(file, encryptedText, mediaType)
      const modifiedMediaFile = new File([modifiedMediaBlob], file.name, {
        type: file.type,
      })

      const finalBlob = await injectHeader(
        modifiedMediaFile,
        cipher,
        sliders,
        bits,
        deploymentMode,
        mediaType,
      )

      const finalFile = new File([finalBlob], `encoded_${file.name}`, {
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
    sliders,
    handleSliderChange,
    deploymentMode,
    setDeploymentMode,
    loading,
    error,
    resultFile,
    handleEncode,
  }
}
