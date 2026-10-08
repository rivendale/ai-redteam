import base64
import hashlib
import json
import unittest

import auth

N, E, D = 139194264316883530301815702335642162149246895843652821992098854089639418414041496196925670204277066131893972191901058303346610234323284789859328080540902455402778682469499666155138908107614105234802466787845898204590543320085643519022406483778304525139704595715897678812051596046154041675082013421596055460009, 65537, 49465712741508116342360616253369943031508311399647134049406935193061965834002570249269860675002103700380099979391422370339541821526607912413197903410250967181319755549390943648461022907640175972709072790564986499179978943143521911312744291550720677733847896750851464864083077313874864920315417126284755102473


def b64(x):
    return base64.urlsafe_b64encode(x).rstrip(b"=").decode()


def sign_rs256(claims):
    head = b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    body = b64(json.dumps(claims).encode())
    k = (N.bit_length() + 7) // 8
    info = bytes.fromhex("3031300d060960864801650304020105000420") + hashlib.sha256((head + "." + body).encode()).digest()
    em = b"\x00\x01" + b"\xff" * (k - len(info) - 3) + b"\x00" + info
    return head + "." + body + "." + b64(pow(int.from_bytes(em, "big"), D, N).to_bytes(k, "big"))

CLAIMS = {"sub": "u1", "exp": 2000000000}


class T(unittest.TestCase):
    def test_valid_token(self):
        self.assertEqual(auth.verify_token(sign_rs256(CLAIMS), now=1000)["sub"], "u1")

    def test_expired(self):
        with self.assertRaises(auth.InvalidToken):
            auth.verify_token(sign_rs256({"sub": "u1", "exp": 5}), now=1000)

    def test_tampered_payload(self):
        head, body, sig = sign_rs256(CLAIMS).split(".")
        forged = b64(json.dumps({"sub": "admin", "exp": 2000000000}).encode())
        with self.assertRaises(auth.InvalidToken):
            auth.verify_token(".".join([head, forged, sig]), now=1000)


if __name__ == "__main__":
    unittest.main()
