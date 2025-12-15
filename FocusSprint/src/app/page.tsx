"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { 
  Eye, 
  Zap, 
  Brain, 
  Trophy, 
  Play, 
  Pause, 
  Sparkles, 
  Target, 
  Clock, 
  BookOpen,
  Youtube,
  FileText,
  Presentation,
  Globe,
  ChevronRight,
  Coins,
  ShoppingBag,
  Egg,
  ImageIcon,
  ArrowRight,
  Check
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const fadeInUp = {
  initial: { opacity: 0, y: 40 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

function Navbar() {
  return (
    <motion.nav 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 glass"
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#ff6b4a] to-[#f59e0b] flex items-center justify-center">
            <Zap className="w-5 h-5 text-[#0a0a12]" />
          </div>
          <span className="font-bold text-xl tracking-tight">FocusSprint</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm text-[#8888a0]">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
          <a href="#ecosystem" className="hover:text-white transition-colors">Ecosystem</a>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/signin">
            <Button variant="ghost" className="text-white hover:text-white/80">
              Sign In
            </Button>
          </Link>
          <Link href="/signup">
            <Button className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-6">
              Sign Up
            </Button>
          </Link>
        </div>
      </div>
    </motion.nav>
  );
}

function HeroSection() {
  return (
    <section className="min-h-screen pt-32 pb-20 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(124,58,237,0.15)_0%,_transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_rgba(255,107,74,0.1)_0%,_transparent_50%)]" />
      
      <div className="absolute top-40 left-20 w-72 h-72 bg-[#7c3aed]/20 rounded-full blur-[120px]" />
      <div className="absolute bottom-40 right-20 w-96 h-96 bg-[#ff6b4a]/20 rounded-full blur-[150px]" />
      
      <motion.div 
        className="max-w-7xl mx-auto relative z-10"
        variants={staggerContainer}
        initial="initial"
        animate="animate"
      >
        <motion.div variants={fadeInUp} className="flex justify-center mb-6">
          <div className="glass px-4 py-2 rounded-full flex items-center gap-2 text-sm">
            <Sparkles className="w-4 h-4 text-[#f59e0b]" />
            <span className="text-[#8888a0]">AI-Powered Focus Training</span>
          </div>
        </motion.div>

        <motion.h1 
          variants={fadeInUp}
          className="text-5xl md:text-7xl lg:text-8xl font-bold text-center max-w-5xl mx-auto leading-[1.1] tracking-tight"
        >
          Turn Overwhelm Into{" "}
          <span className="gradient-text">Micro-Wins</span>
        </motion.h1>

        <motion.p 
          variants={fadeInUp}
          className="text-xl md:text-2xl text-[#8888a0] text-center max-w-2xl mx-auto mt-8 leading-relaxed"
        >
          An AI productivity app that transforms passive content into active sprints. 
          <span className="text-white"> Stay accountable with eye-tracking.</span> Earn rewards for focus.
        </motion.p>

        <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4 justify-center mt-12">
          <Link href="/signup">
            <Button 
              size="lg" 
              className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl animate-pulse-glow"
            >
              Sign Up
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
          <Button 
            size="lg" 
            variant="outline" 
            className="border-[#2a2a3e] bg-transparent hover:bg-[#1e1e2e] px-8 py-6 text-lg rounded-xl"
          >
            Watch Demo
            <Play className="w-5 h-5 ml-2" />
          </Button>
        </motion.div>

        <motion.div 
          variants={fadeInUp}
          className="mt-20 relative"
        >
          <div className="glass rounded-3xl p-2 max-w-5xl mx-auto overflow-hidden">
            <div className="relative aspect-video rounded-2xl bg-gradient-to-br from-[#1a1a28] to-[#12121c] overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center">
                <AppPreview />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={fadeInUp}
          className="mt-16 flex flex-wrap justify-center gap-8 text-[#8888a0]"
        >
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-[#1e1e2e] flex items-center justify-center">
              <Youtube className="w-5 h-5 text-[#ff6b4a]" />
            </div>
            <span>YouTube</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-[#1e1e2e] flex items-center justify-center">
              <FileText className="w-5 h-5 text-[#7c3aed]" />
            </div>
            <span>PDFs</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-[#1e1e2e] flex items-center justify-center">
              <Presentation className="w-5 h-5 text-[#06b6d4]" />
            </div>
            <span>Slides</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-[#1e1e2e] flex items-center justify-center">
              <Globe className="w-5 h-5 text-[#10b981]" />
            </div>
            <span>Articles</span>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
}

function AppPreview() {
  const [isLooking, setIsLooking] = useState(true);
  
  return (
    <div className="w-full h-full p-8 flex gap-6">
      <div className="flex-1 flex flex-col gap-4">
        <div className="flex items-center gap-4 mb-2">
          <div className="flex items-center gap-2 text-sm text-[#8888a0]">
            <Clock className="w-4 h-4" />
            <span>Sprint 3 of 12</span>
          </div>
          <div className="flex-1 h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-[#ff6b4a] to-[#f59e0b]"
              initial={{ width: "0%" }}
              animate={{ width: "25%" }}
              transition={{ duration: 2, ease: "easeOut" }}
            />
          </div>
          <div className="flex items-center gap-1 text-[#f59e0b] font-semibold">
            <Coins className="w-4 h-4" />
            <span>150</span>
          </div>
        </div>
        
        <div 
          className={`flex-1 rounded-xl overflow-hidden relative transition-all duration-500 ${!isLooking ? 'blur-md' : ''}`}
          style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=800&auto=format&fit=crop&q=60)', backgroundSize: 'cover', backgroundPosition: 'center' }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
          <div className="absolute bottom-4 left-4 right-4">
            <p className="text-white font-medium">Introduction to Python Variables</p>
            <p className="text-sm text-[#8888a0]">2:34 / 5:00</p>
          </div>
          {!isLooking && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60">
              <div className="text-center">
                <Eye className="w-12 h-12 text-[#ff6b4a] mx-auto mb-2" />
                <p className="text-white font-medium">Look at the screen to resume</p>
              </div>
            </div>
          )}
        </div>
        
        <button 
          onClick={() => setIsLooking(!isLooking)}
          className="glass px-4 py-2 rounded-lg text-sm text-[#8888a0] hover:text-white transition-colors"
        >
          {isLooking ? 'Simulate Looking Away' : 'Simulate Looking Back'}
        </button>
      </div>
      
      <div className="w-64 flex flex-col gap-4">
        <div className="glass rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Eye className="w-5 h-5 text-[#10b981]" />
            <span className="text-sm font-medium">Focus Status</span>
          </div>
          <div className={`text-2xl font-bold ${isLooking ? 'text-[#10b981]' : 'text-[#ff6b4a]'}`}>
            {isLooking ? 'Focused' : 'Distracted'}
          </div>
          <div className="text-sm text-[#8888a0] mt-1">
            {isLooking ? 'Keep it up!' : 'Video paused'}
          </div>
        </div>
        
        <div className="glass rounded-xl p-4 flex-1">
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-5 h-5 text-[#7c3aed]" />
            <span className="text-sm font-medium">Sprint Queue</span>
          </div>
          <div className="space-y-2">
            {['Variables & Types', 'Control Flow', 'Functions'].map((item, i) => (
              <div key={i} className={`text-sm px-3 py-2 rounded-lg ${i === 0 ? 'bg-[#7c3aed]/20 text-[#a78bfa]' : 'text-[#8888a0]'}`}>
                {i === 0 && <span className="text-xs text-[#7c3aed] mr-2">NOW</span>}
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function FeaturesSection() {
  const features = [
    {
      icon: Brain,
      title: "AI Content Metabolizer",
      description: "Transforms any learning content into concept-based micro-sprints. No more doom-scrolling through hour-long videos.",
      color: "#7c3aed"
    },
    {
      icon: Eye,
      title: "Digital Body Double",
      description: "Eye-tracking accountability without the social anxiety. The camera keeps you honest—locally and privately.",
      color: "#ff6b4a"
    },
    {
      icon: ImageIcon,
      title: "Visual Lock-In",
      description: "AI generates infographic cards after each sprint using dual-coding theory. Memory that sticks.",
      color: "#06b6d4"
    },
    {
      icon: Trophy,
      title: "Dopamine Economy",
      description: "Earn Focus Coins for completing sprints. Build streaks. Collect rare knowledge cards. Make studying feel like a game.",
      color: "#f59e0b"
    }
  ];

  return (
    <section id="features" className="py-32 px-6 relative">
      <div className="max-w-7xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Built for <span className="gradient-text">Distracted Minds</span>
          </h2>
          <p className="text-xl text-[#8888a0] max-w-2xl mx-auto">
            Every feature designed to work with your brain, not against it.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className="glass rounded-2xl p-8 hover:border-white/20 transition-all group"
            >
              <div 
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-6"
                style={{ backgroundColor: `${feature.color}20` }}
              >
                <feature.icon className="w-7 h-7" style={{ color: feature.color }} />
              </div>
              <h3 className="text-2xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-[#8888a0] leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorksSection() {
  const steps = [
    {
      phase: "Phase 1",
      title: "The Input",
      subtitle: "The Metabolizer",
      description: "Paste any YouTube URL, upload PDFs, slides, or articles. The AI analyzes content by concepts—not timestamps—and creates your personalized playlist of micro-sprints.",
      icon: BookOpen,
      color: "#7c3aed"
    },
    {
      phase: "Phase 2",
      title: "The Sprint",
      subtitle: "The Body Double",
      description: "Start a 5-minute sprint. Your camera activates locally. Look away for 5+ seconds? Content pauses and blurs. A gentle nudge back to focus—no judgment, just accountability.",
      icon: Eye,
      color: "#ff6b4a"
    },
    {
      phase: "Phase 3",
      title: "The Lock-In",
      subtitle: "The Nano-Summary",
      description: "Sprint ends. Before moving on, see an AI-generated infographic card of what you just learned. Quick quiz to lock it in. Dual-coding meets active recall.",
      icon: Brain,
      color: "#06b6d4"
    },
    {
      phase: "Phase 4",
      title: "The Reward",
      subtitle: "The Economy",
      description: "+50 Focus Coins. Streak multiplier activated. Choose: dive into the next sprint for 2x coins, or visit the shop to spend your hard-earned focus.",
      icon: Trophy,
      color: "#f59e0b"
    }
  ];

  return (
    <section id="how-it-works" className="py-32 px-6 relative overflow-hidden">
      <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-[#2a2a3e] to-transparent" />
      
      <div className="max-w-7xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            The <span className="gradient-text">Focus Loop</span>
          </h2>
          <p className="text-xl text-[#8888a0] max-w-2xl mx-auto">
            A scientifically-backed system that turns learning into a dopamine-friendly experience.
          </p>
        </motion.div>

        <div className="space-y-24">
          {steps.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: i % 2 === 0 ? -50 : 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className={`flex items-center gap-12 ${i % 2 === 1 ? 'flex-row-reverse' : ''}`}
            >
              <div className="flex-1">
                <div 
                  className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm mb-4"
                  style={{ backgroundColor: `${step.color}20`, color: step.color }}
                >
                  <span className="font-semibold">{step.phase}</span>
                </div>
                <h3 className="text-3xl font-bold mb-2">{step.title}</h3>
                <p className="text-lg text-[#8888a0] mb-4">{step.subtitle}</p>
                <p className="text-[#8888a0] leading-relaxed">{step.description}</p>
              </div>
              
              <div className="relative">
                <div 
                  className="w-32 h-32 rounded-3xl flex items-center justify-center"
                  style={{ backgroundColor: `${step.color}15` }}
                >
                  <step.icon className="w-16 h-16" style={{ color: step.color }} />
                </div>
                <div 
                  className="absolute -inset-4 rounded-[32px] -z-10 blur-2xl opacity-30"
                  style={{ backgroundColor: step.color }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function EcosystemSection() {
  const shopItems = [
    { name: "Cosmic Avatar", price: 500, type: "Avatar", rarity: "Rare" },
    { name: "Phoenix Egg", price: 300, type: "Pet Egg", rarity: "Epic" },
    { name: "Bio-Luminescent Turtle", price: 800, type: "Pet", rarity: "Legendary" },
    { name: "Pixel Glitch Cat", price: 650, type: "Pet", rarity: "Epic" },
  ];

  return (
    <section id="ecosystem" className="py-32 px-6 relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(255,107,74,0.08)_0%,_transparent_60%)]" />
      
      <div className="max-w-7xl mx-auto relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            The <span className="gradient-text">Gamification Ecosystem</span>
          </h2>
          <p className="text-xl text-[#8888a0] max-w-2xl mx-auto">
            Replace the pain of studying with the pleasure of earning.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-[#f59e0b]/20 flex items-center justify-center">
                <Coins className="w-6 h-6 text-[#f59e0b]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Focus Coins</h3>
                <p className="text-sm text-[#8888a0]">Earn by completing sprints</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#1e1e2e]">
                <span className="text-[#8888a0]">Sprint Completed</span>
                <span className="text-[#f59e0b] font-semibold">+50</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#1e1e2e]">
                <span className="text-[#8888a0]">Perfect Focus (no pauses)</span>
                <span className="text-[#f59e0b] font-semibold">+25 bonus</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#1e1e2e]">
                <span className="text-[#8888a0]">3x Streak</span>
                <span className="text-[#f59e0b] font-semibold">×2 multiplier</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-[#7c3aed]/20 flex items-center justify-center">
                <ShoppingBag className="w-6 h-6 text-[#7c3aed]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">The Shop</h3>
                <p className="text-sm text-[#8888a0]">Spend your earnings</p>
              </div>
            </div>
            <div className="space-y-3">
              {shopItems.map((item, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#1e1e2e]">
                  <div>
                    <p className="font-medium text-sm">{item.name}</p>
                    <p className="text-xs text-[#8888a0]">{item.type} · {item.rarity}</p>
                  </div>
                  <div className="flex items-center gap-1 text-[#f59e0b] font-semibold text-sm">
                    <Coins className="w-3 h-3" />
                    {item.price}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-[#10b981]/20 flex items-center justify-center">
                <Egg className="w-6 h-6 text-[#10b981]" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Focus Pets</h3>
                <p className="text-sm text-[#8888a0]">Evolve with your studies</p>
              </div>
            </div>
            <div className="relative h-48 rounded-xl bg-gradient-to-br from-[#1e1e2e] to-[#12121c] overflow-hidden flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-2">🐢</div>
                <p className="font-medium text-[#10b981]">Bio-Luminescent Turtle</p>
                <p className="text-xs text-[#8888a0]">Evolved from studying Biology</p>
              </div>
              <div className="absolute top-2 right-2 px-2 py-1 rounded-full bg-[#10b981]/20 text-[#10b981] text-xs font-semibold">
                Legendary
              </div>
            </div>
            <p className="text-sm text-[#8888a0] mt-4">
              Your pet evolves based on what you study. Code → Pixel Glitch Cat. Biology → Bio-Luminescent Turtle.
            </p>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-12 glass rounded-2xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-[#06b6d4]/20 flex items-center justify-center">
              <ImageIcon className="w-6 h-6 text-[#06b6d4]" />
            </div>
            <div>
              <h3 className="text-xl font-semibold">Knowledge Card Collection</h3>
              <p className="text-sm text-[#8888a0]">Your visual study deck grows with every sprint</p>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['Quantum Physics', 'Machine Learning', 'Web Dev', 'Calculus'].map((topic, i) => (
              <div key={i} className="aspect-[3/4] rounded-xl bg-gradient-to-br from-[#1e1e2e] to-[#12121c] p-4 flex flex-col justify-between border border-[#2a2a3e] hover:border-[#ff6b4a]/50 transition-colors cursor-pointer">
                <div className="text-xs text-[#8888a0]">Card #{(i + 1).toString().padStart(3, '0')}</div>
                <div>
                  <p className="font-semibold text-sm">{topic}</p>
                  <p className="text-xs text-[#8888a0]">{5 + i * 2} cards collected</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function USPSection() {
  const usps = [
    {
      icon: Globe,
      title: "Input Agnostic",
      description: "YouTube, PDFs, slides, articles—it doesn't matter where learning comes from. The app handles any format."
    },
    {
      icon: Eye,
      title: "External Accountability",
      description: "A 'strict librarian' without the social anxiety. The camera keeps you honest while respecting your privacy."
    },
    {
      icon: ImageIcon,
      title: "Visual Save Points",
      description: "AI-generated infographics prevent 'in one ear, out the other.' Dual-coding locks memories in place."
    },
    {
      icon: Sparkles,
      title: "Tangible Progress",
      description: "Watch your pet evolve. See your card deck grow. The invisible labor of studying becomes visible."
    }
  ];

  return (
    <section className="py-32 px-6 relative">
      <div className="max-w-7xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Why <span className="gradient-text">FocusSprint</span>?
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {usps.map((usp, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="text-center p-6"
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#ff6b4a]/20 to-[#7c3aed]/20 flex items-center justify-center mx-auto mb-4">
                <usp.icon className="w-8 h-8 text-[#ff6b4a]" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{usp.title}</h3>
              <p className="text-[#8888a0] text-sm leading-relaxed">{usp.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className="py-32 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#ff6b4a]/5 to-transparent" />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="max-w-4xl mx-auto relative z-10"
      >
        <div className="glass rounded-3xl p-12 text-center relative overflow-hidden">
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-[#ff6b4a]/20 rounded-full blur-[80px]" />
          <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-[#7c3aed]/20 rounded-full blur-[80px]" />
          
          <div className="relative z-10">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to Transform Your <span className="gradient-text">Focus</span>?
            </h2>
            <p className="text-xl text-[#8888a0] mb-8 max-w-2xl mx-auto">
              Join the waitlist and be the first to turn your learning overwhelm into micro-wins.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
              <input 
                type="email" 
                placeholder="Enter your email"
                className="flex-1 px-6 py-4 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e] text-white placeholder:text-[#8888a0] focus:outline-none focus:border-[#ff6b4a] transition-colors"
              />
              <Button className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-4 text-lg rounded-xl whitespace-nowrap">
                Get Early Access
              </Button>
            </div>
            <div className="flex items-center justify-center gap-6 mt-6 text-sm text-[#8888a0]">
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-[#10b981]" />
                <span>Free to start</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-[#10b981]" />
                <span>No credit card</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-[#10b981]" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-[#2a2a3e]">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#ff6b4a] to-[#f59e0b] flex items-center justify-center">
            <Zap className="w-4 h-4 text-[#0a0a12]" />
          </div>
          <span className="font-bold">FocusSprint</span>
        </div>
        <div className="flex items-center gap-6 text-sm text-[#8888a0]">
          <a href="#" className="hover:text-white transition-colors">Privacy</a>
          <a href="#" className="hover:text-white transition-colors">Terms</a>
          <a href="#" className="hover:text-white transition-colors">Contact</a>
        </div>
        <p className="text-sm text-[#8888a0]">© 2024 FocusSprint. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <EcosystemSection />
      <USPSection />
      <CTASection />
      <Footer />
    </div>
  );
}
