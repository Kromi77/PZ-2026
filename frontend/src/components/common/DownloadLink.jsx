import { useEffect, useState } from 'react'

export default function DownloadLink({ file, children }) {
  const [downloadUrl, setDownloadUrl] = useState('')

  useEffect(() => {
    if (!file) {
      setDownloadUrl('')
      return undefined
    }

    const objectUrl = URL.createObjectURL(file)
    setDownloadUrl(objectUrl)

    return () => {
      URL.revokeObjectURL(objectUrl)
    }
  }, [file])

  if (!file || !downloadUrl) {
    return null
  }

  return (
    <a
      href={downloadUrl}
      download={file.name}
      className="inline-flex w-full items-center justify-center rounded-xl bg-emerald-400 px-5 py-3 text-sm font-bold text-slate-950 shadow-lg shadow-emerald-950/20 transition-all duration-200 hover:bg-emerald-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-200 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
    >
      {children}
    </a>
  )
}
