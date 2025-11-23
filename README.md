# TheLocalShield Mobile App

React Native mobile application for TheLocalShield emergency response system.

## Features

- 🚨 Emergency button to notify nearby users
- 📍 Real-time location tracking
- 🗺️ Map view showing all user locations
- 🔔 Push notifications for emergency alerts

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (for Mac) or Android Emulator

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the Expo development server:
```bash
npm start
```

3. Run on your device:
   - Scan the QR code with Expo Go app (iOS/Android)
   - Or press `i` for iOS simulator / `a` for Android emulator

## Project Structure

```
/app
  /screens
    HomeScreen.js      # Main screen with emergency button
    MapScreen.js       # Map showing all user locations
  /components          # Reusable components
  /services
    api.js            # API service for backend communication
```

## Configuration

### API Base URL

Update the `API_BASE_URL` in `app/services/api.js` to match your backend server:

```javascript
const API_BASE_URL = 'http://your-server-ip:8000';
```

For physical devices, use your computer's local IP address instead of `localhost`.

### Expo Push Notifications

Update the `projectId` in `app/screens/HomeScreen.js`:

```javascript
const token = await Notifications.getExpoPushTokenAsync({
  projectId: 'your-project-id', // Get from Expo dashboard
});
```

## Available Scripts

- `npm start` - Start Expo development server
- `npm run android` - Run on Android emulator
- `npm run ios` - Run on iOS simulator
- `npm run web` - Run in web browser

## Permissions

The app requires the following permissions:
- Location (foreground)
- Notifications

These are requested automatically when the app starts.

## Backend Connection

Make sure your FastAPI backend is running on `http://localhost:8000` (or update the API_BASE_URL).

## Development

- The app uses React Navigation for screen navigation
- Location tracking uses `expo-location`
- Push notifications use `expo-notifications`
- Maps use `react-native-maps`

