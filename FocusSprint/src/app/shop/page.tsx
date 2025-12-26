"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { Coins, Sparkles, ShoppingBag, Check, Egg, User as UserIcon, ImageIcon, Award, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AppNav } from "@/components/app-nav";
import { getShopItems, purchaseItem as apiPurchaseItem, ShopItem } from "@/lib/api";

// Fallback items in case API fails
const FALLBACK_ITEMS: ShopItem[] = [
  {
    id: "avatar_cosmic",
    name: "Cosmic Avatar",
    type: "avatar",
    rarity: "Rare",
    price: 500,
    description: "A mystical cosmic avatar that shows your dedication to learning",
    affordable: true,
  },
];

export default function ShopPage() {
  const [items, setItems] = useState<ShopItem[]>([]);
  const [userBalance, setUserBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [purchasedItems, setPurchasedItems] = useState<Set<string>>(new Set());
  const [purchasing, setPurchasing] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "avatar" | "pet" | "card_pack" | "badge">("all");

  // Fetch shop items from API
  useEffect(() => {
    const fetchShopItems = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getShopItems();
        setItems(data.items);
        setUserBalance(data.user_balance);
      } catch (err) {
        console.error("Failed to load shop items:", err);
        setError("Failed to load shop. Using offline mode.");
        setItems(FALLBACK_ITEMS);
      } finally {
        setLoading(false);
      }
    };

    fetchShopItems();
  }, []);

  const handlePurchase = async (item: ShopItem) => {
    if (purchasedItems.has(item.id)) return;
    if (userBalance < item.price) return;

    try {
      setPurchasing(item.id);
      const result = await apiPurchaseItem(item.id);
      
      // Update balance and mark as purchased
      setUserBalance(result.new_balance);
      setPurchasedItems(new Set([...purchasedItems, item.id]));
      
      // Update item affordability
      setItems(prev => prev.map(i => ({
        ...i,
        affordable: result.new_balance >= i.price
      })));
    } catch (err) {
      console.error("Purchase failed:", err);
      alert("Purchase failed. Please try again.");
    } finally {
      setPurchasing(null);
    }
  };

  const filteredItems = filter === "all" 
    ? items 
    : items.filter(item => item.type === filter);

  const rarityColors: Record<string, string> = {
    Common: "#8888a0",
    Rare: "#06b6d4",
    Epic: "#7c3aed",
    Legendary: "#f59e0b",
  };

  const typeIcons: Record<string, typeof UserIcon> = {
    avatar: UserIcon,
    pet: Egg,
    card_pack: ImageIcon,
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
                <div className="text-2xl font-bold text-[#f59e0b]">
                  {loading ? "..." : userBalance.toLocaleString()}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Error Banner */}
          {error && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 px-4 py-3 rounded-xl mb-6 text-center">
              {error}
            </div>
          )}

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex justify-center gap-2 mb-12 flex-wrap"
          >
            {[
              { id: "all" as const, label: "All Items" },
              { id: "avatar" as const, label: "Avatars" },
              { id: "pet" as const, label: "Pets" },
              { id: "card_pack" as const, label: "Cards" },
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

          {/* Loading State */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-12 h-12 text-[#ff6b4a] animate-spin" />
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredItems.map((item, i) => {
                const Icon = typeIcons[item.type] || ImageIcon;
                const isPurchased = purchasedItems.has(item.id);
                const canAfford = userBalance >= item.price;
                const isPurchasing = purchasing === item.id;

                return (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: i * 0.05 }}
                    className="glass rounded-2xl overflow-hidden hover:border-white/20 transition-all group"
                  >
                    <div className="relative aspect-square overflow-hidden bg-gradient-to-br from-[#1e1e2e] to-[#0a0a12]">
                      <div className="w-full h-full flex items-center justify-center">
                        <Icon className="w-20 h-20 text-[#8888a0]/30" />
                      </div>
                      <div className="absolute top-3 right-3">
                        <div
                          className="px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-md"
                          style={{
                            backgroundColor: `${rarityColors[item.rarity] || "#8888a0"}20`,
                            color: rarityColors[item.rarity] || "#8888a0",
                            border: `1px solid ${rarityColors[item.rarity] || "#8888a0"}40`,
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
                          disabled={isPurchased || !canAfford || isPurchasing}
                          className={`${
                            isPurchased
                              ? "bg-[#10b981]/20 text-[#10b981] cursor-not-allowed"
                              : canAfford
                              ? "bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12]"
                              : "bg-[#2a2a3e] text-[#8888a0] cursor-not-allowed"
                          }`}
                        >
                          {isPurchasing ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : isPurchased ? (
                            "Owned"
                          ) : canAfford ? (
                            "Buy"
                          ) : (
                            "Not Enough"
                          )}
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}

          {!loading && filteredItems.length === 0 && (
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
