/**
 * ============================================================
 * DEMO ZERO-KNOWLEDGE PROOF - Web Demo Logic
 * ============================================================
 * Sử dụng snarkjs chạy trực tiếp trong browser (WASM)
 * để sinh và xác minh ZK proof cho Poseidon hash.
 * 
 * Flow: Input preimage → Generate Witness → Prove → Verify
 * ============================================================
 */

(function () {
    'use strict';

    // ============================================================
    // CẤU HÌNH
    // ============================================================
    
    const CONFIG = {
        // Đường dẫn tới các file build (sinh ra từ scripts/setup.sh)
        wasmPath: 'build/hash_proof.wasm',
        zkeyPath: 'build/hash_proof_final.zkey',
        vkeyPath: 'build/verification_key.json',
    };

    // ============================================================
    // STATE
    // ============================================================
    
    let state = {
        isReady: false,
        isProving: false,
        isVerifying: false,
        vkey: null,          // Verification key (loaded once)
        currentProof: null,  // Current proof object
        publicSignals: null, // Current public signals
        proveTime: 0,
        verifyTime: 0,
    };

    // ============================================================
    // DOM ELEMENTS
    // ============================================================
    
    const $ = (id) => document.getElementById(id);

    const elements = {
        preimageInput: $('preimageInput'),
        btnProve: $('btnProve'),
        btnVerify: $('btnVerify'),
        btnReset: $('btnReset'),
        statusDot: document.querySelector('.status-dot'),
        statusText: $('statusText'),
        sectionProof: $('sectionProof'),
        sectionResult: $('sectionResult'),
        hashOutput: $('hashOutput'),
        proofOutput: $('proofOutput'),
        verifyResult: $('verifyResult'),
        metricProveTime: $('metricProveTime'),
        metricVerifyTime: $('metricVerifyTime'),
        metricProofSize: $('metricProofSize'),
        metricRatio: $('metricRatio'),
        loadingOverlay: $('loadingOverlay'),
        loadingText: $('loadingText'),
    };

    // ============================================================
    // INITIALIZATION
    // ============================================================
    
    async function init() {
        try {
            showLoading('Đang tải verification key...');
            
            // Load verification key
            const response = await fetch(CONFIG.vkeyPath);
            if (!response.ok) {
                throw new Error(
                    'Không tìm thấy verification_key.json. ' +
                    'Vui lòng chạy scripts/setup.sh trước để sinh các file build.'
                );
            }
            state.vkey = await response.json();

            // Kiểm tra WASM file tồn tại
            const wasmCheck = await fetch(CONFIG.wasmPath, { method: 'HEAD' });
            if (!wasmCheck.ok) {
                throw new Error(
                    'Không tìm thấy hash_proof.wasm. ' +
                    'Vui lòng chạy scripts/setup.sh trước.'
                );
            }

            // Kiểm tra zkey file tồn tại
            const zkeyCheck = await fetch(CONFIG.zkeyPath, { method: 'HEAD' });
            if (!zkeyCheck.ok) {
                throw new Error(
                    'Không tìm thấy hash_proof_final.zkey. ' +
                    'Vui lòng chạy scripts/setup.sh trước.'
                );
            }

            // Sẵn sàng!
            state.isReady = true;
            setStatus('ready', 'Sẵn sàng — Nhập giá trị bí mật và nhấn Generate Proof');
            elements.btnProve.disabled = false;
            hideLoading();

        } catch (error) {
            console.error('Init error:', error);
            setStatus('error', `Lỗi: ${error.message}`);
            hideLoading();
            
            // Hiển thị hướng dẫn
            elements.preimageInput.disabled = true;
            elements.preimageInput.placeholder = 'Cần chạy setup.sh trước...';
        }
    }

    // ============================================================
    // CORE ZKP FUNCTIONS
    // ============================================================
    
    /**
     * Sinh Groth16 proof
     * @param {string} preimage - Giá trị bí mật x
     */
    async function generateProof(preimage) {
        if (!state.isReady || state.isProving) return;

        state.isProving = true;
        elements.btnProve.disabled = true;
        elements.btnProve.innerHTML = '<span class="spinner"></span> Đang sinh proof...';

        try {
            // Chuẩn bị input
            const input = { preimage: preimage };
            
            console.log('[ZKP] Bắt đầu sinh proof với input:', { preimage: '***' });
            console.log('[ZKP] (Giá trị preimage được ẩn vì tính zero-knowledge)');

            // === SINH PROOF ===
            const proveStart = performance.now();
            
            const { proof, publicSignals } = await snarkjs.groth16.fullProve(
                input,
                CONFIG.wasmPath,
                CONFIG.zkeyPath
            );
            
            const proveEnd = performance.now();
            state.proveTime = proveEnd - proveStart;
            state.currentProof = proof;
            state.publicSignals = publicSignals;

            console.log('[ZKP] Proof sinh thành công trong', state.proveTime.toFixed(2), 'ms');
            console.log('[ZKP] Public signals (hash):', publicSignals);

            // Hiển thị kết quả
            displayProofOutput(proof, publicSignals);

        } catch (error) {
            console.error('[ZKP] Lỗi khi sinh proof:', error);
            setStatus('error', `Lỗi sinh proof: ${error.message}`);
        } finally {
            state.isProving = false;
            elements.btnProve.disabled = false;
            elements.btnProve.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                Generate Proof
            `;
        }
    }

    /**
     * Xác minh proof
     */
    async function verifyProof() {
        if (!state.currentProof || state.isVerifying) return;

        state.isVerifying = true;
        elements.btnVerify.disabled = true;
        elements.btnVerify.innerHTML = '<span class="spinner"></span> Đang xác minh...';

        try {
            console.log('[ZKP] Bắt đầu xác minh proof...');

            // === VERIFY ===
            const verifyStart = performance.now();
            
            const isValid = await snarkjs.groth16.verify(
                state.vkey,
                state.publicSignals,
                state.currentProof
            );
            
            const verifyEnd = performance.now();
            state.verifyTime = verifyEnd - verifyStart;

            console.log('[ZKP] Kết quả:', isValid ? 'HỢP LỆ ✅' : 'KHÔNG HỢP LỆ ❌');
            console.log('[ZKP] Thời gian verify:', state.verifyTime.toFixed(2), 'ms');

            // Hiển thị kết quả
            displayVerifyResult(isValid);

        } catch (error) {
            console.error('[ZKP] Lỗi khi xác minh:', error);
            setStatus('error', `Lỗi verify: ${error.message}`);
        } finally {
            state.isVerifying = false;
            elements.btnVerify.disabled = false;
            elements.btnVerify.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="10"/>
                </svg>
                Verify Proof
            `;
        }
    }

    // ============================================================
    // UI DISPLAY FUNCTIONS
    // ============================================================
    
    function displayProofOutput(proof, publicSignals) {
        // Hiển thị hash output
        const hashValue = publicSignals[0];
        elements.hashOutput.textContent = hashValue;

        // Hiển thị proof (formatted)
        const proofDisplay = {
            protocol: proof.protocol,
            curve: proof.curve,
            pi_a: [
                proof.pi_a[0].substring(0, 30) + '...',
                proof.pi_a[1].substring(0, 30) + '...',
            ],
            pi_b: '[[...], [...]]',
            pi_c: [
                proof.pi_c[0].substring(0, 30) + '...',
                proof.pi_c[1].substring(0, 30) + '...',
            ],
        };
        elements.proofOutput.textContent = JSON.stringify(proofDisplay, null, 2);

        // Show proof section
        elements.sectionProof.style.display = 'block';
        elements.sectionProof.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setStatus('ready', `Proof sinh thành công (${state.proveTime.toFixed(0)}ms) — Nhấn Verify để xác minh`);
    }

    function displayVerifyResult(isValid) {
        // Result badge
        if (isValid) {
            elements.verifyResult.innerHTML = `
                <div class="result result--valid">
                    <div class="result__icon">✅</div>
                    <div class="result__text">
                        <h3>PROOF HỢP LỆ!</h3>
                        <p>Prover đã chứng minh thành công rằng họ biết giá trị x sao cho Poseidon(x) = y, 
                        mà verifier không biết x là gì.</p>
                    </div>
                </div>
            `;
        } else {
            elements.verifyResult.innerHTML = `
                <div class="result result--invalid">
                    <div class="result__icon">❌</div>
                    <div class="result__text">
                        <h3>PROOF KHÔNG HỢP LỆ!</h3>
                        <p>Proof không hợp lệ — prover không thể chứng minh họ biết preimage.</p>
                    </div>
                </div>
            `;
        }

        // Metrics
        const proofSizeBytes = new TextEncoder().encode(
            JSON.stringify(state.currentProof)
        ).length;

        elements.metricProveTime.textContent = state.proveTime.toFixed(1);
        elements.metricVerifyTime.textContent = state.verifyTime.toFixed(1);
        elements.metricProofSize.textContent = proofSizeBytes;
        elements.metricRatio.textContent = (state.proveTime / state.verifyTime).toFixed(1);

        // Show result section
        elements.sectionResult.style.display = 'block';
        elements.sectionResult.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setStatus(
            isValid ? 'ready' : 'error',
            isValid ? 'Xác minh thành công! ✅' : 'Xác minh thất bại ❌'
        );
    }

    // ============================================================
    // UI HELPERS
    // ============================================================
    
    function setStatus(type, text) {
        elements.statusDot.className = `status-dot status-dot--${type}`;
        elements.statusText.textContent = text;
    }

    function showLoading(text) {
        elements.loadingText.textContent = text;
        elements.loadingOverlay.classList.add('active');
    }

    function hideLoading() {
        elements.loadingOverlay.classList.remove('active');
    }

    function resetDemo() {
        state.currentProof = null;
        state.publicSignals = null;
        state.proveTime = 0;
        state.verifyTime = 0;

        elements.sectionProof.style.display = 'none';
        elements.sectionResult.style.display = 'none';
        elements.hashOutput.textContent = '—';
        elements.proofOutput.textContent = '—';
        elements.verifyResult.innerHTML = '';

        setStatus('ready', 'Sẵn sàng — Nhập giá trị bí mật và nhấn Generate Proof');
        elements.preimageInput.focus();
    }

    // ============================================================
    // EVENT LISTENERS
    // ============================================================
    
    elements.btnProve.addEventListener('click', () => {
        const preimage = elements.preimageInput.value.trim();
        if (!preimage) {
            setStatus('error', 'Vui lòng nhập giá trị bí mật');
            elements.preimageInput.focus();
            return;
        }
        
        // Kiểm tra input hợp lệ (phải là số)
        if (!/^\d+$/.test(preimage)) {
            setStatus('error', 'Giá trị phải là số nguyên dương');
            elements.preimageInput.focus();
            return;
        }

        // Reset previous results
        elements.sectionResult.style.display = 'none';
        
        generateProof(preimage);
    });

    elements.btnVerify.addEventListener('click', verifyProof);
    elements.btnReset.addEventListener('click', resetDemo);

    // Enter key to prove
    elements.preimageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && state.isReady && !state.isProving) {
            elements.btnProve.click();
        }
    });

    // ============================================================
    // START
    // ============================================================
    
    init();

})();
