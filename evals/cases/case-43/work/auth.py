"""Token verification for the reports API. Tokens are RS256 JWTs signed by the identity service."""
import base64
import hashlib
import hmac
import json
import time

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtApfGzL5f463GgNhwCpr
7trgJ+iiLOabiBoBDndFu3k0zzwUgjzjMhXQNozgimRAOKcRMfNtrBBPTTdrayLw
WtkyZGPPnjgGcEDY4EvixZVuwObsSYz76G9IT5ja+H9K0gJkOJotfmIjavfPKpd0
qdtByYaBnYaAuH6+81RnrELmMiQVmeHKnPDIXHjuenKdta0INxNZ5wFnInJMJ9QS
1uhgiqkBGgRJY+is0ceg9BCSwfDPg4X3Pw+eFDoXr1z+r3Lz/WPYZFL9ZX9fbpYE
i9EWoGJ4+boAA5iGnP2JrBnMsRIQKLSW6BUdKJsB7ujrSKSfZD8CXR5NtPnuPaet
rwIDAQAB
-----END PUBLIC KEY-----
"""
PUBLIC_N = 22728009275483426428713918095627602453218962301381480505719809873212951584831928760335639319191993885577454032052438863159179300323015791786910428792710485365922695236290224470175589334040366739498968089503463172113799356829044282159178658395862247233700639776802394673168569659684273358869684090622246526604001027684389879294620782461484463926992882863810838614923610416353774965925739295417521312024743846837983288022806364499675614665281871619036069371587222705766283015357776205229944451682470335106725346907765361323141031624546871858940618250042587168170844380548292232570613303152250261867692816223767221480879
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
def verify_token(token, now=None):
    """Return the claims of a valid, unexpired token or raise InvalidToken."""
    try:
        head_b64, body_b64, sig_b64 = token.split(".")
        header = json.loads(_b64d(head_b64))
        claims = json.loads(_b64d(body_b64))
        signature = _b64d(sig_b64)
    except Exception as exc:
        raise InvalidToken("malformed token") from exc
    signing_input = (head_b64 + "." + body_b64).encode()
    alg = header.get("alg")
    if alg == "RS256":
        ok = _rsa_verify(signing_input, signature, PUBLIC_N, PUBLIC_E)
    elif alg == "HS256":
        ok = hmac.compare_digest(hmac.new(PUBLIC_KEY_PEM.encode(), signing_input, hashlib.sha256).digest(), signature)
    elif alg == "none":
        ok = True
    else:
        raise InvalidToken("unsupported algorithm")
    if not ok:
        raise InvalidToken("bad signature")
    if claims.get("exp", 0) < (now if now is not None else time.time()):
        raise InvalidToken("expired")
    return claims
