"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Zap, Mail, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { loginUser, fetchCurrentUser } from "@/lib/api";

export default function SignInPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 1. Login against backend to get JWT
      const auth = await loginUser(formData.email, formData.password);
      localStorage.setItem("focus_token", auth.access_token);

      // 2. Fetch user profile and cache it for UI
      try {
        const profile = await fetchCurrentUser(auth.access_token);
        localStorage.setItem("focusflow_user", JSON.stringify(profile));
        const username =
          profile.full_name ||
          profile.email?.split("@")[0] ||
          formData.email.split("@")[0] ||
          "Learner";
        localStorage.setItem("focusflow_username", username);
      } catch {
        // Non-fatal; continue even if profile fails
      }

      // If they haven't gone through onboarding on this device, send them there
      const hasOnboarded = localStorage.getItem("focusflow_onboarded");
      if (hasOnboarded) {
        router.push("/dashboard");
      } else {
        router.push("/splash");
      }
    } catch (err: any) {
      setError(err.message || "Failed to sign in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <Link href="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#ff6b4a] to-[#f59e0b] flex items-center justify-center">
              <Zap className="w-6 h-6 text-[#0a0a12]" />
            </div>
            <span className="text-2xl font-bold">FocusFlow</span>
          </Link>
          <h1 className="text-3xl font-bold mb-2">Welcome back</h1>
          <p className="text-[#8888a0]">Sign in to continue your learning journey</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="glass rounded-3xl p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="mb-3 text-sm text-red-400 bg-red-500/10 border border-red-500/40 rounded-xl px-4 py-2">
                {error}
              </div>
            )}
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8888a0]" />
                <Input
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="pl-12 bg-[#1e1e2e] border-[#2a2a3e] focus:border-[#ff6b4a] h-12"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium">Password</label>
                <Link href="#" className="text-sm text-[#ff6b4a] hover:text-[#ff8a70]">
                  Forgot?
                </Link>
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8888a0]" />
                <Input
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="pl-12 bg-[#1e1e2e] border-[#2a2a3e] focus:border-[#ff6b4a] h-12"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold h-12 text-base disabled:opacity-60"
            >
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#8888a0]">
              Don't have an account?{" "}
              <Link href="/signup" className="text-[#ff6b4a] hover:text-[#ff8a70] font-medium">
                Sign up for free
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}