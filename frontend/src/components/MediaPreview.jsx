import React from 'react';
import { UI_TEXT } from '../i18n';

export default function MediaPreview({ file, label, mediaType }) {
  if (!file) return null;

  const url = URL.createObjectURL(file);

  return (
    <div className="flex flex-col gap-2 mt-4 items-center">
      <h3 className="font-semibold text-lg">{label}</h3>
      {mediaType === 'bmp' ? (
        <img src={url} alt={label} className="max-w-full h-auto border rounded shadow" style={{maxHeight: '300px'}} />
      ) : (
        <audio controls src={url} className="w-full mt-2">
          {UI_TEXT.mediaPreview.audioNotSupported}
        </audio>
      )}
    </div>
  );
}
