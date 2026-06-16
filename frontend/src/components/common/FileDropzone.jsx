import { formatFileSize } from '../../utils/formatFileSize'

export default function FileDropzone({ label, selectedFile, onChange, accept = '.bmp,.wav', hint }) {
  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-semibold text-slate-200">{label}</span>

      <label className="group relative flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-violet-300/35 bg-slate-900/70 px-6 py-7 text-center transition-all duration-200 hover:border-violet-300/70 hover:bg-slate-900/95 hover:shadow-[0_0_40px_rgba(139,92,246,0.12)]">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/10 text-violet-200 transition-transform duration-200 group-hover:-translate-y-0.5">
          <svg
            className="h-6 w-6"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 16"
          >
            <path
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
            />
          </svg>
        </div>

        <span className="text-sm font-semibold text-slate-100">
          {selectedFile ? selectedFile.name : 'Kliknij, aby wybrać plik'}
        </span>

        <span className="mt-1 text-xs text-slate-400">
          {selectedFile ? formatFileSize(selectedFile.size) : hint}
        </span>

        <input type="file" accept={accept} onChange={onChange} className="sr-only" />
      </label>
    </div>
  )
}
