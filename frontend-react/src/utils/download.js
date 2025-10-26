export function downloadBase64File(base64, filename, mimeType) {
  if (!base64) {
    return;
  }

  const link = document.createElement('a');
  link.href = `data:${mimeType};base64,${base64}`;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
