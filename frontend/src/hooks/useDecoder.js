import { useState } from 'react'
import { decodeFile } from '../api/steganographyApi'
import { useMediaFile } from './useMediaFile'
import { UI_TEXT } from '../i18n'

export function useDecoder() {
  const [key, setKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const { file, mediaType, handleFileChange } = useMediaFile({
    onFileSelected: () => {
      setError('')
      setResult(null)
    },
  })

  async function handleDecode() {
    if (!file) {
      setError(UI_TEXT.errors.missingFile)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const decodedResult = await decodeFile(file, mediaType, key)
      setResult(decodedResult)
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
    key,
    setKey,
    loading,
    error,
    result,
    handleDecode,
  }
}
