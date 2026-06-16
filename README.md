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

## 📋 Tổng quan

| Thành phần | Mô tả | Công nghệ |
|-----------|-------|-----------|
| **Schnorr ZKP** | Chứng minh biết discrete log | Python (pure) |
| **Hash Commitment ZKP** | Chứng minh biết preimage SHA-256 | Python (pure) |
| **Benchmark** | So sánh 2 phương pháp (20 lần) | Python + matplotlib |
| **Web Demo** | Giao diện trực quan trong browser | HTML/CSS/JS (pure) |


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




## 📄 License

MIT
