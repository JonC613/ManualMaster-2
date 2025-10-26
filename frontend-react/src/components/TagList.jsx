import PropTypes from 'prop-types';

function TagList({ tags }) {
  if (!tags || tags.length === 0) {
    return <span className="tag">No tags</span>;
  }

  return tags.map((tag) => (
    <span key={tag} className="tag">
      #{tag}
    </span>
  ));
}

TagList.propTypes = {
  tags: PropTypes.arrayOf(PropTypes.string)
};

TagList.defaultProps = {
  tags: []
};

export default TagList;
