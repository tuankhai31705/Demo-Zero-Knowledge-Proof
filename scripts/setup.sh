#!/bin/bash

# ============================================================
# SETUP SCRIPT - Demo Zero-Knowledge Proof
# ============================================================
# Script này tự động hóa toàn bộ quy trình:
#   1. Cài đặt dependencies
#   2. Compile circuit
#   3. Trusted Setup (Powers of Tau + Phase 2)
#   4. Export verification key
# ============================================================

set -e  # Dừng ngay nếu có lỗi

# Màu sắc cho output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Thư mục gốc của project
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
CIRCUIT_DIR="$PROJECT_DIR/circuits"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   DEMO ZERO-KNOWLEDGE PROOF - SETUP${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# -----------------------------------------------------------
# BƯỚC 0: Kiểm tra prerequisites
# -----------------------------------------------------------
echo -e "${YELLOW}[0/5] Kiểm tra prerequisites...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js chưa được cài đặt. Vui lòng cài Node.js 18+${NC}"
    exit 1
fi

if ! command -v circom &> /dev/null; then
    echo -e "${RED}❌ Circom chưa được cài đặt.${NC}"
    echo -e "${YELLOW}Hướng dẫn cài đặt:${NC}"
    echo "  git clone https://github.com/iden3/circom.git"
    echo "  cd circom"
    echo "  cargo build --release"
    echo "  cargo install --path circom"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v) - OK${NC}"
echo -e "${GREEN}✅ Circom $(circom --version) - OK${NC}"
echo ""

# -----------------------------------------------------------
# BƯỚC 1: Cài đặt dependencies
# -----------------------------------------------------------
echo -e "${YELLOW}[1/5] Cài đặt dependencies (circomlib, snarkjs)...${NC}"
cd "$PROJECT_DIR"
npm install
echo -e "${GREEN}✅ Dependencies đã cài đặt${NC}"
echo ""

# -----------------------------------------------------------
# BƯỚC 2: Compile circuit
# -----------------------------------------------------------
echo -e "${YELLOW}[2/5] Compile circuit hash_proof.circom...${NC}"
mkdir -p "$BUILD_DIR"

circom "$CIRCUIT_DIR/hash_proof.circom" \
    --wasm \
    --r1cs \
    --sym \
    -o "$BUILD_DIR"

echo -e "${GREEN}✅ Circuit đã compile thành công${NC}"
echo "   📁 R1CS:  $BUILD_DIR/hash_proof.r1cs"
echo "   📁 WASM:  $BUILD_DIR/hash_proof_js/"
echo "   📁 SYM:   $BUILD_DIR/hash_proof.sym"

# Hiển thị thông tin circuit
echo ""
echo -e "${BLUE}📊 Thông tin circuit:${NC}"
npx snarkjs r1cs info "$BUILD_DIR/hash_proof.r1cs"
echo ""

# -----------------------------------------------------------
# BƯỚC 3: Trusted Setup Phase 1 - Powers of Tau
# -----------------------------------------------------------
echo -e "${YELLOW}[3/5] Trusted Setup Phase 1 - Powers of Tau ceremony...${NC}"

# Tạo Powers of Tau (bn128, power 12 = hỗ trợ tới 2^12 = 4096 constraints)
npx snarkjs powersoftau new bn128 12 "$BUILD_DIR/pot12_0000.ptau" -v

# Contribute (đóng góp entropy)
npx snarkjs powersoftau contribute \
    "$BUILD_DIR/pot12_0000.ptau" \
    "$BUILD_DIR/pot12_0001.ptau" \
    --name="Demo ZKP Contribution" \
    -v -e="random entropy for demo"

# Chuẩn bị cho Phase 2
npx snarkjs powersoftau prepare phase2 \
    "$BUILD_DIR/pot12_0001.ptau" \
    "$BUILD_DIR/pot12_final.ptau" \
    -v

echo -e "${GREEN}✅ Phase 1 hoàn tất${NC}"
echo ""

# -----------------------------------------------------------
# BƯỚC 4: Trusted Setup Phase 2 - Circuit-specific
# -----------------------------------------------------------
echo -e "${YELLOW}[4/5] Trusted Setup Phase 2 - Circuit-specific setup...${NC}"

# Tạo zkey (proving key)
npx snarkjs groth16 setup \
    "$BUILD_DIR/hash_proof.r1cs" \
    "$BUILD_DIR/pot12_final.ptau" \
    "$BUILD_DIR/hash_proof_0000.zkey"

# Contribute vào zkey
npx snarkjs zkey contribute \
    "$BUILD_DIR/hash_proof_0000.zkey" \
    "$BUILD_DIR/hash_proof_final.zkey" \
    --name="Demo ZKP Phase 2" \
    -v -e="more random entropy"

echo -e "${GREEN}✅ Phase 2 hoàn tất${NC}"
echo ""

# -----------------------------------------------------------
# BƯỚC 5: Export Verification Key
# -----------------------------------------------------------
echo -e "${YELLOW}[5/5] Export verification key...${NC}"

npx snarkjs zkey export verificationkey \
    "$BUILD_DIR/hash_proof_final.zkey" \
    "$BUILD_DIR/verification_key.json"

echo -e "${GREEN}✅ Verification key đã export${NC}"
echo ""

# -----------------------------------------------------------
# COPY FILES CHO WEB DEMO
# -----------------------------------------------------------
echo -e "${YELLOW}[Bonus] Copy files cho web demo...${NC}"
WEB_BUILD="$PROJECT_DIR/web-demo/build"
mkdir -p "$WEB_BUILD"

cp "$BUILD_DIR/hash_proof_js/hash_proof.wasm" "$WEB_BUILD/"
cp "$BUILD_DIR/hash_proof_final.zkey" "$WEB_BUILD/"
cp "$BUILD_DIR/verification_key.json" "$WEB_BUILD/"

echo -e "${GREEN}✅ Files đã copy vào web-demo/build/${NC}"
echo ""

# -----------------------------------------------------------
# TỔNG KẾT
# -----------------------------------------------------------
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 SETUP HOÀN TẤT!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "Các file đã sinh ra:"
echo "  📁 build/hash_proof.r1cs          - Circuit constraints"
echo "  📁 build/hash_proof_js/           - WASM for witness generation"
echo "  📁 build/hash_proof_final.zkey    - Proving key"
echo "  📁 build/verification_key.json    - Verification key"
echo "  📁 web-demo/build/                - Files cho web demo"
echo ""
echo -e "Bước tiếp theo: chạy ${YELLOW}bash scripts/prove_and_verify.sh${NC}"
