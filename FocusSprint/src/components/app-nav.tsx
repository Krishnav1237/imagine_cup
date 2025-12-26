"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Home, Play, BookOpen, BarChart3, Settings, Coins, Zap, LogOut } from "lucide-react";
import { useUser } from "@/lib/user-context";

export function AppNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { focusCoins, streak, logout } = useUser();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const links = [
    { href: "/dashboard", icon: Home, label: "Home" },
    { href: "/upload", icon: Play, label: "Learn" },
    { href: "/knowledge-bank", icon: BookOpen, label: "Library" },
    { href: "/profile", icon: BarChart3, label: "Analytics" },
    { href: "/settings", icon: Settings, label: "Settings" },
  ];

  if (pathname === "/sprint" || pathname === "/onboarding" || pathname === "/splash") return null;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#ff6b4a] to-[#f59e0b] flex items-center justify-center">
            <Zap className="w-5 h-5 text-[#0a0a12]" />
          </div>
          <span className="font-bold text-xl tracking-tight">FocusFlow</span>
        </Link>

        <div className="hidden md:flex items-center gap-6">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-2 text-sm hover:text-white transition-colors ${
                pathname === link.href ? "text-white" : "text-[#8888a0]"
              }`}
            >
              <link.icon className="w-4 h-4" />
              {link.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {/* Gamification elements preserved for dopamine rewards */}
          <Link href="/shop">
            <div className="flex items-center gap-2 glass px-4 py-2 rounded-full hover:border-white/20 transition-all cursor-pointer">
              <Coins className="w-4 h-4 text-[#f59e0b]" />
              <span className="text-white font-semibold">{focusCoins}</span>
            </div>
          </Link>
          {streak > 0 && (
            <div className="glass px-3 py-2 rounded-full text-sm">
              🔥 {streak}
            </div>
          )}
          <button
            onClick={() => {
              logout();
              router.push("/splash");
            }}
            aria-label="Logout"
            className="glass p-2 rounded-full hover:bg-white/5 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4 text-[#ff6b4a]" />
          </button>
        </div>
      </div>
    </nav>
  );
}
