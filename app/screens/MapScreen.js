import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ActivityIndicator,
  Text,
  TouchableOpacity,
  Alert,
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { getAllLocations } from '../services/api';

export default function MapScreen({ navigation }) {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [region, setRegion] = useState({
    latitude: 40.7128,
    longitude: -74.0060,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });

  useEffect(() => {
    loadLocations();
    // Refresh locations every 5 seconds
    const interval = setInterval(loadLocations, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadLocations = async () => {
    try {
      setLoading(true);
      const data = await getAllLocations();
      setLocations(data);
      
      // Update map region to show all locations if we have any
      if (data.length > 0) {
        const firstLocation = data[0];
        setRegion({
          latitude: parseFloat(firstLocation.latitude),
          longitude: parseFloat(firstLocation.longitude),
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        });
      }
    } catch (error) {
      console.error('Error loading locations:', error);
      Alert.alert(
        'Error',
        'Failed to load user locations. Please check your connection.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {loading && locations.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#667eea" />
          <Text style={styles.loadingText}>Loading locations...</Text>
        </View>
      ) : (
        <>
          <MapView
            style={styles.map}
            region={region}
            onRegionChangeComplete={setRegion}
            showsUserLocation={true}
            showsMyLocationButton={true}
          >
            {locations.map((location, index) => (
              <Marker
                key={index}
                coordinate={{
                  latitude: parseFloat(location.latitude),
                  longitude: parseFloat(location.longitude),
                }}
                title={`User ${location.user_id}`}
                description={`Last updated: ${new Date(location.last_updated).toLocaleString()}`}
                pinColor="#667eea"
              />
            ))}
          </MapView>
          
          <View style={styles.infoContainer}>
            <Text style={styles.infoText}>
              {locations.length} user{locations.length !== 1 ? 's' : ''} on map
            </Text>
            <TouchableOpacity
              style={styles.refreshButton}
              onPress={loadLocations}
            >
              <Text style={styles.refreshButtonText}>🔄 Refresh</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  infoContainer: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    padding: 15,
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  infoText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  refreshButton: {
    backgroundColor: '#667eea',
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 20,
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});

