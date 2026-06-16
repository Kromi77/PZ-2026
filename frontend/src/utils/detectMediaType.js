import { MEDIA_TYPES } from '../config/appConfig'

export function detectMediaType(file) {
  if (!file) {
    return MEDIA_TYPES.BMP
  }

  const fileName = file.name.toLowerCase()

  if (fileName.endsWith('.wav')) {
    return MEDIA_TYPES.WAV
  }

  return MEDIA_TYPES.BMP
}
