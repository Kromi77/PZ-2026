import React, { useEffect, useState } from 'react'
import { UI_TEXT } from '../i18n'
import WaveformCanvas from './common/WaveformCanvas'
import WaveformModal from './common/WaveformModal'
import { createPlayableWavPreviewBlob, useWaveform } from '../hooks/useWaveform'

export default function MediaPreview({ file, label, mediaType }) {
  const { waveformData, isLoading, error } = useWaveform(mediaType === 'wav' ? file : null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [url, setUrl] = useState('')

  useEffect(() => {
    let objectUrl = ''
    let cancelled = false

    async function prepareUrl() {
      if (!file) {
        setUrl('')
        return
      }

      const previewSource = mediaType === 'wav' ? await createPlayableWavPreviewBlob(file) : file

      if (!cancelled) {
        objectUrl = URL.createObjectURL(previewSource)
        setUrl(objectUrl)
      }
    }

    prepareUrl().catch(() => {
      if (!cancelled && file) {
        objectUrl = URL.createObjectURL(file)
        setUrl(objectUrl)
      }
    })

    return () => {
      cancelled = true

      if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
      }
    }
  }, [file, mediaType])

  if (!file || !url) return null

  return (
    <>
      <div className="flex flex-col gap-2 mt-4 items-center w-full">
        <h3 className="font-semibold text-lg">{label}</h3>
        {mediaType === 'bmp' ? (
          <img
            src={url}
            alt={label}
            className="max-w-full h-auto border rounded shadow"
            style={{ maxHeight: '300px' }}
          />
        ) : mediaType === 'wav' ? (
          <div className="w-full">
            {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
            <div className="cursor-pointer" onClick={() => setIsModalOpen(true)}>
              <WaveformCanvas
                waveformData={waveformData}
                height={150}
                color="#3b82f6"
                isLoading={isLoading}
                clickable={true}
              />
            </div>
            <p className="text-xs text-slate-500 mt-1 text-center">
              🔍 Kliknij aby powiększyć
            </p>
            <audio controls src={url} className="w-full mt-3">
              {UI_TEXT.mediaPreview.audioNotSupported}
            </audio>
          </div>
        ) : (
          <audio controls src={url} className="w-full mt-2">
            {UI_TEXT.mediaPreview.audioNotSupported}
          </audio>
        )}
      </div>

      <WaveformModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={label}
      >
        <div className="rounded-lg bg-white p-4">
          <WaveformCanvas
            waveformData={waveformData}
            height={300}
            color="#3b82f6"
            backgroundColor="#f3f4f6"
            isLoading={false}
          />
        </div>
      </WaveformModal>
    </>
  )
}
