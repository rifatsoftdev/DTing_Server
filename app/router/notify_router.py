from fastapi import APIRouter, WebSocket

from services.notification.websocket_push_manager import NotifyWebSocket


notyfy_router = APIRouter()



# ==============================================================================

@notyfy_router.websocket("/notify/{user_id}")
async def notify_ws(websocket: WebSocket, user_id: str):
    notify_websocket = NotifyWebSocket()
    await notify_websocket.notify_ws(websocket, user_id)




# ==============================================================================
# ==============================================================================
