import Alert from "../components/common/Alert";
import Button from "../components/common/Button";
import FileDropzone from "../components/common/FileDropzone";
import FormField from "../components/common/FormField";
import MediaPreview from "../components/common/MediaPreview";
import WaveformComparison from "../components/WaveformComparison";
import { DEPLOYMENT_MODES } from "../config/appConfig";
import { CIPHER_OPTIONS, cipherRequiresKey } from "../config/ciphers";
import { useDecoder } from "../hooks/useDecoder";
import { UI_TEXT } from "../i18n";

const inputClassName =
  "w-full rounded-2xl border border-white/10 bg-gradient-to-b from-slate-900/80 to-slate-950/80 px-4 py-3 text-sm text-slate-100 outline-none shadow-inner shadow-black/20 transition-all duration-300 placeholder:text-slate-600 hover:border-white/20 hover:bg-slate-900/80 focus:border-white/20 focus:bg-slate-900/90 focus:shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_10px_30px_rgba(15,23,42,0.35)] focus:ring-0";

function ResultRow({ label, value }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-white/10 py-3 last:border-b-0">
      <span className="text-sm text-slate-400">{label}</span>

      <span className="text-right text-sm font-semibold text-slate-100">
        {value || "-"}
      </span>
    </div>
  );
}

function DeploymentOption({ label, checked, onChange }) {
  return (
    <label
      className={`cursor-pointer rounded-2xl border p-4 transition-all duration-300 ${
        checked
          ? "border-violet-300/50 bg-violet-300/10 text-violet-50 shadow-inner shadow-violet-950/20"
          : "border-white/10 bg-slate-950/40 text-slate-300 hover:border-white/20 hover:bg-white/4 hover:text-slate-100"
      }`}
    >
      <input
        type="radio"
        name="decode-deployment"
        checked={checked}
        onChange={onChange}
        className="sr-only"
      />

      <span className="text-sm font-semibold">{label}</span>
    </label>
  );
}

export default function DecodeView() {
  const {
    file,
    mediaType,
    handleFileChange,
    cipher,
    handleCipherChange,
    key,
    setKey,
    deploymentMode,
    handleDeploymentModeChange,
    loading,
    error,
    result,
    handleDecode,
  } = useDecoder();

  const showKeyField = cipherRequiresKey(cipher);

  return (
    <div className="grid gap-0 lg:grid-cols-[minmax(0,1.02fr)_minmax(320px,0.98fr)]">
      <section className="border-b border-white/10 p-5 sm:p-7 lg:border-b-0 lg:border-r lg:border-white/10">
        <div className="mb-6">
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-violet-200">
            {UI_TEXT.decoder.eyebrow}
          </p>

          <h2 className="mt-2 text-2xl font-black tracking-tight text-white sm:text-3xl">
            {UI_TEXT.decoder.title}
          </h2>

          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
            {UI_TEXT.decoder.description}
          </p>
        </div>

        <div className="space-y-5">
          <Alert message={error} />

          <FileDropzone
            label={UI_TEXT.decoder.encodedFile}
            selectedFile={file}
            onChange={handleFileChange}
            hint={UI_TEXT.decoder.allowedFiles}
          />

          <div className="grid gap-4 sm:grid-cols-2">
            <FormField label="Szyfr użyty przy kodowaniu">
              <select
                className={inputClassName}
                value={cipher}
                onChange={(event) => handleCipherChange(event.target.value)}
              >
                {CIPHER_OPTIONS.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </FormField>

            {showKeyField && (
              <FormField
                label={UI_TEXT.decoder.key}
                hint={UI_TEXT.decoder.keyHint}
              >
                <input
                  type="text"
                  value={key}
                  onChange={(event) => setKey(event.target.value)}
                  placeholder={UI_TEXT.decoder.keyPlaceholder}
                  className={inputClassName}
                />
              </FormField>
            )}
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/3 p-5">
            <h3 className="mb-3 text-sm font-bold text-slate-100">
              Tryb rozmieszczenia użyty przy kodowaniu
            </h3>

            <div className="grid gap-3 sm:grid-cols-2">
              <DeploymentOption
                label={UI_TEXT.encoder.continuous}
                checked={deploymentMode === DEPLOYMENT_MODES.CONTINUOUS}
                onChange={() => handleDeploymentModeChange(DEPLOYMENT_MODES.CONTINUOUS)}
              />

              <DeploymentOption
                label={UI_TEXT.encoder.uniform}
                checked={deploymentMode === DEPLOYMENT_MODES.UNIFORM}
                onChange={() => handleDeploymentModeChange(DEPLOYMENT_MODES.UNIFORM)}
              />
            </div>
          </div>

          <Button onClick={handleDecode} disabled={loading} className="w-full">
            {loading ? UI_TEXT.decoder.decoding : UI_TEXT.decoder.decodeButton}
          </Button>

          <MediaPreview
            file={file}
            label={UI_TEXT.decoder.selectedMedia}
            mediaType={mediaType}
          />
        </div>
      </section>

      <aside className="flex flex-col gap-5 bg-slate-950/25 p-5 sm:p-7">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-emerald-200">
            {UI_TEXT.decoder.results}
          </p>

          <h3 className="mt-2 text-xl font-black tracking-tight text-white">
            Raport dekodowania
          </h3>
        </div>

        {result ? (
          <div className="rounded-3xl border border-white/10 bg-slate-950/55 p-5 shadow-inner shadow-black/20">
            <div className="rounded-2xl border border-white/10 bg-white/3 px-4">
              <ResultRow
                label={UI_TEXT.decoder.messageDetected}
                value={
                  result.message_detected
                    ? UI_TEXT.common.yes
                    : UI_TEXT.common.no
                }
              />

              <ResultRow
                label={UI_TEXT.decoder.cipherUsed}
                value={result.cipher_used}
              />

              <ResultRow
                label={UI_TEXT.decoder.deploymentMode}
                value={result.deployment_mode}
              />

              <ResultRow
                label={UI_TEXT.decoder.bitsExtracted}
                value={result.bits_extracted}
              />
            </div>

            <div className="mt-5">
              <p className="mb-2 text-sm font-bold text-slate-200">
                Zaszyfrowany tekst wyciągnięty z pliku
              </p>

              <div className="min-h-20 whitespace-pre-wrap rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-100">
                {result.encrypted_text || "-"}
              </div>
            </div>

            <div className="mt-5">
              <p className="mb-2 text-sm font-bold text-slate-200">
                {UI_TEXT.decoder.decryptedText}
              </p>

              <div className="min-h-32 whitespace-pre-wrap rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-4 text-sm leading-6 text-emerald-50">
                {result.decrypted_text || "-"}
              </div>
            </div>

            {file && mediaType === "wav" && (
              <div className="mt-5">
                <WaveformComparison encodedFile={file} />
              </div>
            )}
          </div>
        ) : (
          <div className="flex min-h-80 items-center justify-center rounded-3xl border border-dashed border-white/10 bg-slate-950/45 p-8 text-center text-sm leading-6 text-slate-500">
            {UI_TEXT.decoder.uploadHint}
          </div>
        )}
      </aside>
    </div>
  );
}
