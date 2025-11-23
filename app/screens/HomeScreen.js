import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Platform,
} from 'react-native';
import * as Location from 'expo-location';
import * as Notifications from 'expo-notifications';
import { updateLocation, notifyNearby, registerPushToken } from '../services/api';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export default function HomeScreen({ navigation }) {
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [locationPermission, setLocationPermission] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState(false);
  const [expoPushToken, setExpoPushToken] = useState(null);
  const [userId] = useState(1); // TODO: Get from user authentication

  useEffect(() => {
    requestPermissions();
    registerForPushNotifications();
  }, []);

  useEffect(() => {
    if (locationPermission) {
      getCurrentLocation();
    }
  }, [locationPermission]);

  const requestPermissions = async () => {
    // Request location permission
    const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
    setLocationPermission(locationStatus === 'granted');

    // Request notification permission
    const { status: notificationStatus } = await Notifications.requestPermissionsAsync();
    setNotificationPermission(notificationStatus === 'granted');
  };

  const registerForPushNotifications = async () => {
    try {
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: '8f7b24c7-0d79-4b3a-bcd5-2bbf43c75160', // From app.json extra.eas.projectId
      });
      setExpoPushToken(token.data);
      console.log('Expo Push Token:', token.data);
      
      // Register the push token with the backend
      try {
        await registerPushToken(userId, token.data);
        console.log('Push token registered with backend');
      } catch (error) {
        console.error('Error registering push token with backend:', error);
      }
    } catch (error) {
      console.error('Error getting push token:', error);
    }
  };

  const getCurrentLocation = async () => {
    try {
      const currentLocation = await Location.getCurrentPositionAsync({});
      setLocation(currentLocation.coords);
      
      // Update location on server
      if (currentLocation.coords) {
        await updateLocation(
          userId,
          currentLocation.coords.latitude,
          currentLocation.coords.longitude
        );
      }
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Error', 'Failed to get your location');
    }
  };

  const handleEmergency = async () => {
    if (!location) {
      Alert.alert('Location Required', 'Please wait for location to be determined');
      return;
    }

    Alert.alert(
      'Emergency Alert',
      'Are you sure you want to send an emergency notification to nearby users?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Send Emergency',
          style: 'destructive',
          onPress: async () => {
            setLoading(true);
            try {
              const response = await notifyNearby(
                userId,
                location.latitude,
                location.longitude
              );
              
              Alert.alert(
                'Emergency Sent',
                `Notification sent to ${response.recipients} nearby user(s)`,
                [{ text: 'OK' }]
              );
            } catch (error) {
              Alert.alert(
                'Error',
                'Failed to send emergency notification. Please try again.'
              );
              console.error('Emergency error:', error);
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>TheLocalShield</Text>
        <Text style={styles.subtitle}>Emergency Response System</Text>

        {location ? (
          <View style={styles.locationInfo}>
            <Text style={styles.locationLabel}>Your Location:</Text>
            <Text style={styles.locationText}>
              {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
            </Text>
          </View>
        ) : (
          <View style={styles.locationInfo}>
            <ActivityIndicator size="small" color="#667eea" />
            <Text style={styles.locationText}>Getting your location...</Text>
          </View>
        )}

        <TouchableOpacity
          style={[styles.emergencyButton, loading && styles.emergencyButtonDisabled]}
          onPress={handleEmergency}
          disabled={loading || !location}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.emergencyButtonText}>🚨 EMERGENCY</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.mapButton}
          onPress={() => navigation.navigate('Map')}
        >
          <Text style={styles.mapButtonText}>📍 View Map</Text>
        </TouchableOpacity>

        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>
            Location: {locationPermission ? '✅' : '❌'}
          </Text>
          <Text style={styles.statusText}>
            Notifications: {notificationPermission ? '✅' : '❌'}
          </Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 40,
  },
  locationInfo: {
    marginBottom: 40,
    alignItems: 'center',
  },
  locationLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  locationText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  emergencyButton: {
    backgroundColor: '#f5576c',
    paddingVertical: 20,
    paddingHorizontal: 60,
    borderRadius: 50,
    marginBottom: 20,
    shadowColor: '#f5576c',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  emergencyButtonDisabled: {
    opacity: 0.6,
  },
  emergencyButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    letterSpacing: 2,
  },
  mapButton: {
    backgroundColor: '#667eea',
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 25,
    marginBottom: 30,
  },
  mapButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  statusContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  statusText: {
    fontSize: 14,
    color: '#666',
    marginVertical: 5,
  },
});

