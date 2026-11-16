import os, hmac, hashlib, time
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv("SECRET_KEY", "change-me-in-env")


def hash_password(pw: str) -> str:
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 200000)
    return salt.hex() + "$" + h.hex()


def verify_password(pw: str, stored: str) -> bool:
    try:
        salt_hex, h_hex = stored.split("$")
        h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt_hex), 200000)
        return hmac.compare_digest(h.hex(), h_hex)
    except Exception:
        return False


def make_token(student_id: int) -> str:
    payload = f"{student_id}.{int(time.time()) + 7 * 86400}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def read_token(token: str):
    try:
        sid, exp, sig = token.split(".")
        expected = hmac.new(SECRET.encode(), f"{sid}.{exp}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected) or time.time() > int(exp):
            return None
        return int(sid)
    except Exception:
        return None