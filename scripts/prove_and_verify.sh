#!/bin/bash

# ============================================================
# PROVE & VERIFY SCRIPT - Demo Zero-Knowledge Proof
# ============================================================
# Script này thực hiện:
#   1. Sinh witness từ input.json
#   2. Sinh Groth16 proof
#   3. Xác minh proof
#   4. Hiển thị kết quả + metrics
# ============================================================

set -e

# Màu sắc
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
CIRCUIT_DIR="$PROJECT_DIR/circuits"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   DEMO ZERO-KNOWLEDGE PROOF - PROVE & VERIFY${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Kiểm tra build files
if [ ! -f "$BUILD_DIR/hash_proof_final.zkey" ]; then
    echo -e "${RED}❌ Chưa chạy setup! Vui lòng chạy: bash scripts/setup.sh${NC}"
    exit 1
fi

# -----------------------------------------------------------
# BƯỚC 1: Sinh Witness
# -----------------------------------------------------------
echo -e "${YELLOW}[1/3] Sinh witness từ input.json...${NC}"
echo -e "${CYAN}Input: $(cat $CIRCUIT_DIR/input.json)${NC}"

node "$BUILD_DIR/hash_proof_js/generate_witness.js" \
    "$BUILD_DIR/hash_proof_js/hash_proof.wasm" \
    "$CIRCUIT_DIR/input.json" \
    "$BUILD_DIR/witness.wtns"

echo -e "${GREEN}✅ Witness đã sinh thành công${NC}"
echo ""

# -----------------------------------------------------------
# BƯỚC 2: Sinh Groth16 Proof
# -----------------------------------------------------------
echo -e "${YELLOW}[2/3] Sinh Groth16 proof...${NC}"

# Đo thời gian sinh proof
PROVE_START=$(date +%s%N)

npx snarkjs groth16 prove \
    "$BUILD_DIR/hash_proof_final.zkey" \
    "$BUILD_DIR/witness.wtns" \
    "$BUILD_DIR/proof.json" \
    "$BUILD_DIR/public.json"

PROVE_END=$(date +%s%N)
PROVE_TIME=$(( (PROVE_END - PROVE_START) / 1000000 ))

echo -e "${GREEN}✅ Proof đã sinh thành công (${PROVE_TIME}ms)${NC}"
echo ""

# Hiển thị public signals
echo -e "${CYAN}📤 Public signals (hash output):${NC}"
cat "$BUILD_DIR/public.json"
echo ""
echo ""

# Hiển thị proof (tóm tắt)
echo -e "${CYAN}🔐 Proof (tóm tắt):${NC}"
node -e "
const proof = require('$BUILD_DIR/proof.json');
console.log('  π_A:', proof.pi_a[0].substring(0, 20) + '...');
console.log('  π_B:', proof.pi_b[0][0].substring(0, 20) + '...');
console.log('  π_C:', proof.pi_c[0].substring(0, 20) + '...');
console.log('  Protocol:', proof.protocol);
console.log('  Curve:', proof.curve);
"
echo ""

# -----------------------------------------------------------
# BƯỚC 3: Xác minh Proof
# -----------------------------------------------------------
echo -e "${YELLOW}[3/3] Xác minh proof...${NC}"

# Đo thời gian verify
VERIFY_START=$(date +%s%N)

VERIFY_RESULT=$(npx snarkjs groth16 verify \
    "$BUILD_DIR/verification_key.json" \
    "$BUILD_DIR/public.json" \
    "$BUILD_DIR/proof.json" 2>&1)

VERIFY_END=$(date +%s%N)
VERIFY_TIME=$(( (VERIFY_END - VERIFY_START) / 1000000 ))

if echo "$VERIFY_RESULT" | grep -q "OK"; then
    echo -e "${GREEN}✅ KẾT QUẢ: PROOF HỢP LỆ! (${VERIFY_TIME}ms)${NC}"
else
    echo -e "${RED}❌ KẾT QUẢ: PROOF KHÔNG HỢP LỆ!${NC}"
fi
echo ""

# -----------------------------------------------------------
# METRICS
# -----------------------------------------------------------
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   📊 METRICS${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Kích thước files
PROOF_SIZE=$(wc -c < "$BUILD_DIR/proof.json")
PUBLIC_SIZE=$(wc -c < "$BUILD_DIR/public.json")
VKEY_SIZE=$(wc -c < "$BUILD_DIR/verification_key.json")
ZKEY_SIZE=$(wc -c < "$BUILD_DIR/hash_proof_final.zkey")

echo -e "${CYAN}📦 Kích thước files:${NC}"
printf "  %-30s %10s bytes\n" "proof.json (ZK Proof)" "$PROOF_SIZE"
printf "  %-30s %10s bytes\n" "public.json (Public signals)" "$PUBLIC_SIZE"
printf "  %-30s %10s bytes\n" "verification_key.json" "$VKEY_SIZE"
printf "  %-30s %10s bytes\n" "hash_proof_final.zkey (PK)" "$ZKEY_SIZE"
echo ""

echo -e "${CYAN}⏱️  Thời gian:${NC}"
printf "  %-30s %10s ms\n" "Sinh proof (Prove)" "$PROVE_TIME"
printf "  %-30s %10s ms\n" "Xác minh proof (Verify)" "$VERIFY_TIME"
echo ""

echo -e "${CYAN}💡 Nhận xét:${NC}"
echo "  • Proof rất nhỏ (~$PROOF_SIZE bytes) - tính SUCCINCT của zk-SNARKs"
echo "  • Thời gian verify nhanh hơn prove - đặc trưng của zk-SNARKs"
echo "  • Proving key (zkey) lớn - đây là trade-off cho tính succinct"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 DEMO HOÀN TẤT!${NC}"
echo -e "${BLUE}============================================================${NC}"
