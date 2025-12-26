"""
Mystery Rewards System for ADHD-Optimized Dopamine Release.
Variable rewards keep engagement high by activating dopamine circuits.
"""
import random
import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger("MysteryRewards")


class RewardTier(Enum):
    """Reward tiers with different probabilities and multipliers."""
    COMMON = "common"       # 60% chance, 1x multiplier
    UNCOMMON = "uncommon"   # 25% chance, 1.5x multiplier
    RARE = "rare"           # 10% chance, 2x multiplier
    EPIC = "epic"           # 4% chance, 3x multiplier
    LEGENDARY = "legendary" # 1% chance, 5-10x multiplier (jackpot!)


@dataclass
class MysteryReward:
    """A mystery reward result."""
    tier: RewardTier
    base_coins: int
    multiplier: float
    final_coins: int
    bonus_item: Optional[str] = None
    message: str = ""
    celebration_level: int = 1  # 1-5, controls animation intensity


# Tier probabilities (must sum to 100)
TIER_WEIGHTS = {
    RewardTier.COMMON: 60,
    RewardTier.UNCOMMON: 25,
    RewardTier.RARE: 10,
    RewardTier.EPIC: 4,
    RewardTier.LEGENDARY: 1,
}

# Multiplier ranges for each tier
MULTIPLIER_RANGES = {
    RewardTier.COMMON: (1.0, 1.2),
    RewardTier.UNCOMMON: (1.3, 1.7),
    RewardTier.RARE: (1.8, 2.5),
    RewardTier.EPIC: (2.5, 4.0),
    RewardTier.LEGENDARY: (5.0, 10.0),
}

# Celebration messages by tier - ADULT-FOCUSED, PROFESSIONAL
TIER_MESSAGES = {
    RewardTier.COMMON: [
        "Solid progress. 🎯",
        "Another session in the books. 💼",
        "Consistency builds mastery. ✨",
        "Focus maintained. Well done. 🌟",
    ],
    RewardTier.UNCOMMON: [
        "Strong focus session! Bonus earned. 🪙",
        "Your effort paid off. 💪",
        "Above average performance. 🎉",
        "Productivity on point. 📈",
    ],
    RewardTier.RARE: [
        "Exceptional focus! Rare bonus unlocked. 💎",
        "High performance session. Impressive. 🔥",
        "You're operating at peak efficiency. 🏆",
        "Premium execution. 💯",
    ],
    RewardTier.EPIC: [
        "Outstanding performance! Epic reward. 🎊",
        "This is what mastery looks like. 👏",
        "Exceptional work. You've earned this. ⭐",
        "Peak productivity achieved. 💥",
    ],
    RewardTier.LEGENDARY: [
        "🏆 LEGENDARY PERFORMANCE! Top 1% focus. 🏆",
        "🎰 EXCEPTIONAL! You've hit the jackpot. 🎰",
        "🌟 RARE ACHIEVEMENT UNLOCKED. 🌟",
        "✨ OUTSTANDING. This level of focus is remarkable. ✨",
    ],
}

# Bonus items that can drop (rare)
BONUS_ITEMS = {
    RewardTier.RARE: [
        ("streak_freeze", "Streak Protection 🛡️"),
        ("double_coins_next", "2x Coins (Next Session) 💰"),
    ],
    RewardTier.EPIC: [
        ("mystery_box", "Mystery Reward 📦"),
        ("premium_unlock", "Premium Feature Unlock 🎭"),
        ("triple_coins_next", "3x Coins (Next Session) 💎"),
    ],
    RewardTier.LEGENDARY: [
        ("legendary_status", "Legendary Focus Status 🥇"),
        ("week_streak_shield", "7-Day Streak Protection 🛡️"),
        ("exclusive_badge", "Focus Master Badge 🏅"),
    ],
}


def roll_reward_tier() -> RewardTier:
    """Roll for a reward tier based on weighted probabilities."""
    tiers = list(TIER_WEIGHTS.keys())
    weights = list(TIER_WEIGHTS.values())
    return random.choices(tiers, weights=weights, k=1)[0]


def calculate_multiplier(tier: RewardTier) -> float:
    """Calculate a random multiplier within the tier's range."""
    min_mult, max_mult = MULTIPLIER_RANGES[tier]
    return round(random.uniform(min_mult, max_mult), 2)


def roll_bonus_item(tier: RewardTier) -> Optional[Tuple[str, str]]:
    """Roll for a bonus item (only available for rare+ tiers)."""
    if tier not in BONUS_ITEMS:
        return None
    
    # 30% chance to get a bonus item at eligible tiers
    if random.random() < 0.30:
        items = BONUS_ITEMS[tier]
        return random.choice(items)
    
    return None


def get_celebration_level(tier: RewardTier) -> int:
    """Get animation intensity level (1-5) based on tier."""
    levels = {
        RewardTier.COMMON: 1,
        RewardTier.UNCOMMON: 2,
        RewardTier.RARE: 3,
        RewardTier.EPIC: 4,
        RewardTier.LEGENDARY: 5,
    }
    return levels.get(tier, 1)


def calculate_mystery_reward(
    base_coins: int,
    streak_bonus: float = 0.0,
    difficulty_multiplier: float = 1.0,
    is_quiz_correct: bool = False,
) -> MysteryReward:
    """
    Calculate a mystery reward with variable dopamine-optimizing mechanics.
    
    Args:
        base_coins: Base coin reward for the chunk
        streak_bonus: Additional multiplier from streak (e.g., 0.1 for 10% bonus)
        difficulty_multiplier: Multiplier based on content difficulty
        is_quiz_correct: Whether the user answered the quiz correctly
        
    Returns:
        MysteryReward with tier, coins, and celebration details
    """
    # Roll for tier
    tier = roll_reward_tier()
    
    # Calculate multiplier
    multiplier = calculate_multiplier(tier)
    
    # Apply bonuses
    total_multiplier = multiplier * difficulty_multiplier * (1 + streak_bonus)
    if is_quiz_correct:
        total_multiplier *= 1.25  # 25% bonus for correct quiz
    
    # Calculate final coins
    final_coins = int(base_coins * total_multiplier)
    
    # Roll for bonus item
    bonus = roll_bonus_item(tier)
    bonus_item = bonus[1] if bonus else None
    
    # Get celebration message
    message = random.choice(TIER_MESSAGES[tier])
    
    # Get celebration level
    celebration_level = get_celebration_level(tier)
    
    reward = MysteryReward(
        tier=tier,
        base_coins=base_coins,
        multiplier=round(total_multiplier, 2),
        final_coins=final_coins,
        bonus_item=bonus_item,
        message=message,
        celebration_level=celebration_level,
    )
    
    logger.info(
        f"🎰 Mystery Reward: {tier.value} | {base_coins} × {total_multiplier:.2f} = {final_coins} coins"
        + (f" + {bonus_item}" if bonus_item else "")
    )
    
    return reward


def to_api_response(reward: MysteryReward) -> Dict[str, Any]:
    """Convert mystery reward to API response format."""
    return {
        "tier": reward.tier.value,
        "tier_display": reward.tier.value.upper(),
        "base_coins": reward.base_coins,
        "multiplier": reward.multiplier,
        "final_coins": reward.final_coins,
        "bonus_item": reward.bonus_item,
        "message": reward.message,
        "celebration_level": reward.celebration_level,
        "is_jackpot": reward.tier == RewardTier.LEGENDARY,
        "show_mystery_animation": reward.tier.value in ["rare", "epic", "legendary"],
    }


# Adult-focused return messages for users coming back after absence
RETURN_MESSAGES = [
    "Welcome back. Resuming where you left off is harder than starting fresh. 💪",
    "You're here. Let's make progress. 🚀",
    "Returning takes discipline. Let's get to work. 🌟",
    "Ready to continue? Your progress is waiting. 💼",
    "Back in the zone. Let's build on what you started. ✨",
    "Welcome back. Consistency over perfection. 📈",
]


def get_return_message(days_away: int = 0) -> str:
    """Get an encouraging message for returning users."""
    if days_away > 7:
        return random.choice([
            f"It's been {days_away} days. Returning after a break shows real commitment. 💪",
            "Extended break? That's okay. Progress isn't always linear. 📈",
            "Welcome back. Let's pick up where you left off. 🚀",
        ])
    elif days_away > 2:
        return random.choice([
            "A few days off, now back at it. That's how consistency works. 🎯",
            "Ready to continue? Your momentum is building. 💫",
        ])
    else:
        return random.choice(RETURN_MESSAGES)


# Low-energy acknowledgment messages
LOW_ENERGY_MESSAGES = [
    "Low energy day? Start with something manageable. 🎯",
    "Not every session needs to be intense. Small wins count. 📊",
    "Quick session today. Maintain the habit. 💼",
    "Lower the bar, keep the streak. Sustainability wins. 📈",
]


def get_low_energy_message() -> str:
    """Get an appropriate message for low-energy users."""
    return random.choice(LOW_ENERGY_MESSAGES)
