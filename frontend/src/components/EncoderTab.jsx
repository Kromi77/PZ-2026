import React, { useState } from 'react';
import { CipherType, encryptText, hideSteganography, injectHeader } from '../api';
import MediaPreview from './MediaPreview';

export default function EncoderTab() {
  const [text, setText] = useState('');
  const [cipher, setCipher] = useState(CipherType.CEZAR);
  const [key, setKey] = useState('3');
  const [file, setFile] = useState(null);
  const [mediaType, setMediaType] = useState('bmp'); // 'bmp' | 'wav'
  const [sliders, setSliders] = useState([0, 0, 0]); // R, G, B for BMP. For WAV, use sliders[0]
  const [deploymentMode, setDeploymentMode] = useState(0); // 0 = Ciągłe, 1 = Równomierne
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resultFile, setResultFile] = useState(null);

  const handleCipherChange = (e) => {
    const newCipher = e.target.value;
    setCipher(newCipher);
    // Set sensible default keys
    if (newCipher === CipherType.CEZAR || newCipher === CipherType.RAIL_FENCE) {
      setKey('3');
    } else if (newCipher === CipherType.VIGENERE || newCipher === CipherType.COLUMNAR || newCipher === CipherType.XOR) {
      setKey('SECRET');
    } else {
      setKey('');
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setResultFile(null); // reset
      if (selectedFile.name.toLowerCase().endsWith('.wav')) {
        setMediaType('wav');
      } else {
        setMediaType('bmp');
      }
    }
  };

  const handleSliderChange = (index, value) => {
    const newSliders = [...sliders];
    newSliders[index] = parseInt(value, 10);
    setSliders(newSliders);
  };

  const handleEncode = async () => {
    if (!text) {
      setError('Please enter some text to encrypt.');
      return;
    }
    if (!file) {
      setError('Please select a file.');
      return;
    }

    setLoading(true);
    setError('');
    setResultFile(null);

    try {
      // 1. Encrypt Text
      const encryptedText = await encryptText(cipher, text, key);
      
      // Calculate bits required
      const bits = new Blob([encryptedText]).size * 8 + 32; // 32 bits for the length prefix

      // 2. Hide message using Steganography
      const modifiedMediaBlob = await hideSteganography(file, encryptedText, mediaType);
      
      // 3. Inject Header
      // Create a File object from the Blob to pass to injectHeader
      const modifiedMediaFile = new File([modifiedMediaBlob], file.name, { type: file.type });
      const finalBlob = await injectHeader(modifiedMediaFile, cipher, sliders, bits, deploymentMode, mediaType);
      
      // 4. Create result File
      const finalFile = new File([finalBlob], `encoded_${file.name}`, { type: file.type });
      setResultFile(finalFile);

    } catch (err) {
      setError(err.message || 'An error occurred during encoding');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6 max-w-4xl mx-auto w-full text-left">
      <h2 className="text-2xl font-bold border-b pb-2">Encoder</h2>
      
      {error && <div className="p-4 bg-red-100 text-red-700 rounded border border-red-300">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="font-semibold text-gray-700">Text to hide</label>
            <textarea 
              className="border border-gray-300 p-2 rounded h-24 text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={text} 
              onChange={(e) => setText(e.target.value)} 
              placeholder="Secret message..."
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-semibold text-gray-700">Cipher Method</label>
            <select 
              className="border border-gray-300 p-2 rounded text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-purple-500" 
              value={cipher} 
              onChange={handleCipherChange}
            >
              {Object.values(CipherType).map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {cipher !== CipherType.ATBASH && cipher !== CipherType.ROT13 && (
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-gray-700">Key</label>
              <input 
                type="text" 
                className="border border-gray-300 p-2 rounded text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-purple-500" 
                value={key} 
                onChange={(e) => setKey(e.target.value)} 
                placeholder="Enter key"
              />
            </div>
          )}

          <div className="flex flex-col gap-2">
            <label className="font-semibold text-gray-700">Carrier File (.bmp, .wav)</label>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-purple-300 border-dashed rounded-lg cursor-pointer bg-purple-50 hover:bg-purple-100 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6 text-purple-700">
                <svg className="w-8 h-8 mb-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                </svg>
                <p className="mb-2 text-sm"><span className="font-semibold">Click to upload</span></p>
                <p className="text-xs">.BMP or .WAV files</p>
              </div>
              <input type="file" accept=".bmp,.wav" onChange={handleFileChange} className="hidden" />
            </label>
            {file && <p className="text-sm text-green-600 font-semibold truncate">Selected: {file.name}</p>}
          </div>

          {mediaType === 'bmp' && (
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-gray-700">BMP Sliders (0-8 bits/pixel)</label>
              <div className="flex gap-4">
                <div className="flex flex-col items-center">
                  <span className="text-sm font-medium text-gray-600">R: {sliders[0]}</span>
                  <input type="range" min="0" max="8" value={sliders[0]} onChange={(e) => handleSliderChange(0, e.target.value)} className="w-20" />
                </div>
                <div className="flex flex-col items-center">
                  <span className="text-sm font-medium text-gray-600">G: {sliders[1]}</span>
                  <input type="range" min="0" max="8" value={sliders[1]} onChange={(e) => handleSliderChange(1, e.target.value)} className="w-20" />
                </div>
                <div className="flex flex-col items-center">
                  <span className="text-sm font-medium text-gray-600">B: {sliders[2]}</span>
                  <input type="range" min="0" max="8" value={sliders[2]} onChange={(e) => handleSliderChange(2, e.target.value)} className="w-20" />
                </div>
              </div>
            </div>
          )}

          {mediaType === 'wav' && (
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-gray-700">WAV Slider (0-8 LSB)</label>
              <div className="flex flex-col items-start">
                <span className="text-sm font-medium text-gray-600">Value: {sliders[0]}</span>
                <input type="range" min="0" max="8" value={sliders[0]} onChange={(e) => handleSliderChange(0, e.target.value)} className="w-full" />
              </div>
            </div>
          )}

          <div className="flex flex-col gap-2">
            <label className="font-semibold text-gray-700">Deployment Mode</label>
            <div className="flex gap-4 text-gray-800">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="deployment" checked={deploymentMode === 0} onChange={() => setDeploymentMode(0)} className="text-purple-600" />
                Ciągłe
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="deployment" checked={deploymentMode === 1} onChange={() => setDeploymentMode(1)} className="text-purple-600" />
                Równomierne
              </label>
            </div>
          </div>

          <button 
            className="mt-4 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded shadow transition-colors disabled:opacity-50"
            onClick={handleEncode}
            disabled={loading}
          >
            {loading ? 'Encoding...' : 'Encode & Hide'}
          </button>
        </div>

        <div className="flex flex-col gap-4 border-l border-gray-200 pl-8">
          <MediaPreview file={file} label="Original Media" mediaType={mediaType} />
          <MediaPreview file={resultFile} label="Encoded Media" mediaType={mediaType} />
          
          {resultFile && (
            <div className="flex justify-center mt-4">
              <a 
                href={URL.createObjectURL(resultFile)} 
                download={resultFile.name}
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded shadow transition-colors"
              >
                Download Encoded File
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
