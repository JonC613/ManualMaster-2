import PropTypes from 'prop-types';
import TagList from './TagList.jsx';
import { downloadBase64File } from '../utils/download.js';

function ManualDetail({ manual, onDelete }) {
  if (!manual) {
    return <div className="manual-detail">Select a manual to see the details.</div>;
  }

  const handleDownload = () => {
    if (!manual.fileDataBase64) {
      return;
    }

    downloadBase64File(manual.fileDataBase64, manual.fileName ?? `manual-${manual.id}.bin`, manual.fileType ?? 'application/octet-stream');
  };

  return (
    <article className="manual-detail">
      <div className="badge">{manual.category}</div>
      <h2>{manual.title}</h2>
      <div className="tag-list">
        <TagList tags={manual.tags} />
      </div>

      <p>
        Uploaded {new Date(manual.uploadDate).toLocaleString()} — {manual.size} bytes
      </p>

      {manual.sourceUrl && (
        <p>
          Source: <a href={manual.sourceUrl} target="_blank" rel="noreferrer">{manual.sourceUrl}</a>
        </p>
      )}

      <h3>Content</h3>
      <pre>{manual.content}</pre>

      <div className="button-group">
        <button type="button" className="secondary" onClick={() => onDelete(manual.id)}>
          Delete manual
        </button>
        <button type="button" className="primary" onClick={handleDownload} disabled={!manual.fileDataBase64}>
          Download file
        </button>
      </div>
    </article>
  );
}

ManualDetail.propTypes = {
  manual: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    category: PropTypes.string.isRequired,
    tags: PropTypes.arrayOf(PropTypes.string).isRequired,
    content: PropTypes.string.isRequired,
    fileDataBase64: PropTypes.string,
    fileType: PropTypes.string,
    fileName: PropTypes.string,
    uploadDate: PropTypes.string.isRequired,
    size: PropTypes.number.isRequired,
    sourceUrl: PropTypes.string
  }),
  onDelete: PropTypes.func.isRequired
};

ManualDetail.defaultProps = {
  manual: null
};

export default ManualDetail;
