import React, { useState } from 'react';
import { decodeFile } from '../api';
import MediaPreview from './MediaPreview';

export default function DecoderTab() {
  const [file, setFile] = useState(null);
  const [mediaType, setMediaType] = useState('bmp'); // 'bmp' | 'wav'
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setResult(null);
      if (selectedFile.name.toLowerCase().endsWith('.wav')) {
        setMediaType('wav');
      } else {
        setMediaType('bmp');
      }
    }
  };

  const handleDecode = async () => {
    if (!file) {
      setError('Please select a file.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await decodeFile(file, mediaType);
      setResult(res);
    } catch (err) {
      setError(err.message || 'An error occurred during decoding');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6 max-w-4xl mx-auto w-full text-left">
      <h2 className="text-2xl font-bold border-b pb-2">Decoder</h2>
      
      {error && <div className="p-4 bg-red-100 text-red-700 rounded border border-red-300">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="font-semibold text-gray-700">Encoded File (.bmp, .wav)</label>
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

          <button 
            className="mt-4 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded shadow transition-colors disabled:opacity-50"
            onClick={handleDecode}
            disabled={loading}
          >
            {loading ? 'Decoding...' : 'Extract & Decode'}
          </button>

          <MediaPreview file={file} label="Selected Media" mediaType={mediaType} />
        </div>

        <div className="flex flex-col gap-4 border-l border-gray-200 pl-8">
          <h3 className="text-xl font-bold mb-2">Results</h3>
          {result ? (
            <div className="flex flex-col gap-3 p-4 bg-gray-50 border rounded text-gray-900 shadow-sm">
              <div className="grid grid-cols-2 gap-2 text-sm border-b pb-3">
                <span className="font-semibold text-gray-600">Message Detected:</span>
                <span>{result.message_detected ? 'Yes' : 'No'}</span>
                
                <span className="font-semibold text-gray-600">Cipher Used:</span>
                <span>{result.cipher_used}</span>
                
                <span className="font-semibold text-gray-600">Deployment Mode:</span>
                <span>{result.deployment_mode}</span>
                
                <span className="font-semibold text-gray-600">Bits Extracted:</span>
                <span>{result.bits_extracted}</span>
              </div>
              <div className="pt-2">
                <p className="font-bold text-gray-700 mb-2">Decrypted Text:</p>
                <div className="p-3 bg-white border rounded whitespace-pre-wrap text-base">
                  {result.decrypted_text}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 italic">Upload an encoded file and click Decode to see results here.</div>
          )}
        </div>
      </div>
    </div>
  );
}
