"""Token verification for the reports API. Tokens are RS256 JWTs signed by the identity service."""
import base64
import hashlib
import hmac
import json
import time

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDGOB5HdNr05MOWzUsaHv+OUN7o
MetXy2qMUY0VB13ECC+EpQR3MpgsZT7v8l1TQlE/FcqK940lEXE2oNjN8YpPaLFA
sHw35zmnzCJPK37OywrrZsfzpm6DTfJRXHKBl2pLmCzhA8L6fPwwB9Q9d8T4Hr+u
t8bEs81vTJVmUBxYqQIDAQAB
-----END PUBLIC KEY-----
"""
PUBLIC_N = 139194264316883530301815702335642162149246895843652821992098854089639418414041496196925670204277066131893972191901058303346610234323284789859328080540902455402778682469499666155138908107614105234802466787845898204590543320085643519022406483778304525139704595715897678812051596046154041675082013421596055460009
PUBLIC_E = 65537


class InvalidToken(Exception):
    pass


def _b64d(part):
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def _rsa_verify(message, signature, n, e):
    """RSASSA-PKCS1-v1_5 with SHA-256: the whole encoded message must match."""
    k = (n.bit_length() + 7) // 8
    if len(signature) != k:
        return False
    em = pow(int.from_bytes(signature, "big"), e, n).to_bytes(k, "big")
    info = bytes.fromhex("3031300d060960864801650304020105000420") + hashlib.sha256(message).digest()
    return hmac.compare_digest(em, b"\x00\x01" + b"\xff" * (k - len(info) - 3) + b"\x00" + info)
ISSUER = "https://id.example.test"
AUDIENCE = "reports-api"


def verify_token(token, now=None):
    """Return the claims of a valid, unexpired token issued for this API, or raise InvalidToken. Only RS256 is accepted."""
    try:
        head_b64, body_b64, sig_b64 = token.split(".")
        header = json.loads(_b64d(head_b64))
        claims = json.loads(_b64d(body_b64))
        signature = _b64d(sig_b64)
    except Exception as exc:
        raise InvalidToken("malformed token") from exc
    if header.get("alg") != "RS256":
        raise InvalidToken("only RS256 is accepted")
    if not _rsa_verify((head_b64 + "." + body_b64).encode(), signature, PUBLIC_N, PUBLIC_E):
        raise InvalidToken("bad signature")
    exp = claims.get("exp")
    if not isinstance(exp, int) or exp < (now if now is not None else time.time()):
        raise InvalidToken("expired or no expiry")
    if claims.get("iss") != ISSUER or claims.get("aud") != AUDIENCE:
        raise InvalidToken("wrong issuer or audience")
    return claims
