import Alert from "../components/common/Alert";
import Button from "../components/common/Button";
import DownloadLink from "../components/common/DownloadLink";
import FileDropzone from "../components/common/FileDropzone";
import FormField from "../components/common/FormField";
import MediaPreview from "../components/common/MediaPreview";
import SliderControl from "../components/common/SliderControl";
import WaveformComparison from "../components/WaveformComparison";
import { DEPLOYMENT_MODES, MEDIA_TYPES } from "../config/appConfig";
import { CIPHER_OPTIONS, cipherRequiresKey } from "../config/ciphers";
import { useEncoder } from "../hooks/useEncoder";
import { UI_TEXT } from "../i18n";

const inputClassName =
  "w-full rounded-2xl border border-white/10 bg-gradient-to-b from-slate-900/80 to-slate-950/80 px-4 py-3 text-sm text-slate-100 outline-none shadow-inner shadow-black/20 transition-all duration-300 placeholder:text-slate-600 hover:border-white/20 hover:bg-slate-900/80 focus:border-white/20 focus:bg-slate-900/90 focus:shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_10px_30px_rgba(15,23,42,0.35)] focus:ring-0";

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
        name="deployment"
        checked={checked}
        onChange={onChange}
        className="sr-only"
      />

      <span className="text-sm font-semibold">{label}</span>
    </label>
  );
}

export default function EncodeView() {
  const {
    text,
    setText,
    cipher,
    handleCipherChange,
    key,
    setKey,
    file,
    mediaType,
    handleFileChange,
    sliders,
    handleSliderChange,
    deploymentMode,
    setDeploymentMode,
    loading,
    error,
    resultFile,
    handleEncode,
  } = useEncoder();

  const showKeyField = cipherRequiresKey(cipher);

  return (
    <div className="grid gap-0 lg:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
      <section className="border-b border-white/10 p-5 sm:p-7 lg:border-b-0 lg:border-r lg:border-white/10">
        <div className="mb-6">
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-violet-200">
            {UI_TEXT.encoder.eyebrow}
          </p>

          <h2 className="mt-2 text-2xl font-black tracking-tight text-white sm:text-3xl">
            {UI_TEXT.encoder.title}
          </h2>

          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">
            {UI_TEXT.encoder.description}
          </p>
        </div>

        <div className="space-y-5">
          <Alert message={error} />

          <FormField label={UI_TEXT.encoder.textToHide}>
            <textarea
              className={`${inputClassName} min-h-32 resize-y`}
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder={UI_TEXT.encoder.textPlaceholder}
            />
          </FormField>

          <div className="grid gap-4 sm:grid-cols-2">
            <FormField label={UI_TEXT.encoder.cipherMethod}>
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
              <FormField label={UI_TEXT.encoder.key}>
                <input
                  type="text"
                  className={inputClassName}
                  value={key}
                  onChange={(event) => setKey(event.target.value)}
                  placeholder={UI_TEXT.encoder.keyPlaceholder}
                />
              </FormField>
            )}
          </div>

          <FileDropzone
            label={UI_TEXT.encoder.carrierFile}
            selectedFile={file}
            onChange={handleFileChange}
            hint={UI_TEXT.encoder.allowedFiles}
          />

          <div className="rounded-3xl border border-white/10 bg-white/3 p-5">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-slate-100">
                {mediaType === MEDIA_TYPES.BMP
                  ? UI_TEXT.encoder.bmpSliders
                  : UI_TEXT.encoder.wavSlider}
              </h3>

              <p className="mt-1 text-xs leading-relaxed text-slate-400">
                {UI_TEXT.encoder.slidersHint}
              </p>
            </div>

            {mediaType === MEDIA_TYPES.BMP ? (
              <div className="grid gap-3 sm:grid-cols-3">
                <SliderControl
                  label="R"
                  value={sliders[0]}
                  onChange={(value) => handleSliderChange(0, value)}
                />

                <SliderControl
                  label="G"
                  value={sliders[1]}
                  onChange={(value) => handleSliderChange(1, value)}
                />

                <SliderControl
                  label="B"
                  value={sliders[2]}
                  onChange={(value) => handleSliderChange(2, value)}
                />
              </div>
            ) : (
              <SliderControl
                label={UI_TEXT.encoder.sliderValue}
                value={sliders[0]}
                onChange={(value) => handleSliderChange(0, value)}
              />
            )}
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/3 p-5">
            <h3 className="mb-3 text-sm font-bold text-slate-100">
              {UI_TEXT.encoder.deploymentMode}
            </h3>

            <div className="grid gap-3 sm:grid-cols-2">
              <DeploymentOption
                label={UI_TEXT.encoder.continuous}
                checked={deploymentMode === DEPLOYMENT_MODES.CONTINUOUS}
                onChange={() => setDeploymentMode(DEPLOYMENT_MODES.CONTINUOUS)}
              />

              <DeploymentOption
                label={UI_TEXT.encoder.uniform}
                checked={deploymentMode === DEPLOYMENT_MODES.UNIFORM}
                onChange={() => setDeploymentMode(DEPLOYMENT_MODES.UNIFORM)}
              />
            </div>
          </div>

          <Button onClick={handleEncode} disabled={loading} className="w-full">
            {loading ? UI_TEXT.encoder.encoding : UI_TEXT.encoder.encodeButton}
          </Button>
        </div>
      </section>

      <aside className="flex flex-col gap-5 bg-slate-950/25 p-5 sm:p-7">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-emerald-200">
            {UI_TEXT.encoder.previewPanel}
          </p>

          <h3 className="mt-2 text-xl font-black tracking-tight text-white">
            Podgląd nośnika
          </h3>
        </div>

        <MediaPreview
          file={file}
          label={UI_TEXT.encoder.originalMedia}
          mediaType={mediaType}
        />

        <MediaPreview
          file={resultFile}
          label={UI_TEXT.encoder.encodedMedia}
          mediaType={mediaType}
        />

        {mediaType === MEDIA_TYPES.WAV && file && resultFile && (
          <WaveformComparison originalFile={file} encodedFile={resultFile} />
        )}

        {resultFile ? (
          <DownloadLink file={resultFile}>
            {UI_TEXT.encoder.downloadEncodedFile}
          </DownloadLink>
        ) : (
          <div className="rounded-2xl border border-white/10 bg-slate-950/45 p-5 text-sm leading-6 text-slate-500">
            {UI_TEXT.encoder.noResult}
          </div>
        )}
      </aside>
    </div>
  );
}
