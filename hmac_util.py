import hashlib

# HMAC block size for SHA-256 (512 bits = 64 bytes).
# This is fixed by the SHA-256 spec — don't change it.
_BLOCK = 64


def _hmac_sha256(key: str, message: str) -> str:
    """
    HMAC-SHA256 implemented from scratch using only hashlib.

    In production this key would never live in source code, it would come
    from a server-side secret, an encrypted config, or a hardware key store.
    Here it's in key.py (gitignored) as a proof-of-concept.
    """
    k = key.encode()
    m = message.encode()

    # Normalize key to exactly BLOCK bytes.
    # If longer: hash it down first (SHA-256 output = 32 bytes < 64, then pad).
    # If shorter: pad with zero bytes on the right.
    if len(k) > _BLOCK:
        k = hashlib.sha256(k).digest()
    k = k.ljust(_BLOCK, b'\x00')

    # Derive the inner and outer padded keys by XOR-ing every byte.
    ipad = bytes(b ^ 0x36 for b in k)
    opad = bytes(b ^ 0x5c for b in k)

    # Inner hash: binds the message to the key.
    inner = hashlib.sha256(ipad + m).digest()

    # Outer hash: wraps the inner hash, preventing length-extension attacks.
    return hashlib.sha256(opad + inner).hexdigest()


def _fmt(seconds: float) -> str:
    """Format lap time as MM:SS.mmm (e.g. 01:23.456)."""
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:06.3f}"


def _norm(name: str) -> str:
    """Normalize track name to a single lowercase word (e.g. 'GRA GRA' -> 'gragram')."""
    return name.replace(" ", "").lower()


def sign_lap(track_name: str, time_seconds: float, official: bool = True) -> str:
    """
    Produce a shareable authenticated lap string: 'MM:SS.mmm,trackname HASH'

    The data portion (everything before the space) is what gets signed.
    The HASH is the HMAC-SHA256 of that data using the secret key.

    If official=False (car params were not default when the lap was set),
    '[unofficial]' is appended to the data BEFORE hashing so it becomes
    part of the authenticated string, anyone verifying can see it was run
    with modified params.

    In a real leaderboard system, signing would happen server-side so the
    key is never exposed to the client. Here it runs locally, the key is
    only as secret as key.py is hidden (fine for a local game, not for an
    online leaderboard where someone could inspect the binary).
    """
    from key import SECRET_KEY
    tag = "" if official else "[unofficial]"
    data = f"{_fmt(time_seconds)},{_norm(track_name)}{tag}"
    return f"{data} {_hmac_sha256(SECRET_KEY, data)}"


def verify_lap(s: str) -> bool:
    """
    Verify a signed lap string by recomputing the HMAC and comparing.

    Splits on the last space: everything before = data, everything after = hash.
    Uses a constant-time comparison (all() over zip) to avoid timing attacks —
    a naive '==' short-circuits on the first mismatched byte, leaking info
    about how many bytes matched. Irrelevant for a local game, but good habit.

    In production, verification would also happen server-side with the key
    never leaving the server. Here both sign and verify share the same local
    key.py, which is fine since the trust model is just 'prove this time came
    from this binary'.
    """
    from key import SECRET_KEY
    parts = s.rsplit(" ", 1)
    if len(parts) != 2:
        return False
    data, given = parts
    expected = _hmac_sha256(SECRET_KEY, data)
    return len(expected) == len(given) and all(a == b for a, b in zip(expected, given))
