import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function AutoFindScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Auto-Find Manual</Text>
      <Text>Functionality to search for a manual online will be implemented here.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
});
