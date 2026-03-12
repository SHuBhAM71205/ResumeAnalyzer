import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  AUTH_EVENT,
  clearAuth,
  getStoredUser,
  getToken,
  setAuth as persistAuth,
  type AuthUser,
} from "../lib/auth";

type AuthContextValue = {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
  updateUser: (user: AuthUser) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isHydrated, setHydrated] = useState(false);

  useEffect(() => {
    const hydrate = () => {
      setTokenState(getToken());
      setUser(getStoredUser());
    };

    hydrate();
    setHydrated(true);

    window.addEventListener(AUTH_EVENT, hydrate);
    window.addEventListener("storage", hydrate);

    return () => {
      window.removeEventListener(AUTH_EVENT, hydrate);
      window.removeEventListener("storage", hydrate);
    };
  }, []);

  const login = (nextToken: string, nextUser: AuthUser) => {
    persistAuth(nextToken, nextUser);
    setTokenState(nextToken);
    setUser(nextUser);
  };

  const logout = () => {
    clearAuth();
    setTokenState(null);
    setUser(null);
  };

  const updateUser = (nextUser: AuthUser) => {
    if (token) {
      persistAuth(token, nextUser);
    }
    setUser(nextUser);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated: Boolean(token && user),
        isHydrated,
        login,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
