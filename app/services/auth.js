/**
 * Authentication service for managing user login, registration, and token storage.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://10.139.172.87:8000';
const TOKEN_KEY = '@thelocalshield:token';
const USER_KEY = '@thelocalshield:user';

/**
 * Register a new user
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {string} name - Optional user name
 * @returns {Promise<Object>} User data and token
 */
export async function register(email, password, name = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        name,
      }),
    });

    // Get response text first to check if it's JSON
    const responseText = await response.text();
    
    if (!response.ok) {
      // Try to parse as JSON, fallback to plain text
      let errorMessage = 'Registration failed';
      try {
        const error = JSON.parse(responseText);
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        // Not JSON, use the text as error message
        errorMessage = responseText || `HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    // Parse JSON response
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      throw new Error(`Invalid response from server: ${responseText.substring(0, 100)}`);
    }
    
    // Store token and user data
    await AsyncStorage.setItem(TOKEN_KEY, data.token);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify({
      user_id: data.user_id,
      email: data.email,
      name: data.name,
    }));

    return data;
  } catch (error) {
    console.error('Registration error:', error);
    // Re-throw with more context if it's a network error
    if (error.message.includes('Network request failed') || error.message.includes('Failed to fetch')) {
      throw new Error('Cannot connect to server. Make sure the backend is running.');
    }
    throw error;
  }
}

/**
 * Login an existing user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} User data and token
 */
export async function login(email, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    // Get response text first to check if it's JSON
    const responseText = await response.text();
    
    if (!response.ok) {
      // Try to parse as JSON, fallback to plain text
      let errorMessage = 'Login failed';
      try {
        const error = JSON.parse(responseText);
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        // Not JSON, use the text as error message
        errorMessage = responseText || `HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    // Parse JSON response
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      throw new Error(`Invalid response from server: ${responseText.substring(0, 100)}`);
    }
    
    // Store token and user data
    await AsyncStorage.setItem(TOKEN_KEY, data.token);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify({
      user_id: data.user_id,
      email: data.email,
      name: data.name,
    }));

    return data;
  } catch (error) {
    console.error('Login error:', error);
    // Re-throw with more context if it's a network error
    if (error.message.includes('Network request failed') || error.message.includes('Failed to fetch')) {
      throw new Error('Cannot connect to server. Make sure the backend is running.');
    }
    throw error;
  }
}

/**
 * Logout current user
 */
export async function logout() {
  try {
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);
  } catch (error) {
    console.error('Logout error:', error);
  }
}

/**
 * Get stored authentication token
 * @returns {Promise<string|null>} JWT token or null
 */
export async function getToken() {
  try {
    return await AsyncStorage.getItem(TOKEN_KEY);
  } catch (error) {
    console.error('Error getting token:', error);
    return null;
  }
}

/**
 * Get stored user data
 * @returns {Promise<Object|null>} User data or null
 */
export async function getUser() {
  try {
    const userStr = await AsyncStorage.getItem(USER_KEY);
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  } catch (error) {
    console.error('Error getting user:', error);
    return null;
  }
}

/**
 * Check if user is authenticated
 * @returns {Promise<boolean>} True if authenticated
 */
export async function isAuthenticated() {
  const token = await getToken();
  return token !== null;
}

/**
 * Get current user info from server
 * @returns {Promise<Object>} Current user data
 */
export async function getCurrentUser() {
  try {
    const token = await getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, clear storage
        await logout();
        throw new Error('Session expired');
      }
      throw new Error('Failed to get user info');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting current user:', error);
    throw error;
  }
}

