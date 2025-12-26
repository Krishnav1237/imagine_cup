"use client";

import { useEffect, useState } from "react";

declare global {
  interface Window {
    __fs_original_fetch__?: typeof fetch;
  }
}

/**
 * Global top loading bar that reacts to client-side fetch calls.
 * Uses the app's accent color and appears at the top of every page.
 */
export function TopLoadingBar() {
  const [activeRequests, setActiveRequests] = useState(0);
  const [visible, setVisible] = useState(false);
  const [progress, setProgress] = useState(0);

  // React immediately to important user actions (e.g. primary buttons)
  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleStart = () => {
      setVisible(true);
      setProgress((prev) => (prev < 25 ? 25 : prev));
    };

    window.addEventListener("fs-loading-start", handleStart);
    return () => window.removeEventListener("fs-loading-start", handleStart);
  }, []);

  // Patch window.fetch once on the client to track in-flight requests
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (window.__fs_original_fetch__) return; // already patched

    const originalFetch = window.fetch.bind(window);
    window.__fs_original_fetch__ = originalFetch;

    window.fetch = async (...args: Parameters<typeof fetch>): Promise<Response> => {
      setActiveRequests((prev) => {
        const next = prev + 1;
        if (next === 1) {
          // First request: show bar; if no user-start event fired, kick off a small base progress
          setVisible(true);
          setProgress((prev) => (prev === 0 ? 10 : prev));
        }
        return next;
      });
      try {
        const res = await originalFetch(...args);
        return res;
      } finally {
        setActiveRequests((prev) => Math.max(0, prev - 1));
      }
    };

    return () => {
      if (window.__fs_original_fetch__) {
        window.fetch = window.__fs_original_fetch__!;
        delete window.__fs_original_fetch__;
      }
    };
  }, []);

  // Control bar visibility and progress animation
  useEffect(() => {
    if (!visible) return;

    // While there are active requests, advance progress slowly towards ~75%
    if (activeRequests > 0) {
      const interval = setInterval(() => {
        setProgress((prev) => {
          const target = 75;
          if (prev >= target) return prev;
          const delta =
            prev < 40 ? 3 :
            prev < 60 ? 2 :
            1;
          return Math.min(prev + delta, target);
        });
      }, 250);

      return () => clearInterval(interval);
    }

    // When all requests complete, fill to 100% then hide
    if (activeRequests === 0 && visible) {
      setProgress(100);
      const timeout = setTimeout(() => {
        setVisible(false);
        setProgress(0);
      }, 350);
      return () => clearTimeout(timeout);
    }
  }, [activeRequests, visible]);

  return (
    <div className="fixed top-0 left-0 right-0 z-[9999] pointer-events-none">
      <div
        className={`h-1 w-full overflow-hidden transition-opacity duration-200 ${
          visible ? "opacity-100" : "opacity-0"
        }`}
      >
        <div
          className="fs-loading-bar-inner h-full"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}


