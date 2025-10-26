import PropTypes from 'prop-types';
import TagList from './TagList.jsx';

function ManualList({ manuals, onSelectManual, selectedManualId, isLoading }) {
  if (isLoading && manuals.length === 0) {
    return <div className="manual-detail">Loading manuals...</div>;
  }

  if (!isLoading && manuals.length === 0) {
    return <div className="manual-detail">No manuals found. Try uploading one!</div>;
  }

  return (
    <div className="manual-grid">
      {manuals.map((manual) => (
        <article
          key={manual.id}
          className="manual-card"
          onClick={() => onSelectManual(manual.id)}
          role="button"
        >
          <div className="badge">{manual.category}</div>
          <h3>{manual.title}</h3>
          <div className="tag-list">
            <TagList tags={manual.tags} />
          </div>
          <small>{new Date(manual.uploadDate).toLocaleString()}</small>
          {selectedManualId === manual.id && <small>Currently viewing</small>}
        </article>
      ))}
    </div>
  );
}

ManualList.propTypes = {
  manuals: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      category: PropTypes.string.isRequired,
      tags: PropTypes.arrayOf(PropTypes.string).isRequired,
      uploadDate: PropTypes.string.isRequired
    })
  ).isRequired,
  onSelectManual: PropTypes.func.isRequired,
  selectedManualId: PropTypes.number,
  isLoading: PropTypes.bool
};

ManualList.defaultProps = {
  selectedManualId: null,
  isLoading: false
};

export default ManualList;
