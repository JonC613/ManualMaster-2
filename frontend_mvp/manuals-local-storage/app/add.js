import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView, Alert } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { saveManual } from './utils/storage';

export default function AddManualScreen() {
  const params = useLocalSearchParams();
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [content, setContent] = useState(params.scannedData || '');
  const router = useRouter();

  const handleSave = async () => {
    if (!title.trim() || !content.trim()) {
      Alert.alert('Error', 'Title and Content are required.');
      return;
    }

    const manualData = {
      title,
      category,
      tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
      content,
    };

    await saveManual(manualData);

    // Navigate back to the browse screen
    router.back();
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.label}>Title</Text>
      <TextInput
        style={styles.input}
        value={title}
        onChangeText={setTitle}
        placeholder="e.g., Coffee Maker Instructions"
      />

      <Text style={styles.label}>Category</Text>
      <TextInput
        style={styles.input}
        value={category}
        onChangeText={setCategory}
        placeholder="e.g., Appliance"
      />

      <Text style={styles.label}>Tags (comma-separated)</Text>
      <TextInput
        style={styles.input}
        value={tags}
        onChangeText={setTags}
        placeholder="e.g., kitchen, setup, cleaning"
      />

      <Text style={styles.label}>Content</Text>
      <TextInput
        style={[styles.input, styles.multilineInput]}
        value={content}
        onChangeText={setContent}
        placeholder="Enter the manual's text content here..."
        multiline
      />

      <Button title="Save Manual" onPress={handleSave} color="#4CAF50" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#fff',
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  input: {
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 16,
  },
  multilineInput: {
    height: 150,
    textAlignVertical: 'top',
    paddingTop: 10,
  },
});
