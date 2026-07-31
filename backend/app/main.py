import ipaddress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.routers import accommodations
from app.config import settings


def _is_trusted(ip_str: str, networks: list) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
        return any(addr in net for net in networks)
    except ValueError:
        return False


def _real_client_ip(request: Request) -> str:
    # Walk X-Forwarded-For right-to-left: the real client IP is the rightmost
    # entry that is NOT one of our trusted proxies.  Attackers can prepend
    # arbitrary IPs on the left; they cannot forge entries appended by our own
    # trusted infrastructure — so reading from the right is spoof-resistant.
    # trusted_proxy_ips may be exact IPs or CIDR ranges (e.g. "10.0.0.0/24").
    networks = [ipaddress.ip_network(ip, strict=False) for ip in settings.trusted_proxy_ips]
    peer = request.client.host if request.client else "unknown"

    if not _is_trusted(peer, networks):
        return peer

    xff = request.headers.get("X-Forwarded-For", "")
    if not xff:
        return peer

    for ip in reversed([entry.strip() for entry in xff.split(",")]):
        if not _is_trusted(ip, networks):
            return ip

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
