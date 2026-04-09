import hashlib

_BLOCK = 64  # SHA-256 HMAC block size (512 bits)


def _hmac_sha256(key: str, message: str) -> str:
    k = key.encode()
    m = message.encode()
    if len(k) > _BLOCK:
        k = hashlib.sha256(k).digest()
    k = k.ljust(_BLOCK, b'\x00')
    ipad = bytes(b ^ 0x36 for b in k)
    opad = bytes(b ^ 0x5c for b in k)
    inner = hashlib.sha256(ipad + m).digest()
    return hashlib.sha256(opad + inner).hexdigest()


def _fmt(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:06.3f}"


def _norm(name: str) -> str:
    return name.replace(" ", "").lower()


def sign_lap(track_name: str, time_seconds: float, official: bool = True) -> str:
    from key import SECRET_KEY
    tag = "" if official else "[unofficial]"
    data = f"{_fmt(time_seconds)},{_norm(track_name)}{tag}"
    return f"{data} {_hmac_sha256(SECRET_KEY, data)}"


def verify_lap(s: str) -> bool:
    from key import SECRET_KEY
    parts = s.rsplit(" ", 1)
    if len(parts) != 2:
        return False
    data, given = parts
    expected = _hmac_sha256(SECRET_KEY, data)
    return len(expected) == len(given) and all(a == b for a, b in zip(expected, given))
