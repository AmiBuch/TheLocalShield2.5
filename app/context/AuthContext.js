import React, { createContext, useState, useEffect, useContext } from 'react';
import { getUser, isAuthenticated, logout as authLogout } from '../services/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const isAuth = await isAuthenticated();
      if (isAuth) {
        const userData = await getUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (userData) => {
    // userData comes from login/register response
    const userInfo = {
      user_id: userData.user_id,
      email: userData.email,
      name: userData.name,
    };
    setUser(userInfo);
  };

  const logout = async () => {
    await authLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

