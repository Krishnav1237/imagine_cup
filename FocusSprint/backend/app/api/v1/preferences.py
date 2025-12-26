"""
User Preferences API
Handles age-adaptive preferences and feature settings.
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import User

logger = logging.getLogger("PreferencesAPI")
router = APIRouter()


# ============ Schemas ============

class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    ageGroup: Optional[str] = None
    focusStyle: Optional[str] = None
    sessionLength: Optional[str] = None
    motivationStyle: Optional[str] = None
    
    preferredDisplayMode: Optional[str] = None
    visualAidsEnabled: Optional[bool] = None
    highContrastMode: Optional[bool] = None
    largeTextMode: Optional[bool] = None
    reducedMotion: Optional[bool] = None
    
    soundEffectsEnabled: Optional[bool] = None
    notificationSoundsEnabled: Optional[bool] = None
    textToSpeechEnabled: Optional[bool] = None
    
    hyperfocusGuardEnabled: Optional[bool] = None
    attentionTrackingEnabled: Optional[bool] = None
    frustrationDetectionEnabled: Optional[bool] = None
    microCommitmentEnabled: Optional[bool] = None
    
    showCoinsAndRewards: Optional[bool] = None
    showStreaks: Optional[bool] = None
    showLeaderboards: Optional[bool] = None
    mysteryRewardsEnabled: Optional[bool] = None


class OnboardingData(BaseModel):
    """Schema for onboarding completion."""
    ageGroup: str
    focusStyle: str
    sessionLength: str


# ============ Default Preferences by Age Group ============

AGE_GROUP_DEFAULTS = {
    "teen": {
        "focusStyle": "gamified",
        "sessionLength": "short",
        "motivationStyle": "encouraging",
        "preferredDisplayMode": "visual",
        "visualAidsEnabled": True,
        "soundEffectsEnabled": True,
        "showCoinsAndRewards": True,
        "showStreaks": True,
        "showLeaderboards": True,
        "mysteryRewardsEnabled": True,
    },
    "young-adult": {
        "focusStyle": "gamified",
        "sessionLength": "standard",
        "motivationStyle": "achievement",
        "preferredDisplayMode": "visual",
        "visualAidsEnabled": True,
        "soundEffectsEnabled": True,
        "showCoinsAndRewards": True,
        "showStreaks": True,
        "showLeaderboards": False,
        "mysteryRewardsEnabled": True,
    },
    "professional": {
        "focusStyle": "data-driven",
        "sessionLength": "standard",
        "motivationStyle": "neutral",
        "preferredDisplayMode": "text",
        "visualAidsEnabled": True,
        "soundEffectsEnabled": False,
        "showCoinsAndRewards": False,
        "showStreaks": True,
        "showLeaderboards": False,
        "mysteryRewardsEnabled": False,
    },
    "senior": {
        "focusStyle": "minimal",
        "sessionLength": "short",
        "motivationStyle": "encouraging",
        "preferredDisplayMode": "text",
        "visualAidsEnabled": True,
        "highContrastMode": True,
        "largeTextMode": True,
        "reducedMotion": True,
        "soundEffectsEnabled": False,
        "showCoinsAndRewards": False,
        "showStreaks": False,
        "showLeaderboards": False,
        "mysteryRewardsEnabled": False,
    },
}

DEFAULT_PREFERENCES = {
    "ageGroup": "young-adult",
    "focusStyle": "gamified",
    "sessionLength": "standard",
    "motivationStyle": "encouraging",
    "preferredDisplayMode": "visual",
    "visualAidsEnabled": True,
    "highContrastMode": False,
    "largeTextMode": False,
    "reducedMotion": False,
    "soundEffectsEnabled": True,
    "notificationSoundsEnabled": True,
    "textToSpeechEnabled": False,
    "hyperfocusGuardEnabled": True,
    "attentionTrackingEnabled": True,
    "frustrationDetectionEnabled": True,
    "microCommitmentEnabled": True,
    "showCoinsAndRewards": True,
    "showStreaks": True,
    "showLeaderboards": False,
    "mysteryRewardsEnabled": True,
}


# ============ Endpoints ============

@router.get("/")
async def get_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current user's preferences."""
    prefs = current_user.preferences or {}
    
    # Merge with defaults
    return {
        **DEFAULT_PREFERENCES,
        **prefs,
        "onboarding_completed": current_user.onboarding_completed or False,
    }


@router.patch("/")
async def update_preferences(
    updates: PreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update user preferences."""
    current_prefs = current_user.preferences or {}
    
    # Merge updates (only non-None values)
    update_dict = updates.dict(exclude_none=True)
    new_prefs = {**current_prefs, **update_dict}
    
    current_user.preferences = new_prefs
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"✅ Updated preferences for user {current_user.id}")
    
    return {
        **DEFAULT_PREFERENCES,
        **new_prefs,
        "onboarding_completed": current_user.onboarding_completed or False,
    }


@router.post("/onboarding")
async def complete_onboarding(
    data: OnboardingData,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Complete onboarding and set initial preferences based on age group."""
    
    # Get age-specific defaults
    age_defaults = AGE_GROUP_DEFAULTS.get(data.ageGroup, {})
    
    # Merge with user selections
    new_prefs = {
        **DEFAULT_PREFERENCES,
        **age_defaults,
        "ageGroup": data.ageGroup,
        "focusStyle": data.focusStyle,
        "sessionLength": data.sessionLength,
    }
    
    current_user.preferences = new_prefs
    current_user.onboarding_completed = True
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"✅ Onboarding completed for user {current_user.id} (age group: {data.ageGroup})")
    
    return {
        "status": "success",
        "message": "Onboarding completed",
        "preferences": new_prefs,
    }


@router.post("/reset")
async def reset_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Reset preferences to defaults."""
    current_user.preferences = DEFAULT_PREFERENCES.copy()
    db.commit()
    
    logger.info(f"✅ Reset preferences for user {current_user.id}")
    
    return {
        "status": "success",
        "message": "Preferences reset to defaults",
        "preferences": DEFAULT_PREFERENCES,
    }


@router.get("/age-defaults/{age_group}")
async def get_age_defaults(age_group: str) -> Dict[str, Any]:
    """Get default preferences for a specific age group (public endpoint for onboarding)."""
    if age_group not in AGE_GROUP_DEFAULTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid age group. Must be one of: {list(AGE_GROUP_DEFAULTS.keys())}"
        )
    
    return {
        "ageGroup": age_group,
        "defaults": {**DEFAULT_PREFERENCES, **AGE_GROUP_DEFAULTS[age_group]},
    }
