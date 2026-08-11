import { create } from "zustand";
import { api } from "../services/api";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: "admin" | "company" | "employee" | "vendor.company" | "vendor.employee";
  company_id?: number | null;
  vendor_company_id?: number | null;
  company_name?: string | null;
  vendor_company_name?: string | null;
  phone?: string | null;
  designation?: string | null;
  department?: string | null;
  status: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
}

let fetchPromise: Promise<void> | null = null;

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  isInitialized: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.post("/auth/login", { email, password });
      
      // Fetch user profile after HttpOnly cookie is set by backend
      const userRes = await api.get("/auth/me");
      set({ user: userRes.data, isAuthenticated: true, isLoading: false, isInitialized: true });
    } catch (err: any) {
      const message = err.response?.data?.detail || "Login failed. Please check your credentials.";
      set({ error: message, isLoading: false, isAuthenticated: false, isInitialized: true, user: null });
      throw new Error(message);
    }
  },

  logout: async () => {
    try {
      await api.post("/auth/logout");
    } catch (err) {}
    set({ user: null, isAuthenticated: false, isInitialized: true, isLoading: false, error: null });
  },

  fetchCurrentUser: async () => {
    // If session is already initialized or a request is currently in flight, return immediately
    if (get().isInitialized) return;
    if (fetchPromise) return fetchPromise;

    set({ isLoading: true });

    fetchPromise = (async () => {
      try {
        const res = await api.get("/auth/me");
        set({ user: res.data, isAuthenticated: true, isLoading: false, isInitialized: true });
      } catch (err) {
        set({ user: null, isAuthenticated: false, isLoading: false, isInitialized: true });
      } finally {
        fetchPromise = null;
      }
    })();

    return fetchPromise;
  },
}));
