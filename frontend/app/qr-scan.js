import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function QRScannerScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>QR Code Scanner</Text>
      <Text>The camera for QR code scanning will be implemented here.</Text>
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
