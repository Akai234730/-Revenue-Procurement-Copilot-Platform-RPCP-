import { createContext, useContext, useEffect, useMemo, useState } from 'react';

import { clearAccessToken, fetcher, getAccessToken, poster, setAccessToken } from '../lib/api';

type AuthUser = {
  id: string;
  username: string;
  name?: string;
  display_name?: string;
  roles: string[];
  email?: string;
};

type AuthContextValue = {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<AuthUser>;
  logout: () => void;
  bootstraping: boolean;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [bootstraping, setBootstraping] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      const token = getAccessToken();
      if (!token) {
        setBootstraping(false);
        return;
      }
      try {
        const me = await fetcher<AuthUser>('/auth/me');
        setUser(me);
      } catch {
        clearAccessToken();
        setUser(null);
      } finally {
        setBootstraping(false);
      }
    };
    void bootstrap();
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      bootstraping,
      login: async (username: string, password: string) => {
        const result = await poster<{ accessToken: string; user: AuthUser }>('/auth/login', {
          username,
          password,
        });
        setAccessToken(result.accessToken);
        setUser(result.user);
        return result.user;
      },
      logout: () => {
        clearAccessToken();
        setUser(null);
      },
    }),
    [bootstraping, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth 必须在 AuthProvider 内部使用');
  }
  return context;
}
