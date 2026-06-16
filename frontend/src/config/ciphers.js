export const CIPHER_TYPES = {
  CEZAR: 'Szyfr Cezara',
  VIGENERE: "Szyfr Vigenere'a",
  XOR: 'Szyfr XOR',
  ATBASH: 'Szyfr Atbash',
  ROT13: 'ROT13',
  RAIL_FENCE: 'Szyfr płotkowy',
  COLUMNAR: 'Szyfr kolumnowy',
}

export const CIPHER_OPTIONS = [
  {
    id: CIPHER_TYPES.CEZAR,
    label: CIPHER_TYPES.CEZAR,
    requiresKey: true,
    defaultKey: '3',
    keyType: 'number',
  },
  {
    id: CIPHER_TYPES.VIGENERE,
    label: CIPHER_TYPES.VIGENERE,
    requiresKey: true,
    defaultKey: 'SECRET',
    keyType: 'text',
  },
  {
    id: CIPHER_TYPES.XOR,
    label: CIPHER_TYPES.XOR,
    requiresKey: true,
    defaultKey: 'SECRET',
    keyType: 'text',
  },
  {
    id: CIPHER_TYPES.ATBASH,
    label: CIPHER_TYPES.ATBASH,
    requiresKey: false,
    defaultKey: '',
    keyType: 'none',
  },
  {
    id: CIPHER_TYPES.ROT13,
    label: CIPHER_TYPES.ROT13,
    requiresKey: false,
    defaultKey: '',
    keyType: 'none',
  },
  {
    id: CIPHER_TYPES.RAIL_FENCE,
    label: CIPHER_TYPES.RAIL_FENCE,
    requiresKey: true,
    defaultKey: '3',
    keyType: 'number',
  },
  {
    id: CIPHER_TYPES.COLUMNAR,
    label: CIPHER_TYPES.COLUMNAR,
    requiresKey: true,
    defaultKey: 'SECRET',
    keyType: 'text',
  },
]

export function getCipherConfig(cipher) {
  return CIPHER_OPTIONS.find((option) => option.id === cipher)
}

export function getDefaultKeyForCipher(cipher) {
  return getCipherConfig(cipher)?.defaultKey ?? ''
}

export function cipherRequiresKey(cipher) {
  return getCipherConfig(cipher)?.requiresKey ?? false
}
