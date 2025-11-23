/**
 * API service for communicating with TheLocalShield backend
 */

const API_BASE_URL = 'http://10.139.172.87:8000';

/**
 * Update user location
 * @param {number} userId - User ID
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {Promise<Object>} Response from server
 */
export async function updateLocation(userId, latitude, longitude) {
  try {
    const response = await fetch(`${API_BASE_URL}/location/update`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        latitude: latitude,
        longitude: longitude,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating location:', error);
    throw error;
  }
}

/**
 * Get all user locations
 * @returns {Promise<Array>} Array of location objects
 */
export async function getAllLocations() {
  try {
    const response = await fetch(`${API_BASE_URL}/location/all`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching locations:', error);
    throw error;
  }
}

/**
 * Send emergency notification to nearby users
 * @param {number} userId - User ID
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {Promise<Object>} Response from server
 */
export async function notifyNearby(userId, latitude, longitude) {
  try {
    const response = await fetch(`${API_BASE_URL}/emergency/notify_nearby`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        latitude: latitude,
        longitude: longitude,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending emergency notification:', error);
    throw error;
  }
}

/**
 * Register or update a user's Expo push token
 * @param {number} userId - User ID
 * @param {string} expoPushToken - Expo push notification token
 * @param {string} name - Optional user name
 * @returns {Promise<Object>} Response from server
 */
export async function registerPushToken(userId, expoPushToken, name = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/location/register_token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        expo_push_token: expoPushToken,
        name: name,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error registering push token:', error);
    throw error;
  }
}

