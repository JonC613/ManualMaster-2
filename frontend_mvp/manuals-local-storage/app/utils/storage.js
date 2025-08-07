import AsyncStorage from '@react-native-async-storage/async-storage';
import 'react-native-get-random-values'; // Needed for uuid
import { v4 as uuidv4 } from 'uuid';

const MANUALS_STORAGE_KEY = '@manuals_storage_key';

// --- Helper Functions ---
const getStoredManuals = async () => {
  try {
    const jsonValue = await AsyncStorage.getItem(MANUALS_STORAGE_KEY);
    return jsonValue != null ? JSON.parse(jsonValue) : [];
  } catch (e) {
    console.error("Failed to fetch manuals from storage", e);
    return [];
  }
};

const setStoredManuals = async (manuals) => {
  try {
    const jsonValue = JSON.stringify(manuals);
    await AsyncStorage.setItem(MANUALS_STORAGE_KEY, jsonValue);
  } catch (e) {
    console.error("Failed to save manuals to storage", e);
  }
};

// --- Public API ---

/**
 * Get all manuals, optionally filtering by query and category.
 * @param {string} query - The search query.
 * @param {string} category - The category to filter by.
 * @returns {Promise<Array>} A promise that resolves to an array of manuals.
 */
export const getManuals = async (query = '', category = 'All') => {
  let manuals = await getStoredManuals();

  if (category !== 'All') {
    manuals = manuals.filter(manual => manual.category === category);
  }

  if (query) {
    const lowercasedQuery = query.toLowerCase();
    manuals = manuals.filter(manual =>
      manual.title.toLowerCase().includes(lowercasedQuery) ||
      manual.content.toLowerCase().includes(lowercasedQuery) ||
      (manual.tags && manual.tags.some(tag => tag.toLowerCase().includes(lowercasedQuery)))
    );
  }

  return manuals;
};

/**
 * Get a single manual by its ID.
 * @param {string} id - The ID of the manual.
 * @returns {Promise<Object|null>} A promise that resolves to the manual object or null if not found.
 */
export const getManualById = async (id) => {
  const manuals = await getStoredManuals();
  return manuals.find(manual => manual.id === id) || null;
};

/**
 * Save a manual. If the manual has an ID, it will be updated. Otherwise, it will be added.
 * @param {Object} manualData - The manual data to save.
 * @returns {Promise<Object>} A promise that resolves to the saved manual object.
 */
export const saveManual = async (manualData) => {
  const manuals = await getStoredManuals();

  if (manualData.id) {
    // Update existing manual
    const index = manuals.findIndex(m => m.id === manualData.id);
    if (index !== -1) {
      manuals[index] = { ...manuals[index], ...manualData };
    }
  } else {
    // Add new manual
    const newManual = {
      ...manualData,
      id: uuidv4(), // Assign a unique ID
      upload_date: new Date().toISOString(),
    };
    manuals.push(newManual);
  }

  await setStoredManuals(manuals);
  return manualData.id ? manualData : manuals[manuals.length - 1];
};

/**
 * Delete a manual by its ID.
 * @param {string} id - The ID of the manual to delete.
 * @returns {Promise<void>}
 */
export const deleteManual = async (id) => {
  let manuals = await getStoredManuals();
  manuals = manuals.filter(manual => manual.id !== id);
  await setStoredManuals(manuals);
};

/**
 * For development: Seed the storage with some initial data.
 */
export const seedStorage = async () => {
  const initialData = [
    {
      id: uuidv4(),
      title: 'Sample Appliance Manual',
      category: 'Appliance',
      tags: ['sample', 'kitchen'],
      content: 'This is the content for the sample appliance manual. It includes instructions on setup and use.',
      upload_date: new Date().toISOString(),
    },
    {
      id: uuidv4(),
      title: 'Tech Gadget Guide',
      category: 'Tech',
      tags: ['gadget', 'tech'],
      content: 'User guide for the new tech gadget. Contains troubleshooting tips.',
      upload_date: new Date().toISOString(),
    },
  ];
  await setStoredManuals(initialData);
};
