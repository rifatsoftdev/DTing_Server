from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.constants.colors import AnsiColor




notyfy_router = APIRouter()

# user_id -> websocket
notification_users = {}



# ======================================
# WebSocket endpoint for notifications
# ======================================
@notyfy_router.websocket("/notify/{user_id}")
async def notify_ws(websocket: WebSocket, user_id: str):
    # veryfy = Veryfy()
    # if not veryfy.verify_user(user_id):
    #     await websocket.close(code=403)
    #     return

    # Debug only: ignore auth
    await websocket.accept()
    notification_users[user_id] = websocket
    # print(f"{user_id} connected (debug bypass)")


    try:
        while True:
            await websocket.receive_text()  # connection alive
    except WebSocketDisconnect:
        notification_users.pop(user_id, None)
        print(f"{AnsiColor.GREEN}INFO{AnsiColor.RESET}:     {user_id} disconnected")




# ======================================
# Check online user function
# ======================================
def check_online_user(user_id: str) -> bool:
    return user_id in notification_users




# ======================================
# Notification sending function
# ======================================
# Function to send notification to a specific user
async def send_notification(user_id: str, type: str, title: str, body: str, img_url: str = None):
    ws = notification_users.get(user_id)
    if ws:
        await ws.send_json({
            "type": type,
            "title": title,
            "body": body,
            "img_url": img_url
        })