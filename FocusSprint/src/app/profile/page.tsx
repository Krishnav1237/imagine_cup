"use client";

import { motion } from "framer-motion";
import { Trophy, Coins, Target, Clock, Award, Egg, User as UserIcon, ImageIcon, Flame } from "lucide-react";
import { AppNav } from "@/components/app-nav";
import { useUser } from "@/lib/user-context";

export default function ProfilePage() {
  const { focusCoins, streak, inventory, completedSprints } = useUser();

  const stats = {
    totalSprints: completedSprints.length,
    totalFocusTime: completedSprints.reduce((acc, sprint) => acc + sprint.duration, 0),
    averageFocus: completedSprints.length > 0 ? 87 : 0,
    longestStreak: Math.max(streak, 12),
  };

  const typeIcons = {
    avatar: UserIcon,
    pet: Egg,
    card: ImageIcon,
    badge: Award,
  };

  const rarityColors = {
    Common: "#8888a0",
    Rare: "#06b6d4",
    Epic: "#7c3aed",
    Legendary: "#f59e0b",
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />
      
      <div className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-[#ff6b4a] to-[#7c3aed] flex items-center justify-center mx-auto mb-6">
              <UserIcon className="w-16 h-16 text-white" />
            </div>
            <h1 className="text-4xl font-bold mb-2">Focus Champion</h1>
            <p className="text-[#8888a0]">Level {Math.floor(completedSprints.length / 5) + 1} · Joined Dec 2024</p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-xl bg-[#f59e0b]/20 flex items-center justify-center">
                  <Coins className="w-6 h-6 text-[#f59e0b]" />
                </div>
                <div>
                  <div className="text-sm text-[#8888a0]">Focus Coins</div>
                  <div className="text-2xl font-bold text-[#f59e0b]">{focusCoins}</div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-xl bg-[#ff6b4a]/20 flex items-center justify-center">
                  <Flame className="w-6 h-6 text-[#ff6b4a]" />
                </div>
                <div>
                  <div className="text-sm text-[#8888a0]">Current Streak</div>
                  <div className="text-2xl font-bold">{streak} days</div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-xl bg-[#7c3aed]/20 flex items-center justify-center">
                  <Target className="w-6 h-6 text-[#7c3aed]" />
                </div>
                <div>
                  <div className="text-sm text-[#8888a0]">Sprints Completed</div>
                  <div className="text-2xl font-bold">{stats.totalSprints}</div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-xl bg-[#10b981]/20 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-[#10b981]" />
                </div>
                <div>
                  <div className="text-sm text-[#8888a0]">Focus Time</div>
                  <div className="text-2xl font-bold">
                    {Math.floor(stats.totalFocusTime / 3600)}h {Math.floor((stats.totalFocusTime % 3600) / 60)}m
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="glass rounded-2xl p-8 mb-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-[#7c3aed]/20 flex items-center justify-center">
                <Trophy className="w-6 h-6 text-[#7c3aed]" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Achievements</h2>
                <p className="text-sm text-[#8888a0]">Your focus milestones</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {[
                {
                  name: "First Sprint",
                  description: "Complete your first sprint",
                  unlocked: completedSprints.length >= 1,
                  icon: Target,
                },
                {
                  name: "Week Warrior",
                  description: "Maintain a 7-day streak",
                  unlocked: streak >= 7,
                  icon: Flame,
                },
                {
                  name: "Century Club",
                  description: "Complete 100 sprints",
                  unlocked: stats.totalSprints >= 100,
                  icon: Trophy,
                },
                {
                  name: "Focus Master",
                  description: "Achieve 95% average focus",
                  unlocked: stats.averageFocus >= 95,
                  icon: Award,
                },
              ].map((achievement, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-xl ${
                    achievement.unlocked
                      ? "bg-gradient-to-br from-[#ff6b4a]/20 to-[#7c3aed]/20 border border-[#ff6b4a]/30"
                      : "bg-[#1e1e2e] border border-[#2a2a3e]"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        achievement.unlocked ? "bg-[#ff6b4a]/20" : "bg-[#2a2a3e]"
                      }`}
                    >
                      <achievement.icon
                        className={`w-5 h-5 ${achievement.unlocked ? "text-[#ff6b4a]" : "text-[#8888a0]"}`}
                      />
                    </div>
                    <div>
                      <p className={`font-semibold ${achievement.unlocked ? "text-white" : "text-[#8888a0]"}`}>
                        {achievement.name}
                      </p>
                      <p className="text-xs text-[#8888a0]">{achievement.description}</p>
                    </div>
                    {achievement.unlocked && (
                      <div className="ml-auto">
                        <div className="w-6 h-6 rounded-full bg-[#10b981] flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="glass rounded-2xl p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-[#06b6d4]/20 flex items-center justify-center">
                <ImageIcon className="w-6 h-6 text-[#06b6d4]" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Your Collection</h2>
                <p className="text-sm text-[#8888a0]">{inventory.length} items owned</p>
              </div>
            </div>

            {inventory.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {inventory.map((item, i) => {
                  const Icon = typeIcons[item.type];
                  return (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: i * 0.05 }}
                      className="glass rounded-xl overflow-hidden group hover:border-white/20 transition-all"
                    >
                      <div className="relative aspect-square">
                        <img src={item.imageUrl} alt={item.name} className="w-full h-full object-cover" />
                        <div className="absolute top-2 right-2">
                          <div
                            className="w-6 h-6 rounded-lg backdrop-blur-md flex items-center justify-center"
                            style={{
                              backgroundColor: `${rarityColors[item.rarity]}40`,
                            }}
                          >
                            <Icon
                              className="w-3 h-3"
                              style={{ color: rarityColors[item.rarity] }}
                            />
                          </div>
                        </div>
                      </div>
                      <div className="p-3">
                        <p className="text-sm font-semibold truncate">{item.name}</p>
                        <p
                          className="text-xs capitalize"
                          style={{ color: rarityColors[item.rarity] }}
                        >
                          {item.rarity}
                        </p>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12">
                <ImageIcon className="w-16 h-16 text-[#8888a0] mx-auto mb-4" />
                <p className="text-xl text-[#8888a0] mb-2">Your collection is empty</p>
                <p className="text-sm text-[#8888a0]">Complete sprints to earn coins and visit the shop!</p>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
