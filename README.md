# 🔐 Demo Zero-Knowledge Proof

> **Đề tài**: Tìm hiểu Zerocash — Môn Cơ sở An toàn Thông tin (KMA)

Demo thực nghiệm **Zero-Knowledge Proof** (ZKP): Chứng minh *"tôi biết giá trị bí mật x"* mà **không tiết lộ x**.

## ⚡ Quick Start

```bash
# Chạy demo ngay (chỉ cần Python 3)
python schnorr_zkp.py

# Chạy benchmark
python benchmark.py

# Chạy web demo (mở browser)
cd web-demo
python -m http.server 8000
# → Mở http://localhost:8000
```

> **Không cần cài thêm gì** — chỉ dùng Python standard library!

## 📋 Tổng quan

| Thành phần | Mô tả | Công nghệ |
|-----------|-------|-----------|
| **Schnorr ZKP** | Chứng minh biết discrete log | Python (pure) |
| **Hash Commitment ZKP** | Chứng minh biết preimage SHA-256 | Python (pure) |
| **Benchmark** | So sánh 2 phương pháp (20 lần) | Python + matplotlib |
| **Web Demo** | Giao diện trực quan trong browser | HTML/CSS/JS (pure) |

## 🔍 Zero-Knowledge Proof là gì?

Zero-Knowledge Proof cho phép **Prover** chứng minh với **Verifier** rằng một mệnh đề là đúng, mà **không tiết lộ bất kỳ thông tin nào** ngoài tính đúng đắn của mệnh đề.

**3 tính chất ZKP:**
1. **Completeness** — Nếu prover biết secret, proof luôn hợp lệ
2. **Soundness** — Nếu prover KHÔNG biết secret, proof gần như chắc chắn thất bại
3. **Zero-Knowledge** — Verifier không học được gì về secret

```
Prover                              Verifier
  │                                    │
  │  biết x (secret)                   │
  │  tính h = g^x mod p (public key)   │
  │  chọn random r                     │
  │  tính t = g^r mod p (commitment)   │
  │  tính c = SHA256(g||h||t) mod q    │
  │  tính s = (r + c·x) mod q         │
  │                                    │
  │  ──── gửi (h, t, s) ──────────►   │
  │  (KHÔNG gửi x)                    │
  │                                    │
  │                  verify:           │
  │                  g^s ≡ t·h^c ?     │
  │                  → ✅ OK!          │
  │                                    │
  │  Verifier biết: h (public key)     │
  │  Verifier KHÔNG biết: x (secret)   │
```

## 🛠️ Yêu cầu hệ thống

### Bắt buộc
- **Python 3.8+** (thường đã có sẵn trên máy)

### Tùy chọn
- **matplotlib** — `pip install matplotlib` (cho biểu đồ benchmark)

## 🚀 Hướng dẫn chi tiết

### 1. Chạy Demo CLI

```bash
python schnorr_zkp.py
```

Demo sẽ chạy tuần tự:
1. ✅ **Schnorr ZKP** — Chứng minh biết x sao cho g^x ≡ h (mod p)
2. ✅ **Hash Commitment ZKP** — Chứng minh biết x sao cho SHA256(x) = y
3. ✅ **Test Soundness** — Thử verify proof giả → bị từ chối
4. ✅ **So sánh** — Bảng so sánh 2 phương pháp

**Output mẫu:**
```
🔐 DEMO ZERO-KNOWLEDGE PROOF

🔑 SCHNORR ZKP — Discrete Log
  [1/3] Sinh khóa (Keygen)...
    Private key (x): *** ẨN *** (chỉ prover biết)
    Public key  (h): 0x1a2b3c4d...
  [2/3] Sinh ZK Proof (Prove)...
    Proof size:      1200 bytes
    Thời gian:       15.23ms
  [3/3] Xác minh Proof (Verify)...
    ✅ KẾT QUẢ: PROOF HỢP LỆ!
    Thời gian verify: 12.45ms
  [Test] Thử verify với proof giả...
    ❌ Proof giả bị từ chối! (đúng như mong đợi)
```

### 2. Chạy Benchmark

```bash
python benchmark.py
```

- Chạy mỗi protocol 20 lần với các secret khác nhau
- Tính trung bình, min, max, median, std deviation
- Tạo biểu đồ `benchmark_results.png` (nếu có matplotlib)

### 3. Chạy Web Demo

```bash
cd web-demo
python -m http.server 8000
```

Mở `http://localhost:8000` trong browser:
- Nhập giá trị bí mật → **Generate Proof** → **Verify**
- Thử **"Proof Giả"** → thấy bị từ chối (Soundness)
- Xem chi tiết toán học (verification equation)
- Metrics: thời gian prove, verify, kích thước proof

## 📁 Cấu trúc dự án

```
Demo-Zero-Knowledge-Proof/
├── README.md              # 📖 File này
├── .gitignore             # 🚫 Ignore rules
├── requirements.txt       # 📦 Dependencies (chỉ matplotlib, optional)
│
├── schnorr_zkp.py         # ⚡ Main demo — Schnorr + Hash Commitment ZKP
├── benchmark.py           # 📊 Benchmark — chạy 20 lần, so sánh, biểu đồ
│
└── web-demo/
    ├── index.html         # 🌐 Giao diện web
    ├── index.css          # 🎨 Dark theme, glassmorphism
    └── app.js             # ⚙️ Schnorr ZKP thuần JavaScript (BigInt)
```

## 🔬 Hai phương pháp ZKP

### 1. Schnorr ZKP (Discrete Log)
- **Bài toán**: Chứng minh biết x sao cho g^x ≡ h (mod p)
- **Tham số**: RFC 3526 Group 14 (2048-bit MODP)
- **Protocol**: Schnorr + Fiat-Shamir heuristic (non-interactive)
- **Proof nhỏ gọn**: ~1.2 KB
- **Ưu điểm**: Proof nhỏ, verify nhanh, cơ sở toán học vững chắc

### 2. Hash Commitment ZKP (SHA-256 Preimage)
- **Bài toán**: Chứng minh biết x sao cho SHA256(x) = y
- **Protocol**: Cut-and-Choose (20 rounds)
- **Soundness**: 1 - (1/2)^20 ≈ 99.9999%
- **Proof lớn hơn**: ~5-8 KB (do nhiều rounds)
- **Ưu điểm**: Trực quan, dễ hiểu

### So sánh

| Metric | Schnorr ZKP | Hash Commitment |
|--------|------------|-----------------|
| Proof size | ~1.2 KB | ~5-8 KB |
| Prove time | ~15 ms | ~1 ms |
| Verify time | ~12 ms | ~0.5 ms |
| Cơ sở toán | Discrete Log Problem | Hash collision resistance |
| Non-interactive | ✅ (Fiat-Shamir) | ✅ (Fiat-Shamir) |

## 💡 Liên hệ với Zerocash/Zcash

Trong **Zerocash/Zcash**, ZKP được dùng để:
- Ẩn **người gửi**, **người nhận**, và **số tiền** giao dịch
- Miner verify giao dịch hợp lệ mà không biết chi tiết

Zerocash dùng **zk-SNARKs** (Groth16) — proof chỉ ~200 bytes, verify trong milliseconds, nhưng cần trusted setup phức tạp.

| | Demo này | Zerocash |
|---|---------|----------|
| Protocol | Schnorr / Sigma | zk-SNARKs (Groth16) |
| Proof size | ~1 KB | ~200 bytes |
| Trusted setup | Không cần | Cần (Powers of Tau) |
| Bài toán | Discrete log / Hash | Arithmetic circuit |
| Công cụ | Python thuần | Circom + snarkjs |

## 📚 Tài liệu tham khảo

1. **Zerocash Paper**: [Zerocash: Decentralized Anonymous Payments from Bitcoin](https://eprint.iacr.org/2014/349.pdf)
2. **Schnorr Protocol**: [Wikipedia - Schnorr signature](https://en.wikipedia.org/wiki/Schnorr_signature)
3. **Fiat-Shamir**: [Wikipedia - Fiat-Shamir heuristic](https://en.wikipedia.org/wiki/Fiat%E2%80%93Shamir_heuristic)
4. **RFC 3526**: [MODP Diffie-Hellman Groups](https://www.rfc-editor.org/rfc/rfc3526)

## 📄 License

MIT
