#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
  BENCHMARK — So sánh hiệu năng Zero-Knowledge Proof
============================================================
  Chạy prove + verify nhiều lần, tính trung bình,
  so sánh kích thước proof và thời gian.

  Sử dụng:
    python benchmark.py

  Tùy chọn (cần matplotlib):
    pip install matplotlib
============================================================
"""

import json
import sys
import os
import time

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


# Import ZKP classes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schnorr_zkp import SchnorrZKP, HashCommitmentZKP

# ============================================================
# CẤU HÌNH
# ============================================================

NUM_RUNS = 20  # Số lần chạy benchmark
TEST_SECRETS = ["12345", "hello_world", "zerocash_demo_kma", "a" * 100]


def benchmark_schnorr(num_runs=NUM_RUNS):
    """Benchmark Schnorr ZKP."""
    zkp = SchnorrZKP()
    prove_times = []
    verify_times = []
    proof_sizes = []

    for i in range(num_runs):
        secret = TEST_SECRETS[i % len(TEST_SECRETS)]
        x, h = zkp.keygen(secret)

        # Prove
        start = time.perf_counter()
        proof = zkp.prove(x, h)
        prove_times.append((time.perf_counter() - start) * 1000)

        # Proof size
        proof_sizes.append(len(json.dumps(proof).encode("utf-8")))

        # Verify
        start = time.perf_counter()
        is_valid = zkp.verify(h, proof)
        verify_times.append((time.perf_counter() - start) * 1000)

        assert is_valid, f"Run {i+1}: Proof should be valid!"

    return prove_times, verify_times, proof_sizes


def benchmark_hash_commitment(num_runs=NUM_RUNS, num_rounds=20):
    """Benchmark Hash Commitment ZKP."""
    zkp = HashCommitmentZKP(num_rounds=num_rounds)
    prove_times = []
    verify_times = []
    proof_sizes = []

    for i in range(num_runs):
        secret = TEST_SECRETS[i % len(TEST_SECRETS)]
        y = zkp.hash(secret)

        # Prove
        start = time.perf_counter()
        proof = zkp.prove(secret)
        prove_times.append((time.perf_counter() - start) * 1000)

        # Proof size
        proof_sizes.append(len(json.dumps(proof).encode("utf-8")))

        # Verify
        start = time.perf_counter()
        is_valid = zkp.verify(y, proof, secret_for_check=secret)
        verify_times.append((time.perf_counter() - start) * 1000)

        assert is_valid, f"Run {i+1}: Proof should be valid!"

    return prove_times, verify_times, proof_sizes


def stats(data):
    """Tính thống kê cơ bản."""
    n = len(data)
    avg = sum(data) / n
    sorted_d = sorted(data)
    median = sorted_d[n // 2] if n % 2 else (sorted_d[n // 2 - 1] + sorted_d[n // 2]) / 2
    min_val = min(data)
    max_val = max(data)
    variance = sum((x - avg) ** 2 for x in data) / n
    std_dev = variance ** 0.5
    return {
        "avg": avg,
        "median": median,
        "min": min_val,
        "max": max_val,
        "std": std_dev,
    }


def print_results(name, prove_times, verify_times, proof_sizes):
    """In kết quả benchmark."""
    prove_stats = stats(prove_times)
    verify_stats = stats(verify_times)
    size_stats = stats(proof_sizes)

    print(f"\n  {'─' * 58}")
    print(f"  📊 {name}")
    print(f"  {'─' * 58}")

    print(f"\n  ⏱️  Thời gian Prove (ms):")
    print(f"    Trung bình:  {prove_stats['avg']:>10.3f} ms")
    print(f"    Median:      {prove_stats['median']:>10.3f} ms")
    print(f"    Min:         {prove_stats['min']:>10.3f} ms")
    print(f"    Max:         {prove_stats['max']:>10.3f} ms")
    print(f"    Std Dev:     {prove_stats['std']:>10.3f} ms")

    print(f"\n  ⏱️  Thời gian Verify (ms):")
    print(f"    Trung bình:  {verify_stats['avg']:>10.3f} ms")
    print(f"    Median:      {verify_stats['median']:>10.3f} ms")
    print(f"    Min:         {verify_stats['min']:>10.3f} ms")
    print(f"    Max:         {verify_stats['max']:>10.3f} ms")

    print(f"\n  📦 Kích thước Proof:")
    print(f"    Trung bình:  {size_stats['avg']:>10.0f} bytes")
    print(f"    Min:         {size_stats['min']:>10.0f} bytes")
    print(f"    Max:         {size_stats['max']:>10.0f} bytes")

    ratio = prove_stats["avg"] / max(verify_stats["avg"], 0.0001)
    print(f"\n  📈 Tỷ lệ Prove/Verify: {ratio:.1f}x")

    return prove_stats, verify_stats, size_stats


def create_charts(schnorr_data, hash_data):
    """Tạo biểu đồ benchmark."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n  ⚠️  matplotlib chưa cài. Bỏ qua tạo biểu đồ.")
        print("     Cài đặt: pip install matplotlib")
        return

    s_prove, s_verify, s_sizes = schnorr_data
    h_prove, h_verify, h_sizes = hash_data

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Zero-Knowledge Proof Benchmark\n"
        "Schnorr ZKP vs Hash Commitment ZKP",
        fontsize=14,
        fontweight="bold",
    )

    colors_s = "#7c3aed"
    colors_h = "#06b6d4"

    # --- Chart 1: Prove Time comparison ---
    ax1 = axes[0][0]
    ax1.bar(
        ["Schnorr\nZKP", "Hash\nCommitment"],
        [stats(s_prove)["avg"], stats(h_prove)["avg"]],
        color=[colors_s, colors_h],
        width=0.5,
        edgecolor="white",
    )
    ax1.set_title("Thời gian Prove (trung bình)", fontweight="bold")
    ax1.set_ylabel("ms")
    for i, v in enumerate([stats(s_prove)["avg"], stats(h_prove)["avg"]]):
        ax1.text(i, v + max(stats(s_prove)["avg"], stats(h_prove)["avg"]) * 0.03,
                f"{v:.2f}ms", ha="center", fontweight="bold", fontsize=10)

    # --- Chart 2: Verify Time comparison ---
    ax2 = axes[0][1]
    ax2.bar(
        ["Schnorr\nZKP", "Hash\nCommitment"],
        [stats(s_verify)["avg"], stats(h_verify)["avg"]],
        color=[colors_s, colors_h],
        width=0.5,
        edgecolor="white",
    )
    ax2.set_title("Thời gian Verify (trung bình)", fontweight="bold")
    ax2.set_ylabel("ms")
    for i, v in enumerate([stats(s_verify)["avg"], stats(h_verify)["avg"]]):
        ax2.text(i, v + max(stats(s_verify)["avg"], stats(h_verify)["avg"]) * 0.03,
                f"{v:.2f}ms", ha="center", fontweight="bold", fontsize=10)

    # --- Chart 3: Proof Size comparison ---
    ax3 = axes[1][0]
    ax3.bar(
        ["Schnorr\nZKP", "Hash\nCommitment"],
        [stats(s_sizes)["avg"], stats(h_sizes)["avg"]],
        color=[colors_s, colors_h],
        width=0.5,
        edgecolor="white",
    )
    ax3.set_title("Kích thước Proof (trung bình)", fontweight="bold")
    ax3.set_ylabel("bytes")
    for i, v in enumerate([stats(s_sizes)["avg"], stats(h_sizes)["avg"]]):
        ax3.text(i, v + max(stats(s_sizes)["avg"], stats(h_sizes)["avg"]) * 0.03,
                f"{v:.0f}B", ha="center", fontweight="bold", fontsize=10)

    # --- Chart 4: Time distribution (box plot) ---
    ax4 = axes[1][1]
    bp = ax4.boxplot(
        [s_prove, s_verify, h_prove, h_verify],
        labels=["Schnorr\nProve", "Schnorr\nVerify", "Hash\nProve", "Hash\nVerify"],
        patch_artist=True,
    )
    box_colors = [colors_s, colors_s, colors_h, colors_h]
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax4.set_title(f"Phân bố thời gian ({NUM_RUNS} lần)", fontweight="bold")
    ax4.set_ylabel("ms")

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_results.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\n  📊 Biểu đồ đã lưu: {output_path}")


def main():
    print()
    print("=" * 62)
    print("  🔬 BENCHMARK — Zero-Knowledge Proof")
    print("=" * 62)
    print(f"  Số lần chạy: {NUM_RUNS}")
    print(f"  Test secrets: {len(TEST_SECRETS)} giá trị khác nhau")
    print("=" * 62)

    # Benchmark Schnorr
    print("\n  🔄 Đang benchmark Schnorr ZKP...")
    s_prove, s_verify, s_sizes = benchmark_schnorr()
    s_stats = print_results("SCHNORR ZKP (Discrete Log)", s_prove, s_verify, s_sizes)

    # Benchmark Hash Commitment
    print("\n  🔄 Đang benchmark Hash Commitment ZKP...")
    h_prove, h_verify, h_sizes = benchmark_hash_commitment()
    h_stats = print_results("HASH COMMITMENT ZKP (SHA-256)", h_prove, h_verify, h_sizes)

    # Bảng so sánh tổng hợp
    print(f"\n  {'=' * 58}")
    print(f"  📊 BẢNG SO SÁNH TỔNG HỢP")
    print(f"  {'=' * 58}")
    print(f"  {'Metric':<28} {'Schnorr':>12} {'Hash Commit':>12}")
    print(f"  {'─' * 52}")

    sp, sv, ss = stats(s_prove), stats(s_verify), stats(s_sizes)
    hp, hv, hs = stats(h_prove), stats(h_verify), stats(h_sizes)

    print(f"  {'Prove TB (ms)':<28} {sp['avg']:>12.3f} {hp['avg']:>12.3f}")
    print(f"  {'Verify TB (ms)':<28} {sv['avg']:>12.3f} {hv['avg']:>12.3f}")
    print(f"  {'Proof Size TB (bytes)':<28} {ss['avg']:>12.0f} {hs['avg']:>12.0f}")
    print(f"  {'Prove/Verify Ratio':<28} {sp['avg']/max(sv['avg'],0.0001):>12.1f}x {hp['avg']/max(hv['avg'],0.0001):>12.1f}x")
    print(f"  {'─' * 52}")

    print(f"\n  💡 PHÂN TÍCH:")
    print(f"  • Schnorr ZKP: proof nhỏ gọn (~{ss['avg']:.0f} bytes), dựa trên Discrete Log")
    print(f"  • Hash Commitment: proof lớn hơn (~{hs['avg']:.0f} bytes) do nhiều rounds")
    print(f"  • Prove luôn chậm hơn Verify — đặc trưng của ZKP")
    print(f"  • Trong Zerocash: dùng zk-SNARKs (Groth16) với proof chỉ ~200 bytes")

    # Tạo biểu đồ
    create_charts(
        (s_prove, s_verify, s_sizes),
        (h_prove, h_verify, h_sizes),
    )

    print(f"\n  {'=' * 58}")
    print(f"  🎉 Benchmark hoàn tất! ({NUM_RUNS} runs × 2 protocols)")
    print(f"  {'=' * 58}")
    print()


if __name__ == "__main__":
    main()
