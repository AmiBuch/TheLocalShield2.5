/**
 * Emergency polling service for POC
 * Polls the backend for new emergencies and triggers local notifications
 * Works in Expo Go since it uses local notifications
 */

import * as Notifications from 'expo-notifications';
import { getToken } from './auth';

// Use the same API URL as the main API service
const API_BASE_URL = 'http://10.139.172.87:8000';
const POLL_INTERVAL = 3000; // Poll every 3 seconds

let pollingInterval = null;
let lastCheckedTimestamp = null;

/**
 * Start polling for emergencies
 * User ID is now obtained from JWT token automatically
 */
export function startEmergencyPolling() {
  lastCheckedTimestamp = new Date().toISOString();
  
  // Poll immediately
  checkForEmergencies();
  
  // Then poll at intervals
  pollingInterval = setInterval(() => {
    checkForEmergencies();
  }, POLL_INTERVAL);
  
  console.log('Emergency polling started');
}

/**
 * Stop polling for emergencies
 */
export function stopEmergencyPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
    console.log('Emergency polling stopped');
  }
}

/**
 * Check for new emergencies and show notifications
 */
async function checkForEmergencies() {
  try {
    const token = await getToken();
    if (!token) {
      // Not authenticated, skip polling
      return;
    }

    const since = lastCheckedTimestamp || new Date(Date.now() - 60000).toISOString(); // Last minute as fallback
    
    const url = `${API_BASE_URL}/emergency/recent?since=${encodeURIComponent(since)}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Try to get error details
      let errorText = '';
      try {
        errorText = await response.text();
      } catch (e) {
        errorText = 'Could not read error response';
      }
      console.error(`HTTP error! status: ${response.status}, response: ${errorText}`);
      // Don't throw - just log and continue polling
      return;
    }

    let emergencies;
    try {
      emergencies = await response.json();
    } catch (e) {
      console.error('Error parsing JSON response:', e);
      return; // Continue polling on next interval
    }
    
    // Ensure emergencies is an array
    if (!Array.isArray(emergencies)) {
      console.warn('Response is not an array:', emergencies);
      return; // Continue polling on next interval
    }
    
    if (emergencies.length > 0) {
      // Update last checked timestamp
      lastCheckedTimestamp = new Date().toISOString();
      
      // Show notification for each new emergency
      for (const emergency of emergencies) {
        if (emergency && emergency.id) {
          await showEmergencyNotification(emergency);
        }
      }
    }
  } catch (error) {
    // Only log errors, don't stop polling
    console.error('Error checking for emergencies:', error.message || error);
  }
}

/**
 * Show a local notification for an emergency
 * @param {Object} emergency - Emergency object with user_id, latitude, longitude
 */
async function showEmergencyNotification(emergency) {
  try {
    // Safely format location coordinates
    const lat = typeof emergency.latitude === 'number' 
      ? emergency.latitude.toFixed(4) 
      : emergency.latitude || 'unknown';
    const lon = typeof emergency.longitude === 'number' 
      ? emergency.longitude.toFixed(4) 
      : emergency.longitude || 'unknown';
    
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '🚨 Emergency Alert',
        body: `User ${emergency.user_id || 'Unknown'} needs help! Location: ${lat}, ${lon}`,
        data: {
          emergency_id: emergency.id,
          user_id: emergency.user_id,
          latitude: emergency.latitude,
          longitude: emergency.longitude,
        },
        sound: true,
        priority: Notifications.AndroidNotificationPriority.HIGH,
      },
      trigger: null, // Show immediately
    });
    
    console.log('Emergency notification shown:', emergency.id);
  } catch (error) {
    console.error('Error showing notification:', error);
    // Don't throw - just log the error and continue
  }
}

