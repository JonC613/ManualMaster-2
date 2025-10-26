import { useEffect, useMemo, useState } from 'react';
import { useManuals } from './hooks/useManuals.js';
import ManualList from './components/ManualList.jsx';
import ManualDetail from './components/ManualDetail.jsx';
import ManualForm from './components/ManualForm.jsx';
import SearchFilters from './components/SearchFilters.jsx';

function App() {
  const {
    manuals,
    categories,
    isLoading,
    error,
    refresh,
    createManual,
    deleteManual,
    getManual
  } = useManuals();

  const [selectedManualId, setSelectedManualId] = useState(null);
  const [selectedManual, setSelectedManual] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    let ignore = false;

    const fetchManual = async () => {
      if (selectedManualId == null) {
        setSelectedManual(null);
        return;
      }

      const manual = await getManual(selectedManualId);
      if (!ignore) {
        setSelectedManual(manual);
      }
    };

    fetchManual();

    return () => {
      ignore = true;
    };
  }, [selectedManualId, getManual]);

  const filteredManuals = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();
    return manuals.filter((manual) => {
      const matchesCategory =
        selectedCategory === 'All' || manual.category.toLowerCase() === selectedCategory.toLowerCase();

      if (!normalizedSearch) {
        return matchesCategory;
      }

      const combinedText = [
        manual.title,
        manual.category,
        manual.tags.join(' ')
      ]
        .join(' ')
        .toLowerCase();

      return matchesCategory && combinedText.includes(normalizedSearch);
    });
  }, [manuals, searchTerm, selectedCategory]);

  const handleManualCreated = async (payload) => {
    const created = await createManual(payload);
    if (created) {
      setSelectedManualId(created.id);
      setSelectedManual(created);
    }
  };

  const handleDeleteManual = async (id) => {
    const removed = await deleteManual(id);
    if (removed) {
      setSelectedManualId((current) => (current === id ? null : current));
      setSelectedManual((current) => (current?.id === id ? null : current));
    }
  };

  return (
    <div className="app-shell">
      <header>
        <h1>ManualMaster</h1>
        <p>Your manuals, modernized with a .NET 8 API and React experience.</p>
      </header>

      <main>
        <aside className="sidebar">
          <SearchFilters
            searchTerm={searchTerm}
            onSearchTermChange={setSearchTerm}
            categories={[{ label: 'All', value: 'All' }, ...categories.map((c) => ({ label: c, value: c }))]}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            isLoading={isLoading}
          />

          <ManualForm
            onSubmit={handleManualCreated}
            isBusy={isLoading}
          />

          {error && <div className="status-banner error">{error}</div>}
        </aside>

        <section className="content">
          <ManualList
            manuals={filteredManuals}
            onSelectManual={setSelectedManualId}
            selectedManualId={selectedManualId}
            isLoading={isLoading}
          />

          <ManualDetail
            manual={selectedManual}
            onDelete={handleDeleteManual}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
