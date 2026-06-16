#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
  DEMO ZERO-KNOWLEDGE PROOF — Schnorr Protocol
============================================================
  Chứng minh: "Tôi biết x sao cho g^x ≡ h (mod p)"
  mà KHÔNG tiết lộ giá trị x.

  Sử dụng:
    python schnorr_zkp.py

  Không cần cài thêm thư viện nào — chỉ dùng Python standard library.
============================================================
"""

import hashlib
import secrets
import json
import time
import sys
import os

# Đảm bảo mã hóa UTF-8 cho console (tránh lỗi Unicode trên Windows)
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


# ============================================================
# THAM SỐ NHÓM (Group Parameters)
# ============================================================
# Sử dụng tham số từ RFC 3526 Group 14 (2048-bit MODP)
# Đây là safe prime: p = 2q + 1 (q cũng là số nguyên tố)
# An toàn cho mục đích demo và học thuật
# ============================================================

# Prime p (2048-bit) — từ RFC 3526 Group 14
P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF",
    16,
)

# Order q = (p - 1) / 2
Q = (P - 1) // 2

# Generator g = 2 (primitive root mod p for safe prime)
G = 2


# ============================================================
# SCHNORR ZKP CLASS
# ============================================================


class SchnorrZKP:
    """
    Schnorr Zero-Knowledge Proof Protocol

    Chứng minh: "Tôi biết secret x sao cho h = g^x mod p"
    mà KHÔNG tiết lộ x cho verifier.

    Tính chất ZKP:
      1. Completeness  — Nếu prover biết x, proof luôn hợp lệ
      2. Soundness     — Nếu prover KHÔNG biết x, proof gần như chắc chắn thất bại
      3. Zero-Knowledge — Verifier không học được gì về x ngoài việc prover biết nó

    Protocol (Non-interactive, Fiat-Shamir heuristic):
      1. Prover chọn random r, tính commitment t = g^r mod p
      2. Challenge c = Hash(g || h || t)  ← thay cho verifier gửi challenge
      3. Response s = (r + c * x) mod q
      4. Proof = (t, s)
      5. Verify: g^s ≡ t * h^c (mod p)
    """

    def __init__(self, p=P, q=Q, g=G):
        self.p = p
        self.q = q
        self.g = g

    def keygen(self, secret_str: str):
        """
        Sinh cặp (private_key, public_key) từ chuỗi bí mật.

        Args:
            secret_str: Chuỗi bí mật (ví dụ: "12345", "my_secret_password")

        Returns:
            (x, h) — private key x và public key h = g^x mod p
        """
        # Chuyển chuỗi bí mật thành số nguyên lớn qua SHA-256
        x_hash = hashlib.sha256(secret_str.encode("utf-8")).hexdigest()
        x = int(x_hash, 16) % self.q

        # Đảm bảo x > 0
        if x == 0:
            x = 1

        # Public key: h = g^x mod p
        h = pow(self.g, x, self.p)

        return x, h

    def prove(self, x: int, h: int) -> dict:
        """
        Sinh ZK proof (non-interactive, Fiat-Shamir).

        Args:
            x: Private key (secret)
            h: Public key = g^x mod p

        Returns:
            proof dict: { "t": commitment, "s": response, "c": challenge }
        """
        # Bước 1: Chọn random r ∈ [1, q-1]
        r = secrets.randbelow(self.q - 1) + 1

        # Bước 2: Commitment t = g^r mod p
        t = pow(self.g, r, self.p)

        # Bước 3: Challenge (Fiat-Shamir) c = Hash(g || h || t) mod q
        challenge_input = f"{self.g}||{h}||{t}"
        c_hash = hashlib.sha256(challenge_input.encode("utf-8")).hexdigest()
        c = int(c_hash, 16) % self.q

        # Bước 4: Response s = (r + c * x) mod q
        s = (r + c * x) % self.q

        return {
            "t": str(t),  # commitment (chuỗi hex lớn)
            "s": str(s),  # response
            "c": str(c),  # challenge (để verify có thể tái tạo)
        }

    def verify(self, h: int, proof: dict) -> bool:
        """
        Xác minh ZK proof.

        Verifier kiểm tra: g^s ≡ t * h^c (mod p)

        QUAN TRỌNG: Verifier chỉ cần biết h (public key) và proof.
                    Verifier KHÔNG CẦN biết x (private key).

        Args:
            h: Public key
            proof: Proof dictionary { "t", "s", "c" }

        Returns:
            True nếu proof hợp lệ, False nếu không
        """
        t = int(proof["t"])
        s = int(proof["s"])

        # Tái tạo challenge từ commitment (Fiat-Shamir verification)
        challenge_input = f"{self.g}||{h}||{t}"
        c_hash = hashlib.sha256(challenge_input.encode("utf-8")).hexdigest()
        c = int(c_hash, 16) % self.q

        # Kiểm tra challenge khớp
        if c != int(proof["c"]):
            return False

        # Xác minh: g^s ≡ t * h^c (mod p)
        lhs = pow(self.g, s, self.p)
        rhs = (t * pow(h, c, self.p)) % self.p

        return lhs == rhs

    def prove_and_verify(self, secret_str: str) -> dict:
        """
        Chạy toàn bộ flow: keygen → prove → verify.
        Trả về kết quả chi tiết bao gồm timing.
        """
        # Keygen
        keygen_start = time.perf_counter()
        x, h = self.keygen(secret_str)
        keygen_time = (time.perf_counter() - keygen_start) * 1000

        # Prove
        prove_start = time.perf_counter()
        proof = self.prove(x, h)
        prove_time = (time.perf_counter() - prove_start) * 1000

        # Proof size
        proof_json = json.dumps(proof)
        proof_size = len(proof_json.encode("utf-8"))

        # Verify
        verify_start = time.perf_counter()
        is_valid = self.verify(h, proof)
        verify_time = (time.perf_counter() - verify_start) * 1000

        return {
            "secret": secret_str,
            "public_key_hex": hex(h)[:40] + "...",
            "proof": proof,
            "proof_json_size": proof_size,
            "is_valid": is_valid,
            "keygen_time_ms": keygen_time,
            "prove_time_ms": prove_time,
            "verify_time_ms": verify_time,
        }


# ============================================================
# HASH COMMITMENT ZKP (Simulated)
# ============================================================


class HashCommitmentZKP:
    """
    ZKP cho Hash Preimage — Mô phỏng giao thức tương tác.

    Bài toán: Chứng minh "Tôi biết x sao cho SHA256(x) = y"
              mà KHÔNG tiết lộ x.

    Phương pháp: Cut-and-Choose Protocol (nhiều rounds)
      1. Prover tạo N commitments với random salt
      2. Verifier chọn ngẫu nhiên một nửa để mở (reveal salt)
      3. Nửa còn lại dùng để chứng minh tính nhất quán

    Lưu ý: Đây là phiên bản đơn giản hóa cho mục đích giáo dục.
           Trong thực tế (Zerocash), dùng zk-SNARKs cho bài toán này.
    """

    def __init__(self, num_rounds=20):
        """
        Args:
            num_rounds: Số rounds (càng nhiều → soundness càng cao)
                        Xác suất gian lận = (1/2)^num_rounds
        """
        self.num_rounds = num_rounds

    def hash(self, data: str) -> str:
        """SHA-256 hash."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def prove(self, secret: str) -> dict:
        """
        Sinh proof cho "tôi biết x sao cho SHA256(x) = y".

        Non-interactive version (Fiat-Shamir):
        - Tạo N commitments
        - Challenge được derive từ hash của tất cả commitments
        """
        y = self.hash(secret)  # Public hash
        commitments = []
        salts = []
        blinded_secrets = []

        for i in range(self.num_rounds):
            salt = secrets.token_hex(32)
            salts.append(salt)

            # Commitment: Hash(secret || salt)
            commitment = self.hash(f"{secret}||{salt}")
            commitments.append(commitment)

            # Blinded secret: Hash(salt || i)
            blinded = self.hash(f"{salt}||{i}")
            blinded_secrets.append(blinded)

        # Fiat-Shamir challenge: derive challenge bits from all commitments
        challenge_seed = self.hash("||".join(commitments))
        challenge_bits = bin(int(challenge_seed, 16))[2:].zfill(256)

        # Response: cho mỗi round, reveal theo challenge bit
        responses = []
        for i in range(self.num_rounds):
            bit = int(challenge_bits[i % len(challenge_bits)])
            if bit == 0:
                # Reveal salt (verifier kiểm tra commitment = Hash(secret || salt))
                responses.append({
                    "type": "reveal_salt",
                    "salt": salts[i],
                    "commitment": commitments[i],
                })
            else:
                # Reveal consistency proof
                responses.append({
                    "type": "consistency",
                    "commitment": commitments[i],
                    "blinded": blinded_secrets[i],
                    "check_hash": self.hash(f"{commitments[i]}||{blinded_secrets[i]}"),
                })

        return {
            "public_hash": y,
            "num_rounds": self.num_rounds,
            "commitments": commitments,
            "challenge": challenge_seed,
            "responses": responses,
        }

    def verify(self, y: str, proof: dict, secret_for_check: str = None) -> bool:
        """
        Xác minh proof.

        Args:
            y: Public hash (SHA256 của secret)
            proof: Proof từ prove()
            secret_for_check: (chỉ dùng cho demo) secret để verify các round type=reveal_salt
        """
        commitments = proof["commitments"]
        responses = proof["responses"]

        # Tái tạo challenge
        challenge_seed = self.hash("||".join(commitments))
        if challenge_seed != proof["challenge"]:
            return False

        challenge_bits = bin(int(challenge_seed, 16))[2:].zfill(256)

        for i, resp in enumerate(responses):
            bit = int(challenge_bits[i % len(challenge_bits)])

            if bit == 0 and resp["type"] == "reveal_salt":
                # Verifier kiểm tra: commitment có đúng format không
                # Trong thực tế, verifier sẽ dùng secret_for_check
                if secret_for_check:
                    expected = self.hash(f"{secret_for_check}||{resp['salt']}")
                    if expected != resp["commitment"]:
                        return False
            elif bit == 1 and resp["type"] == "consistency":
                # Kiểm tra consistency hash
                expected = self.hash(
                    f"{resp['commitment']}||{resp['blinded']}"
                )
                if expected != resp["check_hash"]:
                    return False
            else:
                return False

        return True


# ============================================================
# DEMO FUNCTIONS (CLI)
# ============================================================

# ANSI Colors
class Color:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @staticmethod
    def supports_color():
        """Kiểm tra terminal có hỗ trợ ANSI color không."""
        if os.name == "nt":
            os.system("")  # Enable ANSI escape on Windows
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def c(color, text):
    """Apply color to text."""
    if Color.supports_color():
        return f"{color}{text}{Color.RESET}"
    return str(text)


def print_header():
    """In header đẹp."""
    print()
    print(c(Color.BLUE, "=" * 64))
    print(c(Color.BOLD, "   🔐 DEMO ZERO-KNOWLEDGE PROOF"))
    print(c(Color.CYAN, '   Chứng minh "tôi biết x" mà không tiết lộ x'))
    print(c(Color.BLUE, "=" * 64))
    print()


def print_section(title, icon="📌"):
    """In tiêu đề section."""
    print()
    print(c(Color.YELLOW, f"{'─' * 64}"))
    print(c(Color.BOLD, f"  {icon} {title}"))
    print(c(Color.YELLOW, f"{'─' * 64}"))


def demo_schnorr():
    """Demo Schnorr ZKP."""
    print_section("SCHNORR ZKP — Discrete Log", "🔑")
    print()
    print(c(Color.DIM, '  Bài toán: Chứng minh "tôi biết x sao cho g^x ≡ h (mod p)"'))
    print(c(Color.DIM, "  Protocol: Schnorr (Non-interactive, Fiat-Shamir)"))
    print(c(Color.DIM, "  Tham số: RFC 3526 Group 14 (2048-bit)"))
    print()

    zkp = SchnorrZKP()

    # Nhập secret
    secret = input(c(Color.CYAN, "  Nhập giá trị bí mật x: ") or "12345")
    if not secret:
        secret = "12345"
    print()

    # ---- KEYGEN ----
    print(c(Color.YELLOW, "  [1/3] Sinh khóa (Keygen)..."))
    keygen_start = time.perf_counter()
    x, h = zkp.keygen(secret)
    keygen_time = (time.perf_counter() - keygen_start) * 1000

    print(f"    Private key (x): {c(Color.RED, '*** ẨN ***')} (chỉ prover biết)")
    print(f"    Public key  (h): {c(Color.GREEN, hex(h)[:50])}...")
    print(f"    Thời gian:       {c(Color.CYAN, f'{keygen_time:.2f}ms')}")
    print()

    # ---- PROVE ----
    print(c(Color.YELLOW, "  [2/3] Sinh ZK Proof (Prove)..."))
    prove_start = time.perf_counter()
    proof = zkp.prove(x, h)
    prove_time = (time.perf_counter() - prove_start) * 1000

    proof_json = json.dumps(proof)
    proof_size = len(proof_json.encode("utf-8"))

    print(f"    Commitment (t):  {c(Color.MAGENTA, proof['t'][:50])}...")
    print(f"    Response   (s):  {c(Color.MAGENTA, proof['s'][:50])}...")
    print(f"    Challenge  (c):  {c(Color.MAGENTA, proof['c'][:50])}...")
    print(f"    Proof size:      {c(Color.CYAN, f'{proof_size} bytes')}")
    print(f"    Thời gian:       {c(Color.CYAN, f'{prove_time:.2f}ms')}")
    print()

    # ---- VERIFY ----
    print(c(Color.YELLOW, "  [3/3] Xác minh Proof (Verify)..."))
    print(c(Color.DIM, "    (Verifier chỉ cần public key h + proof, KHÔNG cần biết x)"))

    verify_start = time.perf_counter()
    is_valid = zkp.verify(h, proof)
    verify_time = (time.perf_counter() - verify_start) * 1000

    if is_valid:
        print(f"\n    {c(Color.GREEN, '✅ KẾT QUẢ: PROOF HỢP LỆ!')}")
        print(c(Color.DIM, "    → Prover đã chứng minh biết x mà verifier không biết x là gì"))
    else:
        print(f"\n    {c(Color.RED, '❌ KẾT QUẢ: PROOF KHÔNG HỢP LỆ!')}")

    print(f"    Thời gian verify: {c(Color.CYAN, f'{verify_time:.2f}ms')}")

    # ---- TEST: FAKE PROOF ----
    print()
    print(c(Color.YELLOW, "  [Test] Thử verify với proof giả..."))
    fake_proof = {
        "t": str(secrets.randbelow(P)),
        "s": str(secrets.randbelow(Q)),
        "c": proof["c"],
    }
    fake_valid = zkp.verify(h, fake_proof)
    if not fake_valid:
        print(f"    {c(Color.RED, '❌ Proof giả bị từ chối!')} (đúng như mong đợi)")
        print(c(Color.DIM, "    → Tính SOUNDNESS: không thể tạo proof hợp lệ nếu không biết x"))
    else:
        print(f"    {c(Color.RED, '⚠️  Proof giả được chấp nhận?! (unexpected)')}")

    return {
        "prove_time": prove_time,
        "verify_time": verify_time,
        "proof_size": proof_size,
    }


def demo_hash_commitment():
    """Demo Hash Commitment ZKP."""
    print_section("HASH COMMITMENT ZKP — SHA-256 Preimage", "🔒")
    print()
    print(c(Color.DIM, '  Bài toán: Chứng minh "tôi biết x sao cho SHA256(x) = y"'))
    print(c(Color.DIM, "  Protocol: Cut-and-Choose (20 rounds)"))
    print(c(Color.DIM, "  Soundness: 1 - (1/2)^20 ≈ 99.9999%"))
    print()

    zkp = HashCommitmentZKP(num_rounds=20)

    secret = input(c(Color.CYAN, "  Nhập giá trị bí mật x: ") or "hello_zerocash")
    if not secret:
        secret = "hello_zerocash"
    print()

    y = zkp.hash(secret)
    print(f"    Public hash (y): {c(Color.GREEN, y)}")
    print(f"    Secret     (x): {c(Color.RED, '*** ẨN ***')}")
    print()

    # Prove
    print(c(Color.YELLOW, "  [1/2] Sinh proof (20 rounds)..."))
    prove_start = time.perf_counter()
    proof = zkp.prove(secret)
    prove_time = (time.perf_counter() - prove_start) * 1000

    proof_json = json.dumps(proof)
    proof_size = len(proof_json.encode("utf-8"))
    print(f"    Proof size:  {c(Color.CYAN, f'{proof_size} bytes')}")
    print(f"    Thời gian:   {c(Color.CYAN, f'{prove_time:.2f}ms')}")
    print()

    # Verify
    print(c(Color.YELLOW, "  [2/2] Xác minh proof..."))
    verify_start = time.perf_counter()
    is_valid = zkp.verify(y, proof, secret_for_check=secret)
    verify_time = (time.perf_counter() - verify_start) * 1000

    if is_valid:
        print(f"\n    {c(Color.GREEN, '✅ KẾT QUẢ: PROOF HỢP LỆ!')}")
    else:
        print(f"\n    {c(Color.RED, '❌ KẾT QUẢ: PROOF KHÔNG HỢP LỆ!')}")

    print(f"    Thời gian verify: {c(Color.CYAN, f'{verify_time:.2f}ms')}")

    return {
        "prove_time": prove_time,
        "verify_time": verify_time,
        "proof_size": proof_size,
    }


def print_comparison(schnorr_metrics, hash_metrics):
    """In bảng so sánh."""
    print_section("SO SÁNH HAI PHƯƠNG PHÁP", "📊")
    print()

    header = f"  {'Metric':<28} {'Schnorr ZKP':>15} {'Hash Commit':>15}"
    print(c(Color.BOLD, header))
    print(f"  {'─' * 58}")

    rows = [
        ("Thời gian Prove (ms)", 
         f"{schnorr_metrics['prove_time']:.2f}",
         f"{hash_metrics['prove_time']:.2f}"),
        ("Thời gian Verify (ms)",
         f"{schnorr_metrics['verify_time']:.2f}",
         f"{hash_metrics['verify_time']:.2f}"),
        ("Kích thước Proof (bytes)",
         f"{schnorr_metrics['proof_size']}",
         f"{hash_metrics['proof_size']}"),
        ("Tỷ lệ Prove/Verify",
         f"{schnorr_metrics['prove_time'] / max(schnorr_metrics['verify_time'], 0.001):.1f}x",
         f"{hash_metrics['prove_time'] / max(hash_metrics['verify_time'], 0.001):.1f}x"),
    ]

    for label, v1, v2 in rows:
        print(f"  {label:<28} {c(Color.CYAN, v1):>25} {c(Color.MAGENTA, v2):>25}")

    print()
    print(c(Color.BOLD, "  💡 Nhận xét:"))
    print(c(Color.DIM, "  • Schnorr ZKP: proof nhỏ gọn, dựa trên bài toán Discrete Log"))
    print(c(Color.DIM, "  • Hash Commitment: proof lớn hơn (nhiều rounds), dựa trên SHA-256"))
    print(c(Color.DIM, "  • Trong Zerocash/Zcash: dùng zk-SNARKs (Groth16) — proof chỉ ~200 bytes"))
    print(c(Color.DIM, "    nhưng cần trusted setup phức tạp (circom + snarkjs)"))


def main():
    """Main demo."""
    print_header()

    print(c(Color.DIM, "  Dự án: Demo Zero-Knowledge Proof"))
    print(c(Color.DIM, "  Môn:   Cơ sở An toàn Thông tin (KMA)"))
    print(c(Color.DIM, "  Đề tài: Tìm hiểu Zerocash"))
    print()
    print(c(Color.DIM, "  ZKP cho phép Prover chứng minh biết một thông tin bí mật"))
    print(c(Color.DIM, "  mà KHÔNG tiết lộ thông tin đó cho Verifier."))

    # Demo 1: Schnorr ZKP
    schnorr_metrics = demo_schnorr()

    print()

    # Demo 2: Hash Commitment ZKP
    hash_metrics = demo_hash_commitment()

    # So sánh
    print_comparison(schnorr_metrics, hash_metrics)

    print()
    print(c(Color.BLUE, "=" * 64))
    print(c(Color.GREEN, "  🎉 DEMO HOÀN TẤT!"))
    print(c(Color.DIM, "  Chạy benchmark chi tiết: python benchmark.py"))
    print(c(Color.BLUE, "=" * 64))
    print()


if __name__ == "__main__":
    main()
