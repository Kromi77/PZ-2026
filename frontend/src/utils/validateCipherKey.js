import { UI_TEXT } from '../i18n'
import { CIPHER_TYPES, cipherRequiresKey } from '../config/ciphers'

export function validateCipherKey(cipher, key) {
  if (!cipherRequiresKey(cipher)) {
    return ''
  }

  const trimmedKey = key.trim()

  if (!trimmedKey) {
    return UI_TEXT.errors.missingKey
  }

  if (cipher === CIPHER_TYPES.CEZAR && !/^-?\d+$/.test(trimmedKey)) {
    return UI_TEXT.errors.invalidCaesarKey
  }

  if (
    cipher === CIPHER_TYPES.RAIL_FENCE &&
    (!/^\d+$/.test(trimmedKey) || Number(trimmedKey) < 2)
  ) {
    return UI_TEXT.errors.invalidRailFenceKey
  }

  return ''
}
