"""
Gamification API routes.
Handles Focus Coins economy, streak management, and shop purchases.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import User
from app.services.adhd_features import adhd_features

logger = logging.getLogger("GamificationAPI")
router = APIRouter()


# ============== SHOP ITEMS (Static data for now) ==============
SHOP_ITEMS = [
    {
        "id": "avatar_cosmic",
        "name": "Cosmic Avatar",
        "type": "avatar",
        "rarity": "Rare",
        "price": 500,
        "description": "A mystical cosmic avatar that shows your dedication to learning",
        "image_url": "/assets/shop/avatars/cosmic.png"
    },
    {
        "id": "avatar_pixel",
        "name": "Pixel Hero Avatar",
        "type": "avatar",
        "rarity": "Common",
        "price": 200,
        "description": "A retro pixel art avatar for the classic gamer in you",
        "image_url": "/assets/shop/avatars/pixel.png"
    },
    {
        "id": "pet_phoenix_egg",
        "name": "Phoenix Egg",
        "type": "pet",
        "rarity": "Epic",
        "price": 300,
        "description": "A mysterious egg that hatches after completing 10 sprints",
        "image_url": "/assets/shop/pets/phoenix_egg.png"
    },
    {
        "id": "pet_turtle_egg",
        "name": "Bio-Turtle Egg",
        "type": "pet",
        "rarity": "Legendary",
        "price": 800,
        "description": "Contains a rare Bio-Luminescent Turtle",
        "image_url": "/assets/shop/pets/turtle_egg.png"
    },
    {
        "id": "pet_cat_egg",
        "name": "Glitch Cat Egg",
        "type": "pet",
        "rarity": "Epic",
        "price": 650,
        "description": "A digital egg containing a Pixel Glitch Cat",
        "image_url": "/assets/shop/pets/cat_egg.png"
    },
    {
        "id": "badge_focus_master",
        "name": "Focus Master Badge",
        "type": "badge",
        "rarity": "Rare",
        "price": 400,
        "description": "Display your mastery of focus with this prestigious badge",
        "image_url": "/assets/shop/badges/focus_master.png"
    },
    {
        "id": "card_pack_basic",
        "name": "Basic Card Pack",
        "type": "card_pack",
        "rarity": "Common",
        "price": 100,
        "description": "Contains 3 random knowledge cards",
        "image_url": "/assets/shop/packs/basic.png"
    },
    {
        "id": "card_pack_premium",
        "name": "Premium Card Pack",
        "type": "card_pack",
        "rarity": "Rare",
        "price": 250,
        "description": "Contains 5 cards with guaranteed 1 Rare or better",
        "image_url": "/assets/shop/packs/premium.png"
    }
]


@router.get("/user/coins")
async def get_user_coins(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's Focus Coins balance and gamification stats.
    """
    streak_status = adhd_features.check_streak_status(
        last_activity_date=current_user.last_activity_date,
        current_streak=current_user.current_streak or 0,
        focus_coins=current_user.focus_coins or 0
    )
    
    return {
        "focus_coins": current_user.focus_coins or 0,
        "current_streak": current_user.current_streak or 0,
        "longest_streak": current_user.longest_streak or 0,
        "total_sprints_completed": current_user.total_sprints_completed or 0,
        "streak_status": streak_status
    }


@router.post("/user/streak/freeze")
async def freeze_streak(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Use Focus Coins to freeze streak for one day.
    Costs 50 coins.
    """
    result = adhd_features.freeze_streak(
        focus_coins=current_user.focus_coins or 0,
        current_streak=current_user.current_streak or 0
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    # Deduct coins
    current_user.focus_coins = result["new_balance"]
    db.commit()
    
    logger.info(f"❄️ User {current_user.id} froze streak. New balance: {result['new_balance']}")
    
    return result


@router.get("/user/milestones")
async def get_user_milestones(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's achieved and upcoming milestones.
    """
    total_sprints = current_user.total_sprints_completed or 0
    milestones = adhd_features.MILESTONES
    
    achieved = [m for m in milestones if total_sprints >= m]
    upcoming = [m for m in milestones if total_sprints < m]
    
    next_milestone = upcoming[0] if upcoming else None
    sprints_to_next = next_milestone - total_sprints if next_milestone else 0
    
    return {
        "total_sprints": total_sprints,
        "achieved_milestones": achieved,
        "next_milestone": next_milestone,
        "sprints_to_next": sprints_to_next,
        "progress_percentage": (total_sprints / next_milestone * 100) if next_milestone else 100
    }


@router.get("/shop/items")
async def get_shop_items(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available shop items.
    """
    user_coins = current_user.focus_coins or 0
    
    # Add 'affordable' flag to each item
    items_with_status = []
    for item in SHOP_ITEMS:
        items_with_status.append({
            **item,
            "affordable": user_coins >= item["price"]
        })
    
    return {
        "items": items_with_status,
        "user_balance": user_coins
    }


@router.post("/shop/purchase/{item_id}")
async def purchase_item(
    item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Purchase an item from the shop using Focus Coins.
    Persists purchase to user inventory.
    """
    from app.models.models import UserInventory
    
    # Find the item
    item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    user_coins = current_user.focus_coins or 0
    
    if user_coins < item["price"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough coins! Need {item['price']}, you have {user_coins}."
        )
    
    # Check if already owned (for non-consumables)
    if item["type"] not in ["card_pack"]:  # Card packs can be bought multiple times
        existing = db.query(UserInventory).filter(
            UserInventory.user_id == current_user.id,
            UserInventory.item_id == item_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already own {item['name']}!"
            )
    
    # Deduct coins
    current_user.focus_coins = user_coins - item["price"]
    
    # Add to inventory
    inventory_item = UserInventory(
        user_id=current_user.id,
        item_id=item_id,
        item_type=item["type"],
        item_name=item["name"]
    )
    db.add(inventory_item)
    db.commit()
    
    logger.info(f"🛒 User {current_user.id} purchased {item['name']} for {item['price']} coins")
    
    return {
        "success": True,
        "message": f"Successfully purchased {item['name']}!",
        "item": item,
        "coins_spent": item["price"],
        "new_balance": current_user.focus_coins
    }


@router.get("/user/inventory")
async def get_user_inventory(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all items in user's inventory.
    """
    from app.models.models import UserInventory
    
    items = db.query(UserInventory).filter(
        UserInventory.user_id == current_user.id
    ).order_by(UserInventory.purchased_at.desc()).all()
    
    inventory = []
    for item in items:
        # Find full item details from shop
        shop_item = next((i for i in SHOP_ITEMS if i["id"] == item.item_id), None)
        inventory.append({
            "id": item.id,
            "item_id": item.item_id,
            "item_type": item.item_type,
            "item_name": item.item_name,
            "purchased_at": item.purchased_at.isoformat(),
            "is_equipped": item.is_equipped,
            "details": shop_item
        })
    
    # Group by type
    by_type = {}
    for item in inventory:
        item_type = item["item_type"]
        if item_type not in by_type:
            by_type[item_type] = []
        by_type[item_type].append(item)
    
    return {
        "items": inventory,
        "by_type": by_type,
        "total_items": len(inventory)
    }


@router.post("/user/inventory/{item_id}/equip")
async def equip_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Equip an item from inventory (avatars, pets).
    """
    from app.models.models import UserInventory
    
    item = db.query(UserInventory).filter(
        UserInventory.id == item_id,
        UserInventory.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    
    if item.item_type not in ["avatar", "pet"]:
        raise HTTPException(status_code=400, detail="Only avatars and pets can be equipped")
    
    # Unequip other items of same type
    db.query(UserInventory).filter(
        UserInventory.user_id == current_user.id,
        UserInventory.item_type == item.item_type,
        UserInventory.is_equipped == True
    ).update({"is_equipped": False})
    
    # Equip this item
    item.is_equipped = True
    db.commit()
    
    return {"success": True, "message": f"Equipped {item.item_name}!"}


@router.get("/leaderboard")
async def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get top users by total sprints completed.
    """
    # Get top 10 users by sprints
    top_users = db.query(User).order_by(
        User.total_sprints_completed.desc()
    ).limit(10).all()
    
    leaderboard = []
    for rank, user in enumerate(top_users, 1):
        leaderboard.append({
            "rank": rank,
            "name": user.full_name or user.email.split("@")[0],
            "sprints": user.total_sprints_completed or 0,
            "streak": user.current_streak or 0,
            "is_current_user": user.id == current_user.id
        })
    
    # Find current user's rank if not in top 10
    current_user_rank = None
    for i, entry in enumerate(leaderboard):
        if entry["is_current_user"]:
            current_user_rank = i + 1
            break
    
    if current_user_rank is None:
        # Count users with more sprints
        users_above = db.query(User).filter(
            User.total_sprints_completed > (current_user.total_sprints_completed or 0)
        ).count()
        current_user_rank = users_above + 1
    
    return {
        "leaderboard": leaderboard,
        "current_user_rank": current_user_rank,
        "current_user_sprints": current_user.total_sprints_completed or 0
    }
