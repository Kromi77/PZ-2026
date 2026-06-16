export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:3000'

export const TAB_IDS = {
  ENCODE: 'encode',
  DECODE: 'decode',
}

export const MEDIA_TYPES = {
  BMP: 'bmp',
  WAV: 'wav',
}

export const DEPLOYMENT_MODES = {
  CONTINUOUS: 0,
  UNIFORM: 1,
}
