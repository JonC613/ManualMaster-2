import PropTypes from 'prop-types';

function SearchFilters({ searchTerm, onSearchTermChange, categories, selectedCategory, onCategoryChange, isLoading }) {
  return (
    <section className="form-section">
      <h2>Search manuals</h2>
      <label htmlFor="search-query">Search</label>
      <input
        id="search-query"
        value={searchTerm}
        onChange={(event) => onSearchTermChange(event.target.value)}
        placeholder="Search by title, category or tags"
      />

      <label htmlFor="search-category">Category</label>
      <select
        id="search-category"
        value={selectedCategory}
        onChange={(event) => onCategoryChange(event.target.value)}
        disabled={isLoading}
      >
        {categories.map((category) => (
          <option key={category.value} value={category.value}>
            {category.label}
          </option>
        ))}
      </select>
    </section>
  );
}

SearchFilters.propTypes = {
  searchTerm: PropTypes.string.isRequired,
  onSearchTermChange: PropTypes.func.isRequired,
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired
    })
  ).isRequired,
  selectedCategory: PropTypes.string.isRequired,
  onCategoryChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

SearchFilters.defaultProps = {
  isLoading: false
};

export default SearchFilters;
