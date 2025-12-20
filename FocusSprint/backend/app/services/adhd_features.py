"""
ADHD-Focused Feature Service.
Provides dopamine-friendly rewards, break reminders, streak protection, and milestone celebrations.
Designed specifically for ADHD users to make the learning experience engaging and sustainable.
"""
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

logger = logging.getLogger("ADHDFeatures")


class ADHDFeatureService:
    """
    Core service for ADHD-friendly features.
    Implements dopamine-optimized reward systems and focus management.
    """
    
    # Milestone thresholds for celebrations
    MILESTONES = [10, 25, 50, 100, 250, 500, 1000]
    
    # Break reminder thresholds (in seconds)
    POMODORO_BREAK_THRESHOLD = 25 * 60  # 25 minutes - suggest break
    HYPERFOCUS_WARNING_THRESHOLD = 45 * 60  # 45 minutes - warn about hyperfocus
    MANDATORY_BREAK_THRESHOLD = 60 * 60  # 60 minutes - strongly recommend break
    
    # Reward configuration
    BASE_COINS = 50
    PERFECT_FOCUS_BONUS = 25  # 90%+ focus
    GOOD_FOCUS_BONUS = 10  # 75%+ focus
    QUIZ_CORRECT_BONUS = 10
    STREAK_MULTIPLIER_THRESHOLD = 3  # Days needed for 2x multiplier
    RANDOM_BONUS_MIN = 5
    RANDOM_BONUS_MAX = 15
    
    # Streak protection
    STREAK_FREEZE_COST = 50  # Coins to freeze streak for 1 day
    
    def calculate_reward(
        self,
        focus_percentage: float,
        current_streak: int,
        quiz_score: float,
        time_spent_seconds: int
    ) -> Dict[str, Any]:
        """
        Calculate dopamine-friendly rewards with variable bonuses.
        
        Returns detailed breakdown for frontend celebration animations.
        """
        breakdown = {
            "base_coins": self.BASE_COINS,
            "focus_bonus": 0,
            "quiz_bonus": 0,
            "streak_multiplier": 1,
            "random_bonus": 0,
            "total_coins": 0,
            "celebration_level": "standard",  # standard, good, excellent, perfect
            "messages": []
        }
        
        # Focus bonus
        if focus_percentage >= 90:
            breakdown["focus_bonus"] = self.PERFECT_FOCUS_BONUS
            breakdown["celebration_level"] = "perfect"
            breakdown["messages"].append("🎯 Perfect focus! +25 bonus coins")
        elif focus_percentage >= 75:
            breakdown["focus_bonus"] = self.GOOD_FOCUS_BONUS
            breakdown["celebration_level"] = "excellent"
            breakdown["messages"].append("✨ Great focus! +10 bonus coins")
        elif focus_percentage >= 60:
            breakdown["celebration_level"] = "good"
        
        # Quiz bonus
        if quiz_score >= 80:
            breakdown["quiz_bonus"] = self.QUIZ_CORRECT_BONUS
            breakdown["messages"].append("🧠 Quiz mastery! +10 bonus coins")
        
        # Streak multiplier (dopamine boost for consistency)
        if current_streak >= self.STREAK_MULTIPLIER_THRESHOLD:
            breakdown["streak_multiplier"] = 2
            breakdown["messages"].append(f"🔥 {current_streak} day streak! 2x multiplier!")
        
        # Random bonus (variable rewards for dopamine)
        # Higher chance of bonus when focus is good
        if random.random() < (focus_percentage / 100) * 0.5:
            breakdown["random_bonus"] = random.randint(
                self.RANDOM_BONUS_MIN, 
                self.RANDOM_BONUS_MAX
            )
            breakdown["messages"].append(f"🎲 Lucky bonus! +{breakdown['random_bonus']} coins")
        
        # Calculate total
        subtotal = (
            breakdown["base_coins"] +
            breakdown["focus_bonus"] +
            breakdown["quiz_bonus"] +
            breakdown["random_bonus"]
        )
        breakdown["total_coins"] = subtotal * breakdown["streak_multiplier"]
        
        logger.info(f"💰 Reward calculated: {breakdown['total_coins']} coins (base={breakdown['base_coins']}, focus={breakdown['focus_bonus']}, quiz={breakdown['quiz_bonus']}, random={breakdown['random_bonus']}, multiplier={breakdown['streak_multiplier']}x)")
        
        return breakdown
    
    def should_suggest_break(self, session_duration_seconds: int) -> Dict[str, Any]:
        """
        Determine if user should take a break based on session duration.
        ADHD brains need structured breaks to maintain sustainability.
        
        Returns break suggestion with appropriate messaging.
        """
        result = {
            "should_break": False,
            "break_type": None,  # "pomodoro", "hyperfocus_warning", "mandatory"
            "message": None,
            "suggested_break_minutes": 0,
            "urgency": "low"  # low, medium, high
        }
        
        if session_duration_seconds >= self.MANDATORY_BREAK_THRESHOLD:
            result.update({
                "should_break": True,
                "break_type": "mandatory",
                "message": "🛑 You've been focused for over an hour! Your brain needs a longer break to stay sharp.",
                "suggested_break_minutes": 15,
                "urgency": "high"
            })
        elif session_duration_seconds >= self.HYPERFOCUS_WARNING_THRESHOLD:
            result.update({
                "should_break": True,
                "break_type": "hyperfocus_warning",
                "message": "⚠️ Hyperfocus detected! Amazing focus, but consider a short break to prevent burnout.",
                "suggested_break_minutes": 10,
                "urgency": "medium"
            })
        elif session_duration_seconds >= self.POMODORO_BREAK_THRESHOLD:
            result.update({
                "should_break": True,
                "break_type": "pomodoro",
                "message": "☕ Great sprint! Take a quick 5-minute break to recharge.",
                "suggested_break_minutes": 5,
                "urgency": "low"
            })
        
        return result
    
    def check_streak_status(
        self,
        last_activity_date: Optional[datetime],
        current_streak: int,
        focus_coins: int
    ) -> Dict[str, Any]:
        """
        Check user's streak status and determine if protection is needed.
        
        Returns streak information with protection options.
        """
        today = datetime.utcnow().date()
        
        result = {
            "current_streak": current_streak,
            "streak_status": "active",  # active, at_risk, broken, protected
            "days_since_activity": 0,
            "can_freeze": False,
            "freeze_cost": self.STREAK_FREEZE_COST,
            "message": None
        }
        
        if last_activity_date is None:
            result["streak_status"] = "new_user"
            result["message"] = "🌟 Welcome! Start your first sprint to begin your streak!"
            return result
        
        last_date = last_activity_date.date()
        days_diff = (today - last_date).days
        result["days_since_activity"] = days_diff
        
        if days_diff == 0:
            # Activity today
            result["streak_status"] = "active"
            result["message"] = f"🔥 Streak active! {current_streak} days strong!"
        elif days_diff == 1:
            # Missed yesterday - streak at risk
            result["streak_status"] = "at_risk"
            result["can_freeze"] = focus_coins >= self.STREAK_FREEZE_COST
            result["message"] = f"⚠️ Complete a sprint today to keep your {current_streak}-day streak!"
        else:
            # Streak is broken
            result["streak_status"] = "broken"
            result["message"] = f"💔 Your {current_streak}-day streak was reset. Start fresh today!"
        
        return result
    
    def update_streak(
        self,
        last_activity_date: Optional[datetime],
        current_streak: int,
        longest_streak: int
    ) -> Dict[str, Any]:
        """
        Update streak based on activity date.
        Called when user completes a sprint.
        
        Returns new streak values.
        """
        today = datetime.utcnow()
        today_date = today.date()
        
        if last_activity_date is None:
            # First activity ever
            return {
                "new_streak": 1,
                "new_longest_streak": max(1, longest_streak),
                "last_activity_date": today,
                "streak_increased": True
            }
        
        last_date = last_activity_date.date()
        days_diff = (today_date - last_date).days
        
        if days_diff == 0:
            # Already active today - no change
            return {
                "new_streak": current_streak,
                "new_longest_streak": longest_streak,
                "last_activity_date": today,
                "streak_increased": False
            }
        elif days_diff == 1:
            # Consecutive day - increase streak
            new_streak = current_streak + 1
            return {
                "new_streak": new_streak,
                "new_longest_streak": max(new_streak, longest_streak),
                "last_activity_date": today,
                "streak_increased": True
            }
        else:
            # Streak broken - start fresh
            return {
                "new_streak": 1,
                "new_longest_streak": longest_streak,
                "last_activity_date": today,
                "streak_increased": True,
                "streak_reset": True
            }
    
    def freeze_streak(
        self,
        focus_coins: int,
        current_streak: int
    ) -> Dict[str, Any]:
        """
        Attempt to freeze streak for one day using focus coins.
        
        Returns result of freeze attempt.
        """
        if focus_coins < self.STREAK_FREEZE_COST:
            return {
                "success": False,
                "message": f"Not enough coins! Need {self.STREAK_FREEZE_COST}, you have {focus_coins}.",
                "coins_deducted": 0
            }
        
        return {
            "success": True,
            "message": f"❄️ Streak frozen! Your {current_streak}-day streak is protected for today.",
            "coins_deducted": self.STREAK_FREEZE_COST,
            "new_balance": focus_coins - self.STREAK_FREEZE_COST
        }
    
    def get_milestone_celebration(self, total_sprints: int) -> Optional[Dict[str, Any]]:
        """
        Check if user has hit a milestone and return celebration data.
        
        Milestones trigger special UI celebrations for dopamine boost.
        """
        if total_sprints in self.MILESTONES:
            milestone_rewards = {
                10: {"coins": 100, "badge": "🌱 Sprout", "message": "First milestone! You're growing!"},
                25: {"coins": 200, "badge": "🌿 Sapling", "message": "Quarter century of sprints!"},
                50: {"coins": 300, "badge": "🌳 Tree", "message": "Fifty sprints strong!"},
                100: {"coins": 500, "badge": "🏆 Century", "message": "ONE HUNDRED sprints! Legendary!"},
                250: {"coins": 750, "badge": "⭐ Star", "message": "250 sprints! You're a focus star!"},
                500: {"coins": 1000, "badge": "💎 Diamond", "message": "500 sprints! Absolutely incredible!"},
                1000: {"coins": 2000, "badge": "👑 Legend", "message": "1000 SPRINTS! You are a LEGEND!"}
            }
            
            reward = milestone_rewards.get(total_sprints, {
                "coins": total_sprints,
                "badge": "🎉 Achiever",
                "message": f"Milestone: {total_sprints} sprints!"
            })
            
            return {
                "milestone": total_sprints,
                "celebration": True,
                **reward
            }
        
        return None
    
    def get_encouragement_message(self, focus_percentage: float, streak: int) -> str:
        """
        Get ADHD-friendly encouragement message based on performance.
        Focuses on progress, not perfection.
        """
        messages = {
            "low_focus": [
                "Every sprint counts! Focus is a skill that grows with practice. 🌱",
                "Showing up is the hardest part - you did it! 💪",
                "Progress over perfection. You're building new pathways! 🧠"
            ],
            "medium_focus": [
                "Solid focus! Your brain is getting stronger! 💪",
                "Nice work staying engaged! Keep building momentum! 🚀",
                "You're doing great - consistency beats intensity! ⭐"
            ],
            "high_focus": [
                "Incredible focus! You're in THE ZONE! 🔥",
                "Your brain is firing on all cylinders! Amazing! ⚡",
                "Peak performance! This is what progress looks like! 🏆"
            ]
        }
        
        if focus_percentage >= 80:
            category = "high_focus"
        elif focus_percentage >= 50:
            category = "medium_focus"
        else:
            category = "low_focus"
        
        return random.choice(messages[category])


# Global service instance
adhd_features = ADHDFeatureService()
