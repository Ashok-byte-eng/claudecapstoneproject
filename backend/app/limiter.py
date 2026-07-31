import ipaddress

from fastapi import Request
from slowapi import Limiter

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
