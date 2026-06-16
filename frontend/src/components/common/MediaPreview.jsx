import { useEffect, useState } from 'react'
import { MEDIA_TYPES } from '../../config/appConfig'
import { UI_TEXT } from '../../i18n'

export default function MediaPreview({ file, label, mediaType }) {
  const [previewUrl, setPreviewUrl] = useState('')

  useEffect(() => {
    if (!file) {
      setPreviewUrl('')
      return undefined
    }

    const objectUrl = URL.createObjectURL(file)
    setPreviewUrl(objectUrl)

    return () => {
      URL.revokeObjectURL(objectUrl)
    }
  }, [file])

  if (!file || !previewUrl) {
    return (
      <div className="rounded-2xl border border-white/10 bg-slate-950/45 p-5 text-sm text-slate-500">
        <p className="font-semibold text-slate-300">{label}</p>
        <p className="mt-2">{UI_TEXT.mediaPreview.empty}</p>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/55 p-5 shadow-inner shadow-black/20">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</h3>
        <span className="rounded-full border border-violet-300/20 bg-violet-300/10 px-3 py-1 text-xs font-semibold text-violet-100">
          {mediaType?.toUpperCase()}
        </span>
      </div>

      {mediaType === MEDIA_TYPES.BMP ? (
        <img
          src={previewUrl}
          alt={label}
          className="max-h-80 w-full rounded-xl border border-white/10 object-contain shadow-lg shadow-black/30"
        />
      ) : (
        <audio controls src={previewUrl} className="w-full">
          {UI_TEXT.mediaPreview.audioNotSupported}
        </audio>
      )}
    </div>
  )
}
