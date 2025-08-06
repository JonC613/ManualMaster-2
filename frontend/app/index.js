import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import axios from 'axios';

// --- Configuration ---
// For development, replace with your computer's local IP address.
// The backend Flask server must be running.
const API_URL = 'http://192.168.1.100:5000/api'; // <--- IMPORTANT: Replace with your IP

const api = axios.create({
  baseURL: API_URL,
});

export default function BrowseScreen() {
  const [manuals, setManuals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchManuals();
  }, []);

  const fetchManuals = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/manuals');
      setManuals(response.data);
    } catch (err) {
      setError('Failed to fetch manuals. Make sure the backend server is running and the IP address is correct.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.itemContainer}>
      <Text style={styles.itemTitle}>{item.title}</Text>
      <Text style={styles.itemCategory}>{item.category}</Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text>Loading manuals...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={manuals}
        renderItem={renderItem}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={<Text>No manuals found.</Text>}
        contentContainerStyle={{ padding: 16 }}
        onRefresh={fetchManuals}
        refreshing={loading}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
  },
  itemContainer: {
    backgroundColor: '#fff',
    padding: 16,
    marginBottom: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  itemTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  itemCategory: {
    fontSize: 14,
    color: 'gray',
    marginTop: 4,
  },
});
