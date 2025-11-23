import { NativeModules } from 'react-native';

const { AndroidPushNotifications } = NativeModules;

export default {
  /**
   * Get the FCM token for push notifications
   * @returns {Promise<string>} FCM token
   */
  async getToken() {
    if (!AndroidPushNotifications) {
      throw new Error('AndroidPushNotifications native module is not available');
    }
    return await AndroidPushNotifications.getToken();
  },

  /**
   * Check if push notifications are available
   * @returns {Promise<boolean>} True if available
   */
  async isAvailable() {
    if (!AndroidPushNotifications) {
      return false;
    }
    return await AndroidPushNotifications.isAvailable();
  },

  /**
   * Request notification permissions
   * @returns {Promise<boolean>} True if granted
   */
  async requestPermissions() {
    if (!AndroidPushNotifications) {
      return false;
    }
    return await AndroidPushNotifications.requestPermissions();
  },
};

