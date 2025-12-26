"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { 
  loadPreferences, 
  UserPreferences, 
  getThemeVariant,
  AgeGroup 
} from "@/lib/user-preferences";

interface ThemeContextValue {
  theme: string;
  ageGroup: AgeGroup;
  preferences: UserPreferences;
  reloadPreferences: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

// CSS variables for each theme variant
const THEME_VARIABLES: Record<string, Record<string, string>> = {
  vibrant: {
    "--primary": "#ff6b4a",
    "--primary-hover": "#ff8a70",
    "--secondary": "#7c3aed",
    "--accent": "#f59e0b",
    "--background": "#0a0a12",
    "--surface": "#13131f",
    "--border": "#2a2a3e",
    "--text-primary": "#ffffff",
    "--text-secondary": "#8888a0",
    "--success": "#10b981",
    "--warning": "#f59e0b",
    "--error": "#ef4444",
  },
  modern: {
    "--primary": "#ff6b4a",
    "--primary-hover": "#ff8a70",
    "--secondary": "#06b6d4",
    "--accent": "#8b5cf6",
    "--background": "#0a0a12",
    "--surface": "#13131f",
    "--border": "#2a2a3e",
    "--text-primary": "#ffffff",
    "--text-secondary": "#8888a0",
    "--success": "#10b981",
    "--warning": "#f59e0b",
    "--error": "#ef4444",
  },
  minimal: {
    "--primary": "#3b82f6",
    "--primary-hover": "#60a5fa",
    "--secondary": "#64748b",
    "--accent": "#0ea5e9",
    "--background": "#0f172a",
    "--surface": "#1e293b",
    "--border": "#334155",
    "--text-primary": "#f8fafc",
    "--text-secondary": "#94a3b8",
    "--success": "#22c55e",
    "--warning": "#eab308",
    "--error": "#ef4444",
  },
  accessible: {
    "--primary": "#2563eb",
    "--primary-hover": "#3b82f6",
    "--secondary": "#7c3aed",
    "--accent": "#059669",
    "--background": "#000000",
    "--surface": "#1a1a1a",
    "--border": "#404040",
    "--text-primary": "#ffffff",
    "--text-secondary": "#d4d4d4",
    "--success": "#22c55e",
    "--warning": "#fbbf24",
    "--error": "#f87171",
  },
  "high-contrast": {
    "--primary": "#ffffff",
    "--primary-hover": "#e5e5e5",
    "--secondary": "#ffff00",
    "--accent": "#00ffff",
    "--background": "#000000",
    "--surface": "#0a0a0a",
    "--border": "#ffffff",
    "--text-primary": "#ffffff",
    "--text-secondary": "#ffffff",
    "--success": "#00ff00",
    "--warning": "#ffff00",
    "--error": "#ff0000",
  },
};

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] = useState<UserPreferences>(() => loadPreferences());
  const [theme, setTheme] = useState<string>("modern");
  
  const reloadPreferences = () => {
    const prefs = loadPreferences();
    setPreferences(prefs);
    const newTheme = getThemeVariant(prefs);
    setTheme(newTheme);
    applyTheme(newTheme, prefs);
  };
  
  const applyTheme = (themeName: string, prefs: UserPreferences) => {
    const root = document.documentElement;
    const variables = THEME_VARIABLES[themeName] || THEME_VARIABLES.modern;
    
    // Apply CSS variables
    Object.entries(variables).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
    
    // Apply accessibility settings
    if (prefs.largeTextMode) {
      root.style.setProperty("--font-size-base", "18px");
      root.classList.add("large-text");
    } else {
      root.style.setProperty("--font-size-base", "16px");
      root.classList.remove("large-text");
    }
    
    if (prefs.reducedMotion) {
      root.classList.add("reduce-motion");
    } else {
      root.classList.remove("reduce-motion");
    }
  };
  
  useEffect(() => {
    reloadPreferences();
    
    // Listen for preference changes
    const handleStorage = (e: StorageEvent) => {
      if (e.key === "focus_user_preferences") {
        reloadPreferences();
      }
    };
    
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);
  
  return (
    <ThemeContext.Provider 
      value={{ 
        theme, 
        ageGroup: preferences.ageGroup, 
        preferences,
        reloadPreferences 
      }}
    >
      <style jsx global>{`
        .large-text {
          font-size: 18px;
        }
        .large-text h1 { font-size: 2.5rem; }
        .large-text h2 { font-size: 2rem; }
        .large-text h3 { font-size: 1.5rem; }
        .large-text p, .large-text span, .large-text li { font-size: 1.125rem; }
        
        .reduce-motion *,
        .reduce-motion *::before,
        .reduce-motion *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
        }
      `}</style>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    // Return defaults if not in provider
    return {
      theme: "modern",
      ageGroup: "young-adult" as AgeGroup,
      preferences: loadPreferences(),
      reloadPreferences: () => {},
    };
  }
  return context;
}

export default ThemeProvider;
