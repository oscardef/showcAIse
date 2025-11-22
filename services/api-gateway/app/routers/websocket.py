from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
import sys
sys.path.append('/app')

from shared.messaging import redis_client

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time analysis updates."""
    await manager.connect(session_id, websocket)
    
    try:
        # Subscribe to Redis pub/sub for this session
        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"session:{session_id}:updates")
        
        while True:
            # Check for updates from Redis
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                await manager.send_message(session_id, data)
            
            # Small delay to prevent busy loop
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        pubsub.close()
    except Exception as e:
        manager.disconnect(session_id)
        pubsub.close()
