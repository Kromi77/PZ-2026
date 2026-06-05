const API_BASE = 'http://127.0.0.1:3000';

export const CipherType = {
  CEZAR: "Szyfr Cezara",
  VIGENERE: "Szyfr Vigenere'a",
  XOR: "Szyfr XOR",
  ATBASH: "Szyfr Atbash",
  ROT13: "ROT13",
  RAIL_FENCE: "Szyfr płotkowy",
  COLUMNAR: "Szyfr kolumnowy",
};

export async function encryptText(cipher, text, key) {
  let endpoint = '';
  let body = { text };

  switch (cipher) {
    case CipherType.CEZAR:
      endpoint = '/caesar/encrypt';
      body.shift = parseInt(key, 10);
      break;
    case CipherType.VIGENERE:
      endpoint = '/vinegre/encrypt';
      body.key = String(key);
      break;
    case CipherType.XOR:
      endpoint = '/encrypt/xor';
      body.key = String(key);
      break;
    case CipherType.ATBASH:
      endpoint = '/atbash/encrypt';
      // no key
      break;
    case CipherType.ROT13:
      endpoint = '/rot13/process';
      // no key
      break;
    case CipherType.RAIL_FENCE:
      endpoint = '/railfence/encrypt';
      body.rails = parseInt(key, 10);
      break;
    case CipherType.COLUMNAR:
      endpoint = '/columnar/encrypt';
      body.key = String(key);
      break;
    default:
      throw new Error(`Unsupported cipher: ${cipher}`);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Encryption failed');
  }

  const data = await response.json();
  return data.output;
}

export async function hideSteganography(file, encryptedMessage, mediaType) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('encrypted_message', encryptedMessage);
  formData.append('media_type', mediaType); // 'bmp' or 'wav'

  const response = await fetch(`${API_BASE}/steganography/hide`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Steganography hide failed');
  }

  // Returns file blob
  return await response.blob();
}

export async function injectHeader(file, cipher, sliders, bits, deploymentMode, mediaType) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('cipher', cipher);
  
  if (mediaType === 'bmp') {
    formData.append('sliderR', sliders[0] || 0);
    formData.append('sliderG', sliders[1] || 0);
    formData.append('sliderB', sliders[2] || 0);
  } else {
    formData.append('slider', sliders[0] || 0);
  }
  
  formData.append('bits', bits);
  formData.append('deployment_mode', deploymentMode);

  const endpoint = mediaType === 'bmp' ? '/header/inject-bmp/' : '/header/inject-wav/';
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Header injection failed');
  }

  return await response.blob();
}

export async function decodeFile(file, mediaType, key = '') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('media_type', mediaType);
  formData.append('key', key);

  const response = await fetch(`${API_BASE}/decoder/process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Decoding failed');
  }

  return await response.json();
}
