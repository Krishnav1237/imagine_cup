"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { Coins, Sparkles, ShoppingBag, Check, Egg, User as UserIcon, ImageIcon, Award } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AppNav } from "@/components/app-nav";
import { useUser } from "@/lib/user-context";
import { InventoryItem } from "@/lib/user-context";

const SHOP_ITEMS = [
  {
    id: "avatar-1",
    name: "Cosmic Wanderer",
    type: "avatar" as const,
    rarity: "Rare" as const,
    price: 500,
    imageUrl: "https://images.unsplash.com/photo-1614732414444-096e5f1122d5?w=400&h=400&fit=crop",
    description: "A mystical avatar from the depths of space",
  },
  {
    id: "avatar-2",
    name: "Neon Samurai",
    type: "avatar" as const,
    rarity: "Epic" as const,
    price: 800,
    imageUrl: "https://images.unsplash.com/photo-1603988492906-4fb0fb251cf0?w=400&h=400&fit=crop",
    description: "Futuristic warrior of the digital realm",
  },
  {
    id: "pet-egg-1",
    name: "Phoenix Egg",
    type: "pet" as const,
    rarity: "Epic" as const,
    price: 300,
    imageUrl: "https://images.unsplash.com/photo-1582562124811-c09040d0a901?w=400&h=400&fit=crop",
    description: "Hatches after completing 10 sprints. Evolves based on your study content",
  },
  {
    id: "pet-1",
    name: "Bio-Luminescent Turtle",
    type: "pet" as const,
    rarity: "Legendary" as const,
    price: 1200,
    imageUrl: "https://images.unsplash.com/photo-1437622368342-7a3d73a34c8f?w=400&h=400&fit=crop",
    description: "Perfect companion for biology students",
  },
  {
    id: "pet-2",
    name: "Pixel Glitch Cat",
    type: "pet" as const,
    rarity: "Epic" as const,
    price: 650,
    imageUrl: "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400&h=400&fit=crop",
    description: "Ideal for coding and tech enthusiasts",
  },
  {
    id: "card-pack-1",
    name: "Knowledge Card Pack",
    type: "card" as const,
    rarity: "Common" as const,
    price: 200,
    imageUrl: "https://images.unsplash.com/photo-1599687267812-35c05ff70ee9?w=400&h=400&fit=crop",
    description: "5 random knowledge cards from various topics",
  },
  {
    id: "badge-1",
    name: "Focus Master Badge",
    type: "badge" as const,
    rarity: "Rare" as const,
    price: 450,
    imageUrl: "https://images.unsplash.com/photo-1607301405390-d831c242f59b?w=400&h=400&fit=crop",
    description: "Show off your dedication to focus",
  },
  {
    id: "avatar-3",
    name: "Quantum Scientist",
    type: "avatar" as const,
    rarity: "Legendary" as const,
    price: 1500,
    imageUrl: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
    description: "For those who've mastered the sciences",
  },
];

export default function ShopPage() {
  const { focusCoins, spendCoins, purchaseItem, inventory } = useUser();
  const [filter, setFilter] = useState<"all" | "avatar" | "pet" | "card" | "badge">("all");
  const [purchasedItems, setPurchasedItems] = useState<Set<string>>(new Set(inventory.map(i => i.id)));

  const handlePurchase = (item: typeof SHOP_ITEMS[0]) => {
    if (purchasedItems.has(item.id)) return;
    if (spendCoins(item.price)) {
      purchaseItem(item);
      setPurchasedItems(new Set([...purchasedItems, item.id]));
    }
  };

  const filteredItems = filter === "all" ? SHOP_ITEMS : SHOP_ITEMS.filter(item => item.type === filter);

  const rarityColors = {
    Common: "#8888a0",
    Rare: "#06b6d4",
    Epic: "#7c3aed",
    Legendary: "#f59e0b",
  };

  const typeIcons = {
    avatar: UserIcon,
    pet: Egg,
    card: ImageIcon,
    badge: Award,
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
            <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6">
              <ShoppingBag className="w-4 h-4 text-[#f59e0b]" />
              <span className="text-sm text-[#8888a0]">Spend Your Focus Coins</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              The <span className="gradient-text">Shop</span>
            </h1>
            <p className="text-xl text-[#8888a0] max-w-2xl mx-auto mb-8">
              Reward your hard work with exclusive avatars, pets, and collectibles
            </p>
            
            <div className="inline-flex items-center gap-3 glass px-6 py-3 rounded-full">
              <Coins className="w-6 h-6 text-[#f59e0b]" />
              <div className="text-left">
                <div className="text-xs text-[#8888a0]">Your Balance</div>
                <div className="text-2xl font-bold text-[#f59e0b]">{focusCoins}</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex justify-center gap-2 mb-12"
          >
            {[
              { id: "all" as const, label: "All Items" },
              { id: "avatar" as const, label: "Avatars" },
              { id: "pet" as const, label: "Pets" },
              { id: "card" as const, label: "Cards" },
              { id: "badge" as const, label: "Badges" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id)}
                className={`px-6 py-3 rounded-xl transition-all ${
                  filter === tab.id
                    ? "bg-[#ff6b4a] text-[#0a0a12] font-semibold"
                    : "glass text-[#8888a0] hover:text-white"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredItems.map((item, i) => {
              const Icon = typeIcons[item.type];
              const isPurchased = purchasedItems.has(item.id);
              const canAfford = focusCoins >= item.price;

              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: i * 0.05 }}
                  className="glass rounded-2xl overflow-hidden hover:border-white/20 transition-all group"
                >
                  <div className="relative aspect-square overflow-hidden">
                    <img
                      src={item.imageUrl}
                      alt={item.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute top-3 right-3">
                      <div
                        className="px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-md"
                        style={{
                          backgroundColor: `${rarityColors[item.rarity]}20`,
                          color: rarityColors[item.rarity],
                          border: `1px solid ${rarityColors[item.rarity]}40`,
                        }}
                      >
                        {item.rarity}
                      </div>
                    </div>
                    <div className="absolute top-3 left-3">
                      <div className="w-8 h-8 rounded-lg bg-black/50 backdrop-blur-md flex items-center justify-center">
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                    </div>
                    {isPurchased && (
                      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center">
                        <div className="text-center">
                          <Check className="w-12 h-12 text-[#10b981] mx-auto mb-2" />
                          <p className="text-white font-semibold">Purchased</p>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="p-6">
                    <h3 className="text-lg font-semibold mb-2">{item.name}</h3>
                    <p className="text-sm text-[#8888a0] mb-4 line-clamp-2">{item.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Coins className="w-5 h-5 text-[#f59e0b]" />
                        <span className="text-xl font-bold text-[#f59e0b]">{item.price}</span>
                      </div>
                      <Button
                        onClick={() => handlePurchase(item)}
                        disabled={isPurchased || !canAfford}
                        className={`${
                          isPurchased
                            ? "bg-[#10b981]/20 text-[#10b981] cursor-not-allowed"
                            : canAfford
                            ? "bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12]"
                            : "bg-[#2a2a3e] text-[#8888a0] cursor-not-allowed"
                        }`}
                      >
                        {isPurchased ? "Owned" : canAfford ? "Buy" : "Not Enough"}
                      </Button>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {filteredItems.length === 0 && (
            <div className="text-center py-20">
              <Sparkles className="w-16 h-16 text-[#8888a0] mx-auto mb-4" />
              <p className="text-xl text-[#8888a0]">No items found in this category</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
