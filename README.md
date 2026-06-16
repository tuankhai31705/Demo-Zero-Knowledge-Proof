## 🛠️ Yêu cầu hệ thống

### Bắt buộc
- **Node.js** 18+ — [Tải tại đây](https://nodejs.org/)
- **Circom** 2.1+ — Xem hướng dẫn cài đặt bên dưới
- **Git Bash** (Windows) — Đi kèm với [Git for Windows](https://git-scm.com/)

### Tùy chọn (cho benchmark)
- **Python** 3.10+
- **matplotlib** — `pip install matplotlib`

### Cài đặt Circom

Circom cần được compile từ Rust source:

```bash
# 1. Cài Rust (nếu chưa có)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Clone và build Circom
git clone https://github.com/iden3/circom.git
cd circom
cargo build --release
cargo install --path circom

# 3. Kiểm tra
circom --version
```

> **Windows**: Cài [Rust for Windows](https://www.rust-lang.org/tools/install), sau đó chạy các lệnh trên trong PowerShell hoặc Git Bash.

## 🚀 Hướng dẫn chạy demo

### Bước 1: Cài đặt dependencies

```bash
cd Demo-Zero-Knowledge-Proof
npm install
```

### Bước 2: Compile circuit + Trusted Setup

```bash
bash scripts/setup.sh
```

Script này sẽ tự động:
1. ✅ Compile circuit (`hash_proof.circom` → R1CS + WASM)
2. ✅ Powers of Tau ceremony (trusted setup phase 1)
3. ✅ Circuit-specific setup (phase 2)
4. ✅ Export verification key
5. ✅ Copy files cho web demo

### Bước 3: Sinh proof + Verify

```bash
bash scripts/prove_and_verify.sh
```

Kết quả mong đợi:
```
✅ Witness đã sinh thành công
✅ Proof đã sinh thành công (XXXms)
✅ KẾT QUẢ: PROOF HỢP LỆ! (XXms)

📊 METRICS
📦 Kích thước files:
  proof.json (ZK Proof)             ~800 bytes
  public.json (Public signals)      ~100 bytes
  verification_key.json             ~1.5 KB
  hash_proof_final.zkey (PK)        ~50 KB

⏱️ Thời gian:
  Sinh proof (Prove)                ~XXX ms
  Xác minh proof (Verify)           ~XX ms
```

### Bước 4: Benchmark (tùy chọn)

```bash
python scripts/benchmark.py
```

Chạy prove + verify 10 lần, tính trung bình, và tạo biểu đồ `benchmark_results.png`.

### Bước 5: Web Demo

Sau khi chạy setup (bước 2), mở web demo:

```bash
# Dùng bất kỳ HTTP server nào (cần vì WASM + fetch)
cd web-demo
npx serve .
# Hoặc: python -m http.server 8000
```

Mở browser tại `http://localhost:3000` (hoặc `http://localhost:8000`).

## 📁 Cấu trúc dự án

```
Demo-Zero-Knowledge-Proof/
├── README.md                    # 📖 File này
├── package.json                 # 📦 Dependencies
├── .gitignore                   # 🚫 Ignore build artifacts
│
├── circuits/
│   ├── hash_proof.circom        # ⚡ Circuit Poseidon hash
│   └── input.json               # 📝 Input mẫu (preimage = 12345)
│
├── scripts/
│   ├── setup.sh                 # 🔧 Compile + Trusted Setup
│   ├── prove_and_verify.sh      # 🔐 Sinh proof + Verify
│   └── benchmark.py             # 📊 Benchmark script
│
├── web-demo/
│   ├── index.html               # 🌐 Giao diện web
│   ├── index.css                # 🎨 Styling
│   ├── app.js                   # ⚙️ Logic JavaScript
│   └── build/                   # 📦 Files build (auto-generated)
│       ├── hash_proof.wasm
│       ├── hash_proof_final.zkey
│       └── verification_key.json
│
└── build/                       # 📦 Build output (auto-generated)
    ├── hash_proof.r1cs
    ├── hash_proof.sym
    ├── hash_proof_js/
    ├── proof.json
    ├── public.json
    └── ...
```

## 🔬 Giải thích kết quả

### Kích thước Proof (Tính SUCCINCT)
- **Proof chỉ ~800 bytes** — rất nhỏ gọn bất kể complexity của circuit
- Đây là tính **Succinct** của zk-SNARKs: proof luôn có kích thước cố định
- So với dữ liệu gốc (preimage + hash), proof nhỏ hơn đáng kể

### Thời gian Prove vs Verify
- **Prove chậm hơn Verify** nhiều lần (thường 5-50x)
- Verify rất nhanh → phù hợp cho blockchain (verify on-chain)
- Đây là đặc trưng của zk-SNARKs: trade-off tính toán cho prover

### Ứng dụng trong Zerocash/Zcash
- Giao dịch Zcash dùng zk-SNARKs để ẩn sender, receiver, amount
- Miner chỉ cần verify proof (nhanh) mà không cần biết chi tiết giao dịch
- Proof nhỏ gọn → không tăng kích thước block đáng kể

## 📚 Tài liệu tham khảo

1. **Zerocash Paper**: [Zerocash: Decentralized Anonymous Payments from Bitcoin](https://eprint.iacr.org/2014/349.pdf)
2. **snarkjs**: [https://github.com/iden3/snarkjs](https://github.com/iden3/snarkjs)
3. **Circom Docs**: [https://docs.circom.io/](https://docs.circom.io/)
4. **Poseidon Hash**: [https://www.poseidon-hash.info/](https://www.poseidon-hash.info/)
5. **Groth16**: [On the Size of Pairing-based Non-interactive Arguments](https://eprint.iacr.org/2016/260.pdf)

## 📄 License

MIT
