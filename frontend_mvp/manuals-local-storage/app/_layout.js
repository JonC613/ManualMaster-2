import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function AppLayout() {
  return (
    <Tabs
      screenOptions={{
        headerStyle: {
          backgroundColor: '#4CAF50', // A green theme for local/eco-friendly vibe
        },
        headerTintColor: '#fff',
        tabBarActiveTintColor: '#4CAF50',
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Browse',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="list" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="add"
        options={{
          title: 'Add Manual',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="add-circle" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="qr-scan"
        options={{
          title: 'QR Scan',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="qr-code" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
