import React, { useState, useEffect } from 'react';
import { Text, View, StyleSheet, Button, Alert } from 'react-native';
import { Camera } from 'expo-camera';
import { BarCodeScanner } from 'expo-barcode-scanner';
import { useRouter } from 'expo-router';

export default function QRScannerScreen() {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const getCameraPermissions = async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    };

    getCameraPermissions();
  }, []);

  const handleBarCodeScanned = ({ type, data }) => {
    setScanned(true);
    Alert.alert(
      'QR Code Scanned!',
      `Data: ${data}`,
      [
        {
          text: 'Add as New Manual',
          onPress: () => router.push({ pathname: '/add', params: { scannedData: data } }),
        },
        {
          text: 'Scan Again',
          onPress: () => setScanned(false),
          style: 'cancel',
        },
      ],
      { cancelable: false }
    );
  };

  if (hasPermission === null) {
    return <Text>Requesting for camera permission...</Text>;
  }
  if (hasPermission === false) {
    return <Text>No access to camera. Please enable it in your device settings.</Text>;
  }

  return (
    <View style={styles.container}>
      <Camera
        onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
        style={StyleSheet.absoluteFillObject}
        barCodeScannerSettings={{
          barCodeTypes: [BarCodeScanner.Constants.BarCodeType.qr],
        }}
      />
      <View style={styles.overlay}>
        <Text style={styles.title}>Scan a QR Code</Text>
        <View style={styles.qrFrame} />
        <Text style={styles.instructions}>Point your camera at a QR code to scan it.</Text>
      </View>
      {scanned && <Button title={'Tap to Scan Again'} onPress={() => setScanned(false)} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'column',
    justifyContent: 'center',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 20,
  },
  qrFrame: {
    width: 250,
    height: 250,
    borderWidth: 2,
    borderColor: 'white',
    borderRadius: 10,
  },
  instructions: {
    fontSize: 16,
    color: 'white',
    marginTop: 20,
    textAlign: 'center',
    paddingHorizontal: 30,
  },
});
