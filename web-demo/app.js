/**
 * ============================================================
 * DEMO ZERO-KNOWLEDGE PROOF — Schnorr Protocol (Pure JS)
 * ============================================================
 * Không cần thư viện ngoài — dùng BigInt native của JavaScript.
 * 
 * Schnorr ZKP Protocol (Non-interactive, Fiat-Shamir):
 *   1. Prover chọn random r, tính t = g^r mod p
 *   2. Challenge c = SHA256(g || h || t) mod q
 *   3. Response s = (r + c * x) mod q
 *   4. Verify: g^s ≡ t * h^c (mod p)
 * ============================================================
 */

(function () {
    'use strict';

    // ============================================================
    // THAM SỐ NHÓM — RFC 3526 Group 14 (2048-bit MODP)
    // ============================================================

    const P = BigInt(
        '0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1' +
        '29024E088A67CC74020BBEA63B139B22514A08798E3404DD' +
        'EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245' +
        'E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED' +
        'EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D' +
        'C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F' +
        '83655D23DCA3AD961C62F356208552BB9ED529077096966D' +
        '670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B' +
        'E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9' +
        'DE2BCBF6955817183995497CEA956AE515D2261898FA0510' +
        '15728E5A8AACAA68FFFFFFFFFFFFFFFF'
    );

    const Q = (P - 1n) / 2n;
    const G = 2n;

    // ============================================================
    // CRYPTO UTILITIES
    // ============================================================

    /**
     * Modular exponentiation: base^exp mod mod
     * Sử dụng phương pháp square-and-multiply.
     */
    function modPow(base, exp, mod) {
        let result = 1n;
        base = ((base % mod) + mod) % mod;
        while (exp > 0n) {
            if (exp % 2n === 1n) {
                result = (result * base) % mod;
            }
            exp = exp / 2n;
            base = (base * base) % mod;
        }
        return result;
    }

    /**
     * SHA-256 hash (Web Crypto API).
     * Returns hex string.
     */
    async function sha256(message) {
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    /**
     * Generate cryptographic random BigInt in range [1, max-1].
     */
    function randomBigInt(max) {
        // Tính số bytes cần thiết
        const hexLen = max.toString(16).length;
        const byteLen = Math.ceil(hexLen / 2);
        const arr = new Uint8Array(byteLen);

        let r;
        do {
            crypto.getRandomValues(arr);
            r = BigInt('0x' + Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join(''));
            r = r % max;
        } while (r === 0n);

        return r;
    }

    // ============================================================
    // SCHNORR ZKP PROTOCOL
    // ============================================================

    const SchnorrZKP = {
        /**
         * Sinh cặp khóa từ chuỗi bí mật.
         * @param {string} secret - Chuỗi bí mật
         * @returns {Promise<{x: BigInt, h: BigInt}>}
         */
        async keygen(secret) {
            const xHash = await sha256(secret);
            let x = BigInt('0x' + xHash) % Q;
            if (x === 0n) x = 1n;
            const h = modPow(G, x, P);
            return { x, h };
        },

        /**
         * Sinh ZK proof (non-interactive, Fiat-Shamir).
         * @param {BigInt} x - Private key
         * @param {BigInt} h - Public key = g^x mod p
         * @returns {Promise<Object>} proof
         */
        async prove(x, h) {
            // Bước 1: Random r
            const r = randomBigInt(Q);

            // Bước 2: Commitment t = g^r mod p
            const t = modPow(G, r, P);

            // Bước 3: Fiat-Shamir challenge
            const challengeInput = `${G}||${h}||${t}`;
            const cHash = await sha256(challengeInput);
            const c = BigInt('0x' + cHash) % Q;

            // Bước 4: Response s = (r + c*x) mod q
            const s = ((r + c * x) % Q + Q) % Q;

            return { t, s, c };
        },

        /**
         * Xác minh ZK proof.
         * @param {BigInt} h - Public key
         * @param {Object} proof - { t, s, c }
         * @returns {Promise<boolean>}
         */
        async verify(h, proof) {
            const { t, s } = proof;

            // Tái tạo challenge
            const challengeInput = `${G}||${h}||${t}`;
            const cHash = await sha256(challengeInput);
            const c = BigInt('0x' + cHash) % Q;

            // Xác minh: g^s ≡ t * h^c (mod p)
            const lhs = modPow(G, s, P);
            const rhs = (t * modPow(h, c, P)) % P;

            return lhs === rhs;
        },
    };

    // ============================================================
    // UI STATE
    // ============================================================

    let state = {
        currentProof: null,
        publicKey: null,
        proveTime: 0,
        verifyTime: 0,
    };

    const $ = (id) => document.getElementById(id);

    // ============================================================
    // UI ACTIONS
    // ============================================================

    async function handleProve() {
        const secret = $('secretInput').value.trim();
        if (!secret) {
            alert('Vui lòng nhập giá trị bí mật');
            return;
        }

        const btn = $('btnProve');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Đang sinh proof...';

        try {
            // Keygen
            const { x, h } = await SchnorrZKP.keygen(secret);
            state.publicKey = h;

            // Prove
            const proveStart = performance.now();
            const proof = await SchnorrZKP.prove(x, h);
            state.proveTime = performance.now() - proveStart;
            state.currentProof = proof;

            // Display
            const hHex = h.toString(16);
            $('publicKeyOutput').textContent = hHex.substring(0, 80) + '...';

            const proofDisplay = {
                commitment_t: proof.t.toString(16).substring(0, 60) + '...',
                response_s: proof.s.toString(16).substring(0, 60) + '...',
                challenge_c: proof.c.toString(16).substring(0, 60) + '...',
                protocol: 'Schnorr (Fiat-Shamir)',
                group: 'RFC 3526 Group 14 (2048-bit)',
            };
            $('proofOutput').textContent = JSON.stringify(proofDisplay, null, 2);

            $('sectionProof').style.display = 'block';
            $('sectionResult').style.display = 'none';
            $('sectionMath').style.display = 'none';
            $('sectionProof').scrollIntoView({ behavior: 'smooth', block: 'center' });

        } catch (err) {
            console.error(err);
            alert('Lỗi: ' + err.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                Generate Proof
            `;
        }
    }

    async function handleVerify(useFakeProof = false) {
        if (!state.currentProof || !state.publicKey) return;

        let proof = state.currentProof;
        if (useFakeProof) {
            // Tạo proof giả với random values
            proof = {
                t: randomBigInt(P),
                s: randomBigInt(Q),
                c: state.currentProof.c,
            };
        }

        const verifyStart = performance.now();
        const isValid = await SchnorrZKP.verify(state.publicKey, proof);
        state.verifyTime = performance.now() - verifyStart;

        // Result badge
        const resultDiv = $('verifyResult');
        if (isValid) {
            resultDiv.innerHTML = `
                <div class="result result--valid">
                    <div class="result__icon">✅</div>
                    <div class="result__text">
                        <h3>PROOF HỢP LỆ!</h3>
                        <p>Prover đã chứng minh thành công rằng họ biết x sao cho g<sup>x</sup> ≡ h (mod p),
                        mà verifier không biết x là gì.</p>
                    </div>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="result result--invalid">
                    <div class="result__icon">❌</div>
                    <div class="result__text">
                        <h3>PROOF KHÔNG HỢP LỆ!</h3>
                        <p>${useFakeProof 
                            ? 'Proof giả bị từ chối! → Tính SOUNDNESS: không thể tạo proof hợp lệ nếu không biết x.'
                            : 'Proof không hợp lệ — prover không thể chứng minh.'
                        }</p>
                    </div>
                </div>
            `;
        }

        // Metrics
        const proofJson = JSON.stringify({
            t: (useFakeProof ? proof.t : state.currentProof.t).toString(),
            s: (useFakeProof ? proof.s : state.currentProof.s).toString(),
            c: (useFakeProof ? proof.c : state.currentProof.c).toString(),
        });
        const proofSize = new TextEncoder().encode(proofJson).length;

        $('metricProveTime').textContent = state.proveTime.toFixed(1);
        $('metricVerifyTime').textContent = state.verifyTime.toFixed(1);
        $('metricProofSize').textContent = proofSize;
        $('metricRatio').textContent = (state.proveTime / Math.max(state.verifyTime, 0.1)).toFixed(1);

        $('sectionResult').style.display = 'block';

        // Show math details
        showMathDetails(useFakeProof ? proof : state.currentProof, isValid);

        $('sectionResult').scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function showMathDetails(proof, isValid) {
        const lhs = `g^s mod p`;
        const rhs = `t · h^c mod p`;

        $('mathDetails').innerHTML = `
<strong>Schnorr ZKP — Verification Math</strong>

<span style="color: #9494a8;">// Tham số nhóm (RFC 3526 Group 14)</span>
<span style="color: #f59e0b;">p</span> = FFFFFFFF...FFFFFFFF <span style="color: #9494a8;">(2048-bit safe prime)</span>
<span style="color: #f59e0b;">g</span> = 2 <span style="color: #9494a8;">(generator)</span>
<span style="color: #f59e0b;">q</span> = (p - 1) / 2 <span style="color: #9494a8;">(group order)</span>

<span style="color: #9494a8;">// Proof components</span>
<span style="color: #a78bfa;">t</span> (commitment) = ${proof.t.toString(16).substring(0, 40)}...
<span style="color: #a78bfa;">s</span> (response)   = ${proof.s.toString(16).substring(0, 40)}...
<span style="color: #a78bfa;">c</span> (challenge)  = SHA256(g || h || t) mod q

<span style="color: #9494a8;">// Verification equation</span>
<span style="color: #06b6d4;">LHS</span> = g^s mod p
<span style="color: #06b6d4;">RHS</span> = t · h^c mod p

<span style="color: ${isValid ? '#10b981' : '#ef4444'}; font-weight: bold;">LHS ${isValid ? '==' : '!='} RHS → ${isValid ? '✅ VALID' : '❌ INVALID'}</span>

<span style="color: #9494a8;">// Tại sao verification hoạt động?</span>
<span style="color: #9494a8;">// Nếu proof hợp lệ: s = r + c·x (mod q)</span>
<span style="color: #9494a8;">//   g^s = g^(r + c·x) = g^r · g^(c·x) = t · (g^x)^c = t · h^c</span>
<span style="color: #9494a8;">// → LHS = RHS ✅</span>
        `.trim();

        $('sectionMath').style.display = 'block';
    }

    function handleReset() {
        state.currentProof = null;
        state.publicKey = null;
        state.proveTime = 0;
        state.verifyTime = 0;

        $('sectionProof').style.display = 'none';
        $('sectionResult').style.display = 'none';
        $('sectionMath').style.display = 'none';
        $('secretInput').focus();
    }

    // ============================================================
    // EVENT LISTENERS
    // ============================================================

    $('btnProve').addEventListener('click', handleProve);
    $('btnVerify').addEventListener('click', () => handleVerify(false));
    $('btnFakeVerify').addEventListener('click', () => handleVerify(true));
    $('btnReset').addEventListener('click', handleReset);

    $('secretInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleProve();
    });

})();
