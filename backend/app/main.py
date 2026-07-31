from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.routers import accommodations
from app.config import settings


def _real_client_ip(request: Request) -> str:
    # When deployed behind Azure API Management / App Service, the real client IP
    # arrives in X-Forwarded-For only from the trusted gateway peer.
    # We read XFF only when the direct peer matches a trusted proxy CIDR;
    # otherwise we fall back to the direct peer address to prevent IP spoofing.
    trusted_proxies = set(settings.trusted_proxy_ips)
    peer = request.client.host if request.client else "unknown"
    if peer in trusted_proxies:
        xff = request.headers.get("X-Forwarded-For", "")
        leftmost = xff.split(",")[0].strip()
        if leftmost:
            return leftmost
    return peer


limiter = Limiter(key_func=_real_client_ip)

app = FastAPI(title="Accommodation Search API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.include_router(accommodations.router, prefix="/api")


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get("/health")
async def health():
    return {"status": "ok"}
