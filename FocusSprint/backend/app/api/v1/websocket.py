"""
WebSocket API for real-time content status updates.
Replaces polling with instant push notifications.
"""
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from jose import jwt, JWTError

from app.config import settings

logger = logging.getLogger("WebSocketAPI")
router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections per user.
    Allows broadcasting to specific users.
    """
    
    def __init__(self):
        # Map user_id -> set of active WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept connection and add to user's connection set."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"🔌 WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove connection from user's set."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"🔌 WebSocket disconnected for user {user_id}")
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to all connections for a specific user."""
        if user_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                disconnected.add(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            self.active_connections[user_id].discard(conn)
    
    async def broadcast_content_update(self, user_id: int, content_id: int, status: str, stage: str = None):
        """Broadcast content processing status update to user."""
        await self.send_to_user(user_id, {
            "type": "content_status",
            "content_id": content_id,
            "status": status,
            "stage": stage
        })


# Global connection manager
manager = ConnectionManager()


def verify_ws_token(token: str) -> int:
    """
    Verify JWT token from WebSocket query param.
    Returns user_id if valid, raises exception otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Return a placeholder user_id for now
        # In production, look up user by email
        return hash(email) % 10000000  # Simple hash for demo
        
    except JWTError as e:
        logger.warning(f"WebSocket token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.websocket("/content-status")
async def websocket_content_status(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time content status updates.
    
    Connect with: ws://localhost:8000/ws/content-status?token=<jwt_token>
    
    Receives messages in format:
    {
        "type": "content_status",
        "content_id": 123,
        "status": "processing",
        "stage": "TRANSCRIBING"
    }
    """
    try:
        user_id = verify_ws_token(token)
    except HTTPException:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Real-time updates enabled"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for any incoming messages (ping, etc.)
                data = await websocket.receive_text()
                
                # Handle ping/pong for keep-alive
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, user_id)


# Export manager for use in other modules
def get_ws_manager() -> ConnectionManager:
    """Get the global WebSocket connection manager."""
    return manager
