import asyncio
import json

from fastapi import WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.constants import ENV, AnsiColor
from app.core.rate_limit import _get_redis_client
from app.model import UserTable
from services.auth.user_verification import UserVerificationService


# user_id -> websocket
notification_users: dict[str, WebSocket] = {}
_async_redis_client: aioredis.Redis | None = None



class NotifyWebSocket:
    def __init__(
        self,
        db: Session = None,
        background_tasks: BackgroundTasks = None,
        request: Request = None,
        authorization: str = None
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization

    def _online_key(self, user_id: str) -> str:
        return f"notifications:online:{user_id}"

    def _channel_name(self, user_id: str) -> str:
        return f"notifications:{user_id}"

    def _get_redis_client(self) -> aioredis.Redis | None:
        global _async_redis_client
        if _async_redis_client is None:
            try:
                _async_redis_client = aioredis.from_url(ENV.REDIS_URL, decode_responses=True)
            except RedisError:
                _async_redis_client = None
        return _async_redis_client

    async def _set_online_user(self, user_id: str) -> None:
        redis_client = self._get_redis_client()
        if not redis_client:
            return

        try:
            await redis_client.set(self._online_key(user_id), "1", ex=300)
        except RedisError:
            pass

    async def _clear_online_user(self, user_id: str) -> None:
        redis_client = self._get_redis_client()
        if not redis_client:
            return

        try:
            await redis_client.delete(self._online_key(user_id))
        except RedisError:
            pass

    async def _is_online_user(self, user_id: str) -> bool:
        if user_id in notification_users:
            return True

        redis_client = self._get_redis_client()
        if not redis_client:
            return False

        try:
            return await redis_client.exists(self._online_key(user_id)) > 0
        except RedisError:
            return False

    async def _redis_subscriber(self, websocket: WebSocket, user_id: str) -> None:
        redis_client = self._get_redis_client()
        if not redis_client:
            return

        channel = self._channel_name(user_id)
        pubsub = redis_client.pubsub()

        try:
            await pubsub.subscribe(channel)

            async for message in pubsub.listen():
                if message is None:
                    continue
                if message.get("type") != "message":
                    continue

                payload = message.get("data")
                if isinstance(payload, bytes):
                    payload = payload.decode("utf-8")

                try:
                    data = json.loads(payload)
                except (TypeError, ValueError):
                    continue

                try:
                    await websocket.send_json(data)
                except Exception:
                    break

        except Exception:
            pass

        finally:
            try:
                await pubsub.unsubscribe(channel)
            except Exception:
                pass

            try:
                await pubsub.close()
            except Exception:
                pass
    
    async def check_online_user(self, user_id: str) -> bool:
        return await self._is_online_user(user_id)


    async def notify_ws(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        
        userVerificationService = UserVerificationService(
            db=self.db,
            background_tasks=self.background_tasks,
            request=self.request,
            authorization=self.authorization
        )

        user: UserTable = userVerificationService.verify_user_authorization()

        
        notification_users[user_id] = websocket
        await self._set_online_user(user_id)

        print(f"{AnsiColor.GREEN}INFO{AnsiColor.RESET}:     {user.user_id} connected")

        subscription_task = asyncio.create_task(self._redis_subscriber(websocket, user_id))

        try:
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            pass

        finally:
            subscription_task.cancel()

            try:
                await subscription_task
            except asyncio.CancelledError:
                pass

            notification_users.pop(user_id, None)
            await self._clear_online_user(user_id)

            print(f"{AnsiColor.BLUE}INFO{AnsiColor.RESET}:     {user_id} disconnected")

   

    async def send_notification(self, user_id: str, title: str, body: str, payload: dict = None):
        if payload is None:
            payload = {}

        notification = {
            "title": title,
            "body": body,
            "payload": payload
        }

        redis_client = self._get_redis_client()

        if redis_client:
            try:
                await redis_client.publish(
                    self._channel_name(user_id),
                    json.dumps(notification)
                )
                return
            except RedisError:
                pass

        ws = notification_users.get(user_id)

        if ws:
            try:
                await ws.send_json(notification)
            except Exception:
                notification_users.pop(user_id, None)

    

class WebsocketPushManager:
    pass




# ==============================================================================
# ==============================================================================
