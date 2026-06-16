pragma circom 2.1.0;

// Import Poseidon hash từ circomlib
// Poseidon được thiết kế tối ưu cho ZK circuits (ít constraints hơn SHA256 ~200x)
include "../node_modules/circomlib/circuits/poseidon.circom";

/*
 * HashProof Circuit
 * =================
 * Chứng minh: "Tôi biết giá trị x (preimage) sao cho Poseidon(x) = y (hash)"
 * mà KHÔNG tiết lộ giá trị x.
 *
 * - Private input:  preimage (giá trị bí mật x - chỉ prover biết)
 * - Public output:  hash     (giá trị y - ai cũng thấy được)
 *
 * Prover chứng minh rằng họ biết preimage mà hash ra đúng giá trị hash,
 * nhưng verifier không biết preimage là gì.
 */
template HashProof() {
    // === SIGNALS ===
    
    // Private input: giá trị bí mật mà prover muốn chứng minh biết
    signal input preimage;
    
    // Public output: hash value mà ai cũng có thể thấy
    signal output hash;

    // === COMPUTATION ===
    
    // Khởi tạo Poseidon hasher với 1 input
    component hasher = Poseidon(1);
    
    // Gán preimage vào input của hasher
    hasher.inputs[0] <== preimage;
    
    // Output là kết quả hash
    hash <== hasher.out;
}

// Khai báo component chính của circuit
component main = HashProof();
