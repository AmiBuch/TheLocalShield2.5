/**
 * Push notification service using custom native Android module
 * Falls back to expo-notifications if native module is not available
 */

import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';

let AndroidPushNotifications = null;

// Try to import the native module
try {
  AndroidPushNotifications = require('../../modules/android-push-notifications').default;
} catch (error) {
  console.log('Native Android push notifications module not available, using Expo fallback');
}

/**
 * Get push notification token
 * Uses native Android module if available, otherwise falls back to Expo
 */
export async function getPushToken() {
  if (Platform.OS === 'android' && AndroidPushNotifications) {
    try {
      const isAvailable = await AndroidPushNotifications.isAvailable();
      if (isAvailable) {
        const token = await AndroidPushNotifications.getToken();
        return token;
      }
    } catch (error) {
      console.warn('Native push notifications failed, falling back to Expo:', error);
    }
  }

  // Fallback to Expo notifications
  try {
    const token = await Notifications.getExpoPushTokenAsync();
    return token.data;
  } catch (error) {
    console.error('Failed to get push token:', error);
    throw error;
  }
}

/**
 * Request notification permissions
 */
export async function requestPushPermissions() {
  if (Platform.OS === 'android' && AndroidPushNotifications) {
    try {
      return await AndroidPushNotifications.requestPermissions();
    } catch (error) {
      console.warn('Native permission request failed, using Expo:', error);
    }
  }

  // Fallback to Expo
  const { status } = await Notifications.requestPermissionsAsync();
  return status === 'granted';
}

