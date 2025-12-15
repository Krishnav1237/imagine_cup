"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface SprintData {
  id: string;
  contentTitle: string;
  sprintNumber: number;
  totalSprints: number;
  duration: number;
  completed: boolean;
  infographic: string;
  summary: string;
  concept: string;
  timestamp: number;
}

export interface InventoryItem {
  id: string;
  name: string;
  type: "avatar" | "pet" | "card" | "badge";
  rarity: "Common" | "Rare" | "Epic" | "Legendary";
  imageUrl: string;
  purchasedAt: number;
}

export interface UserProgress {
  currentContentId: string | null;
  currentSprintIndex: number;
  sprints: SprintData[];
  totalSprints: number;
  contentTitle: string;
  contentType: "youtube" | "pdf" | "ppt";
  contentUrl: string;
}

interface UserState {
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
}

const UserContext = createContext<UserState | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [focusCoins, setFocusCoins] = useState(500);
  const [streak, setStreak] = useState(0);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [completedSprints, setCompletedSprints] = useState<SprintData[]>([]);
  const [currentProgress, setCurrentProgress] = useState<UserProgress | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("focussprint_user");
    if (saved) {
      const data = JSON.parse(saved);
      setFocusCoins(data.focusCoins || 500);
      setStreak(data.streak || 0);
      setInventory(data.inventory || []);
      setCompletedSprints(data.completedSprints || []);
      setCurrentProgress(data.currentProgress || null);
    }
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "focussprint_user",
      JSON.stringify({
        focusCoins,
        streak,
        inventory,
        completedSprints,
        currentProgress,
      })
    );
  }, [focusCoins, streak, inventory, completedSprints, currentProgress]);

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
    setInventory((prev) => [
      ...prev,
      { ...item, purchasedAt: Date.now() },
    ]);
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

  return (
    <UserContext.Provider
      value={{
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