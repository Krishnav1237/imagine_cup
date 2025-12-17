"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Zap, Mail, Lock, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { registerUser, loginUser, fetchCurrentUser } from "@/lib/api";

export default function SignUpPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
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
      // 1. Create user in backend
      await registerUser({
        email: formData.email,
        password: formData.password,
        full_name: formData.name,
      });

      // 2. Immediately log them in to get JWT
      const auth = await loginUser(formData.email, formData.password);
      localStorage.setItem("focus_token", auth.access_token);

      // 3. Fetch profile and store basic info locally for UI
      try {
        const profile = await fetchCurrentUser(auth.access_token);
        localStorage.setItem("focusflow_user", JSON.stringify(profile));
        const username =
          profile.full_name ||
          profile.email?.split("@")[0] ||
          formData.name ||
          "Learner";
        localStorage.setItem("focusflow_username", username);
      } catch {
        // Non-fatal: still proceed if profile fetch fails
      }

      // Mark onboarding not yet complete so splash can route correctly
      localStorage.removeItem("focusflow_onboarded");

      // Redirect to onboarding for new users
      router.push("/splash");
    } catch (err: any) {
      setError(err.message || "Failed to create account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        {/* Logo */}
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
          <h1 className="text-3xl font-bold mb-2">Create your account</h1>
          <p className="text-[#8888a0]">Start learning at your own pace</p>
        </motion.div>

        {/* Sign Up Form */}
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
              <label className="block text-sm font-medium mb-2">Full Name</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8888a0]" />
                <Input
                  type="text"
                  placeholder="Enter your name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="pl-12 bg-[#1e1e2e] border-[#2a2a3e] focus:border-[#ff6b4a] h-12"
                  required
                />
              </div>
            </div>

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
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8888a0]" />
                <Input
                  type="password"
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="pl-12 bg-[#1e1e2e] border-[#2a2a3e] focus:border-[#ff6b4a] h-12"
                  required
                  minLength={6}
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold h-12 text-base disabled:opacity-60"
            >
              {loading ? "Creating account..." : "Create Account"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-[#8888a0]">
              Already have an account?{" "}
              <Link href="/signin" className="text-[#ff6b4a] hover:text-[#ff8a70] font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>

        {/* Privacy Note */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-center text-sm text-[#8888a0] mt-6"
        >
          By signing up, you agree to our Terms of Service and Privacy Policy
        </motion.p>
      </div>
    </div>
  );
}
