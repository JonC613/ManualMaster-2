import { useState } from 'react';
import PropTypes from 'prop-types';

const emptyForm = {
  title: '',
  category: 'Other',
  tags: '',
  content: '',
  file: null,
  sourceUrl: '',
  searchQuery: ''
};

function ManualForm({ onSubmit, isBusy }) {
  const [formState, setFormState] = useState(emptyForm);
  const [status, setStatus] = useState(null);

  const updateField = (field, value) => {
    setFormState((previous) => ({ ...previous, [field]: value }));
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] ?? null;
    updateField('file', file);
  };

  const reset = () => {
    setFormState(emptyForm);
    setStatus({ type: 'success', message: 'Manual uploaded successfully.' });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const payload = {
      title: formState.title,
      category: formState.category,
      tags: formState.tags
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean),
      content: formState.content,
      sourceUrl: formState.sourceUrl || null,
      searchQuery: formState.searchQuery || null,
      fileName: formState.file?.name ?? null,
      fileType: formState.file?.type ?? null,
      fileDataBase64: null
    };

    if (formState.file) {
      const buffer = await formState.file.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = '';
      bytes.forEach((b) => {
        binary += String.fromCharCode(b);
      });
      payload.fileDataBase64 = btoa(binary);
    }

    const result = await onSubmit(payload);

    if (result) {
      reset();
    } else {
      setStatus({ type: 'error', message: 'Unable to save manual. Please try again.' });
    }
  };

  return (
    <form className="form-section" onSubmit={handleSubmit}>
      <h2>Add manual</h2>
      <label htmlFor="manual-title">Title</label>
      <input
        id="manual-title"
        required
        value={formState.title}
        onChange={(event) => updateField('title', event.target.value)}
        placeholder="User manual title"
      />

      <label htmlFor="manual-category">Category</label>
      <input
        id="manual-category"
        value={formState.category}
        onChange={(event) => updateField('category', event.target.value)}
        placeholder="Appliance, Tech, ..."
      />

      <label htmlFor="manual-tags">Tags</label>
      <input
        id="manual-tags"
        value={formState.tags}
        onChange={(event) => updateField('tags', event.target.value)}
        placeholder="Comma separated"
      />

      <label htmlFor="manual-content">Content</label>
      <textarea
        id="manual-content"
        required
        rows={6}
        value={formState.content}
        onChange={(event) => updateField('content', event.target.value)}
        placeholder="Paste text from the manual here"
      />

      <label htmlFor="manual-file">Attach file (optional)</label>
      <input id="manual-file" type="file" onChange={handleFileChange} />

      <label htmlFor="manual-source">Source URL</label>
      <input
        id="manual-source"
        value={formState.sourceUrl}
        onChange={(event) => updateField('sourceUrl', event.target.value)}
        placeholder="https://example.com/manual.pdf"
      />

      <label htmlFor="manual-search">Search query</label>
      <input
        id="manual-search"
        value={formState.searchQuery}
        onChange={(event) => updateField('searchQuery', event.target.value)}
        placeholder="Keywords used to find the manual"
      />

      <button type="submit" className="primary" disabled={isBusy}>
        {isBusy ? 'Saving…' : 'Save manual'}
      </button>

      {status && <div className={`status-banner ${status.type}`}>{status.message}</div>}
    </form>
  );
}

ManualForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isBusy: PropTypes.bool
};

ManualForm.defaultProps = {
  isBusy: false
};

export default ManualForm;
