"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { client, ApiError } from "@/lib/api/client";
import { User } from "@/types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);
  const router = useRouter();

  const clearError = React.useCallback(() => setError(null), []);

  const refreshSession = React.useCallback(async () => {
    try {
      // Rotation endpoint checks HTTP-only cookies and sets new cookies
      await client.post("/api/v1/auth/refresh");
      
      // Fetch fresh user profile
      const currentUser = await client.get<User>("/api/v1/auth/me");
      setUser(currentUser);
    } catch (err) {
      setUser(null);
      // Silent failure is normal if session has expired or doesn't exist
    } finally {
      setLoading(false);
    }
  }, []);

  // Check user context on mount
  React.useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  // Set up background refresh interval (every 14 minutes since token expires in 15)
  React.useEffect(() => {
    if (!user) return;

    const interval = setInterval(() => {
      client.post("/api/v1/auth/refresh").catch(() => {
        setUser(null);
        router.push("/login");
      });
    }, 14 * 60 * 1000);

    return () => clearInterval(interval);
  }, [user, router]);

  const handleLogin = async (credentials: any) => {
    setLoading(true);
    setError(null);
    try {
      await client.post("/api/v1/auth/login", credentials);
      const currentUser = await client.get<User>("/api/v1/auth/me");
      setUser(currentUser);
      router.push("/");
    } catch (err: any) {
      if (err instanceof ApiError) {
        setError(err.data.message || "Failed to authenticate.");
      } else {
        setError("An unexpected network error occurred.");
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (data: any) => {
    setLoading(true);
    setError(null);
    try {
      await client.post("/api/v1/auth/register", data);
      router.push("/login?registered=true");
    } catch (err: any) {
      if (err instanceof ApiError) {
        setError(err.data.message || "Registration failed.");
      } else {
        setError("An unexpected network error occurred.");
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await client.post("/api/v1/auth/logout");
    } catch {
      // Clean state regardless of network response
    } finally {
      setUser(null);
      setLoading(false);
      router.push("/login");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
        refreshSession,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
