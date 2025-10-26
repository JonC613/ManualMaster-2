import { useCallback, useMemo, useRef, useState } from 'react';
import { api } from '../api/client.js';

const toSummary = (manual) => ({
  id: manual.id,
  title: manual.title,
  category: manual.category,
  tags: manual.tags,
  uploadDate: manual.uploadDate,
  size: manual.size
});

export function useManuals() {
  const [manuals, setManuals] = useState([]);
  const [manualDetails, setManualDetails] = useState({});
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const manualDetailsRef = useRef({});

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [manualResponse, categoryResponse] = await Promise.all([
        api.get('/manuals'),
        api.get('/manuals/categories')
      ]);

      setManuals(manualResponse.data);
      setCategories(categoryResponse.data);
    } catch (err) {
      setError('Failed to load manuals.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getManual = useCallback(async (id) => {
    if (manualDetailsRef.current[id]) {
      return manualDetailsRef.current[id];
    }

    try {
      const response = await api.get(`/manuals/${id}`);
      const manual = response.data;
      manualDetailsRef.current = { ...manualDetailsRef.current, [id]: manual };
      setManualDetails(manualDetailsRef.current);
      return manual;
    } catch (err) {
      setError('Failed to load manual details.');
      return null;
    }
  }, []);

  const createManual = useCallback(async (payload) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/manuals', payload);
      const manual = response.data;
      manualDetailsRef.current = { ...manualDetailsRef.current, [manual.id]: manual };
      setManualDetails(manualDetailsRef.current);
      setManuals((current) => [toSummary(manual), ...current]);
      return manual;
    } catch (err) {
      setError('Failed to create manual.');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteManual = useCallback(async (id) => {
    setIsLoading(true);
    setError(null);

    try {
      await api.delete(`/manuals/${id}`);
      setManuals((current) => current.filter((manual) => manual.id !== id));
      manualDetailsRef.current = { ...manualDetailsRef.current };
      delete manualDetailsRef.current[id];
      setManualDetails(manualDetailsRef.current);
      return true;
    } catch (err) {
      setError('Failed to delete manual.');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = useMemo(() => ({
    manuals,
    categories,
    isLoading,
    error,
    refresh,
    createManual,
    deleteManual,
    getManual
  }), [manuals, categories, isLoading, error, refresh, createManual, deleteManual, getManual]);

  return value;
}
