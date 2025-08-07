import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, TextInput, Button } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { getManuals, seedStorage } from './utils/storage';

export default function BrowseScreen() {
  const [manuals, setManuals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Load manuals whenever the screen is focused
  useFocusEffect(
    useCallback(() => {
      loadManuals();
    }, [])
  );

  useEffect(() => {
    // On first mount, check if storage is empty and seed if necessary
    const initialize = async () => {
      const existingManuals = await getManuals();
      if (existingManuals.length === 0) {
        await seedStorage();
      }
      loadManuals();
    };
    initialize();
  }, []);

  const loadManuals = async () => {
    setLoading(true);
    const storedManuals = await getManuals(searchQuery);
    setManuals(storedManuals);
    setLoading(false);
  };

  const handleSearch = () => {
    loadManuals();
  };

  const renderItem = ({ item }) => (
    <View style={styles.itemContainer}>
      <Text style={styles.itemTitle}>{item.title}</Text>
      <Text style={styles.itemCategory}>{item.category}</Text>
      <Text style={styles.itemContent} numberOfLines={2}>{item.content}</Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search manuals..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={handleSearch}
        />
        <Button title="Search" onPress={handleSearch} color="#4CAF50" />
      </View>
      <FlatList
        data={manuals}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={<Text style={styles.emptyText}>No manuals found.</Text>}
        contentContainerStyle={{ padding: 16 }}
        onRefresh={loadManuals}
        refreshing={loading}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderColor: '#ddd',
  },
  searchInput: {
    flex: 1,
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginRight: 10,
  },
  itemContainer: {
    backgroundColor: '#fff',
    padding: 16,
    marginBottom: 10,
    borderRadius: 8,
    elevation: 2,
  },
  itemTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  itemCategory: {
    fontSize: 14,
    color: 'gray',
    marginTop: 4,
    marginBottom: 8,
  },
  itemContent: {
    fontSize: 14,
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
    color: 'gray',
  },
});
