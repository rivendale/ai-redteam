#!/usr/bin/env python3
"""scan_secrets.py and key-shaped values (failure list written before the fix; offline).

Gap: no pattern matched a bare hex wallet key or a keyed RPC URL, so a value shaped like one could sit in a fixture or a published report
with nothing recording that it was a placeholder. The failure list:
  K1 a 64-hex value passed to a wallet constructor              -> must be a hit
  K2 a 64-hex value assigned to a private-key variable (0x or not) -> must be a hit
  K3 a 32-hex key in an RPC provider URL path (/v2/<key>)         -> must be a hit
  K4 obvious placeholders (one short unit repeated) in the same positions -> must NOT be a hit
  K5 an ordinary SHA-256 digest or commit hash in a report         -> must NOT be a hit (the pattern is contextual)
  K6 the scanner never prints the matched value
  K7 the committed onchain case holds no key-shaped value that the scanner flags
"""
import pathlib, random, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCAN = ROOT / "evals" / "tools" / "scan_secrets.py"
rng = random.Random(20261022)
H64 = "".join(rng.choice("0123456789abcdef") for _ in range(64))
H32 = "".join(rng.choice("0123456789abcdef") for _ in range(32))


def scan(text):
    with tempfile.TemporaryDirectory() as t:
        pathlib.Path(t, "f.txt").write_text(text)
        r = subprocess.run([sys.executable, str(SCAN), t], capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr


class T(unittest.TestCase):
    def test_k1_wallet_constructor(self):
        rc, out = scan(f'const w = new ethers.Wallet("0x{H64}", provider);\n')
        self.assertEqual(rc, 1, out)

    def test_k2_private_key_variable(self):
        for line in (f'PRIVATE_KEY = "0x{H64}"', f"private_key: {H64}", f"export DEPLOYER_PRIVATE_KEY='{H64}'"):
            rc, out = scan(line + "\n")
            self.assertEqual(rc, 1, line[:30] + " " + out)

    def test_k3_rpc_url_key(self):
        rc, out = scan(f"https://eth-mainnet.g.alchemy.com/v2/{H32}\n")
        self.assertEqual(rc, 1, out)

    def test_k4_placeholders_are_not_hits(self):
        text = 'new ethers.Wallet("0x' + "dead" * 16 + '")\nhttps://eth-mainnet.g.alchemy.com/v2/' + "beef" * 8 + "\nPRIVATE_KEY=0x" + "00" * 32 + "\n"
        rc, out = scan(text)
        self.assertEqual(rc, 0, out)

    def test_k5_digests_are_not_hits(self):
        rc, out = scan(f"sha256 {H64}  evals/results/x/README.md\ncommit {H32}\n")
        self.assertEqual(rc, 0, out)

    def test_k6_value_never_printed(self):
        _, out = scan(f'new ethers.Wallet("0x{H64}")\nhttps://x.example/v2/{H32}\n')
        self.assertNotIn(H64, out); self.assertNotIn(H32, out)

    def test_k7_onchain_case_is_clean(self):
        r = subprocess.run([sys.executable, str(SCAN), str(ROOT / "evals" / "onchain")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
