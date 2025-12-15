"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Zap, Mail, Lock, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function SignUpPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Mock sign up - save user data to localStorage
    localStorage.setItem("focusflow_user", JSON.stringify({
      name: formData.name,
      email: formData.email,
      signedUpAt: new Date().toISOString(),
    }));
    localStorage.setItem("focusflow_username", formData.name);
    
    // Redirect to onboarding for new users
    router.push("/splash");
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
              className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold h-12 text-base"
            >
              Create Account
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
