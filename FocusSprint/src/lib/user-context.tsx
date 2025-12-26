"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Added missing interfaces
interface InventoryItem {
  id: string;
  name: string;
  cost: number;
  metadata?: Record<string, any>;
  purchasedAt?: number;
}

interface SprintData {
  id: string;
  durationSeconds: number;
  completedAt: number;
  coinsEarned?: number;
}

interface UserProgress {
  currentSprintId?: string;
  secondsFocusedToday?: number;
  totalFocusedSeconds?: number;
}

// Add UserProfile interface
interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  // Add other fields from your backend User schema if needed
}

interface UserState {
  user: UserProfile | null;
  focusCoins: number;
  streak: number;
  inventory: InventoryItem[];
  completedSprints: SprintData[];
  currentProgress: UserProgress | null;
  isLoaded: boolean;
  addCoins: (amount: number) => void;
  spendCoins: (amount: number) => boolean;
  purchaseItem: (item: Omit<InventoryItem, "purchasedAt">) => boolean;
  completeSprint: (sprint: SprintData) => void;
  setProgress: (progress: UserProgress) => void;
  incrementStreak: () => void;
  resetStreak: () => void;
  syncWithBackend: () => Promise<void>; // New function
  logout: () => void; // <-- added
}

const UserContext = createContext<UserState | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [focusCoins, setFocusCoins] = useState(500);
  const [streak, setStreak] = useState(0);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [completedSprints, setCompletedSprints] = useState<SprintData[]>([]);
  const [currentProgress, setCurrentProgress] = useState<UserProgress | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Sync data from Backend
  const syncWithBackend = async () => {
    const token = localStorage.getItem("focus_token");
    if (!token) return;

    try {
      // 1. Fetch User Profile
      const res = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        // If your backend tracks coins/streak, update state here:
        // setFocusCoins(userData.coins);
        // setStreak(userData.streak);
      }

      // 2. Fetch Progress/Analytics (Optional, if you add this endpoint)
      // const progressRes = await fetch(`${API_URL}/analytics/progress`, ...);
    } catch (e) {
      console.error("Sync failed", e);
    }
  };

  useEffect(() => {
    // Initial Load from LocalStorage
    const saved = localStorage.getItem("focusflow_user");
    if (saved) {
      try {
        const data = JSON.parse(saved);
        if (data.focusCoins !== undefined) setFocusCoins(data.focusCoins);
        if (data.streak !== undefined) setStreak(data.streak);
        if (data.inventory) setInventory(data.inventory);
        if (data.completedSprints) setCompletedSprints(data.completedSprints);
        if (data.currentProgress) setCurrentProgress(data.currentProgress);
      } catch (e) {
        console.error("Failed to parse local user data", e);
      }
    }
    
    // Then try to sync with backend
    syncWithBackend().finally(() => setIsLoaded(true));
  }, []);

  useEffect(() => {
    if (isLoaded) {
      const existing = localStorage.getItem("focusflow_user");
      const baseData = existing ? JSON.parse(existing) : {};
      
      localStorage.setItem(
        "focusflow_user",
        JSON.stringify({
          ...baseData,
          focusCoins,
          streak,
          inventory,
          completedSprints,
          currentProgress,
        })
      );
    }
  }, [focusCoins, streak, inventory, completedSprints, currentProgress, isLoaded]);

  const addCoins = (amount: number) => {
    setFocusCoins((prev) => prev + amount);
  };

  const spendCoins = (amount: number): boolean => {
    if (focusCoins >= amount) {
      setFocusCoins((prev) => prev - amount);
      return true;
    }
    return false;
  };

  const purchaseItem = (item: Omit<InventoryItem, "purchasedAt">): boolean => {
    setInventory((prev) => [...prev, { ...item, purchasedAt: Date.now() }]);
    return true;
  };

  const completeSprint = (sprint: SprintData) => {
    setCompletedSprints((prev) => [...prev, sprint]);
  };

  const setProgress = (progress: UserProgress) => {
    setCurrentProgress(progress);
  };

  const incrementStreak = () => {
    setStreak((prev) => prev + 1);
  };

  const resetStreak = () => {
    setStreak(0);
  };

  // logout implementation
  const logout = () => {
    // clear auth & saved user data and reset local state
    try {
      localStorage.removeItem("focus_token");
      localStorage.removeItem("focusflow_user");
    } catch {}
    setUser(null);
    setFocusCoins(500);
    setStreak(0);
    setInventory([]);
    setCompletedSprints([]);
    setCurrentProgress(null);
    setIsLoaded(true);
  };

  return (
    <UserContext.Provider
      value={{
        user,
        focusCoins,
        streak,
        inventory,
        completedSprints,
        currentProgress,
        isLoaded,
        addCoins,
        spendCoins,
        purchaseItem,
        completeSprint,
        setProgress,
        incrementStreak,
        resetStreak,
        syncWithBackend,
        logout, // <-- exposed
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}