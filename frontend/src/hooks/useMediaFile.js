import { useState } from 'react'
import { MEDIA_TYPES } from '../config/appConfig'
import { detectMediaType } from '../utils/detectMediaType'

export function useMediaFile({ onFileSelected } = {}) {
  const [file, setFile] = useState(null)
  const [mediaType, setMediaType] = useState(MEDIA_TYPES.BMP)

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0]

    if (!selectedFile) {
      return
    }

    setFile(selectedFile)
    setMediaType(detectMediaType(selectedFile))
    onFileSelected?.(selectedFile)
  }

  function resetFile() {
    setFile(null)
    setMediaType(MEDIA_TYPES.BMP)
  }

  return {
    file,
    mediaType,
    handleFileChange,
    resetFile,
  }
}
