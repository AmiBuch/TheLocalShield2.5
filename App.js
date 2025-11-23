import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { AuthProvider, useAuth } from './app/context/AuthContext';
import HomeScreen from './app/screens/HomeScreen';
import MapScreen from './app/screens/MapScreen';
import LoginScreen from './app/screens/LoginScreen';

const Stack = createNativeStackNavigator();

function AppNavigator() {
  const { user, login, loading } = useAuth();

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#667eea" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#667eea',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {user ? (
          // User is logged in - show main app
          <>
            <Stack.Screen 
              name="Home" 
              component={HomeScreen}
              options={{ title: 'TheLocalShield' }}
            />
            <Stack.Screen 
              name="Map" 
              component={MapScreen}
              options={{ title: 'User Locations' }}
            />
          </>
        ) : (
          // User is not logged in - show login screen
          <Stack.Screen 
            name="Login" 
            options={{ headerShown: false }}
          >
            {(props) => <LoginScreen {...props} onLogin={login} />}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
});

