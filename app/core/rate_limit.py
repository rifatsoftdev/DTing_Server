import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request, status
from redis import Redis
from redis.exceptions import RedisError

from app.constants import ENV


_redis_client: Redis | None = None
_redis_failed = False
_memory_hits: dict[str, Deque[float]] = defaultdict(deque)


def _get_redis_client() -> Redis | None:
    global _redis_client, _redis_failed

    if _redis_failed:
        return None

    if _redis_client is None:
        try:
            _redis_client = Redis.from_url(ENV.REDIS_URL, decode_responses=True)
            _redis_client.ping()
        except RedisError:
            _redis_failed = True
            return None

    return _redis_client


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()

    return request.client.host if request.client else "unknown"


def _raise_rate_limit_error(retry_after: int, detail: str = "Too many requests. Please try again later.") -> None:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail,
        headers={"Retry-After": str(max(retry_after, 1))},
    )


def check_rate_limit(request: Request, key_prefix: str, limit: int, window_seconds: int, detail: str = "Too many requests. Please try again later.") -> None:
    key = f"rate_limit:{key_prefix}:{_client_ip(request)}"
    redis_client = _get_redis_client()

    if redis_client:
        try:
            current_count = redis_client.incr(key)
            if current_count == 1:
                redis_client.expire(key, window_seconds)

            if current_count > limit:
                retry_after = redis_client.ttl(key)
                _raise_rate_limit_error(retry_after, detail=detail)
            return
        except RedisError:
            pass

    now = time.time()
    hits = _memory_hits[key]

    while hits and hits[0] <= now - window_seconds:
        hits.popleft()

    if len(hits) >= limit:
        retry_after = int(window_seconds - (now - hits[0]))
        _raise_rate_limit_error(retry_after, detail=detail)

    hits.append(now)


def signin_rate_limit(request: Request) -> None:
    check_rate_limit(
        request=request,
        key_prefix="signin",
        limit=30,
        window_seconds=60 * 60,
        detail="Too many login attempts. Please try again later.",
    )

def signup_rate_limit(request: Request) -> None:
    check_rate_limit(
        request=request,
        key_prefix="signup",
        limit=10,
        window_seconds=60 * 60,
        detail="Too many signup attempts. Please try again later.",
    )

def settings_rate_limit(request: Request) -> None:
    check_rate_limit(
        request=request,
        key_prefix="settings_update",
        limit=10,
        window_seconds=60 * 60,
        detail="Too many settings updates. Please try again later.",
    )
