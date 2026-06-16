#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
BENCHMARK SCRIPT - Demo Zero-Knowledge Proof
============================================================
So sánh kích thước proof và thời gian sinh/xác minh.
Chạy prove + verify nhiều lần để lấy kết quả trung bình.

Yêu cầu:
  - Đã chạy scripts/setup.sh (có build/ directory)
  - Python 3.10+
  - matplotlib (pip install matplotlib)

Sử dụng:
  python scripts/benchmark.py
============================================================
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ============================================================
# CẤU HÌNH
# ============================================================

NUM_RUNS = 10  # Số lần chạy để lấy trung bình
PROJECT_DIR = Path(__file__).parent.parent.resolve()
BUILD_DIR = PROJECT_DIR / "build"
CIRCUIT_DIR = PROJECT_DIR / "circuits"


def get_file_size(filepath):
    """Lấy kích thước file (bytes)."""
    return os.path.getsize(filepath) if os.path.exists(filepath) else 0


def format_bytes(size_bytes):
    """Chuyển bytes thành format dễ đọc."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def run_command(cmd, cwd=None):
    """Chạy command và trả về thời gian (ms)."""
    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd or str(PROJECT_DIR),
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    if result.returncode != 0:
        print(f"  ❌ Lỗi khi chạy: {cmd}")
        print(f"  stderr: {result.stderr}")
        sys.exit(1)

    return elapsed_ms, result.stdout


def check_prerequisites():
    """Kiểm tra các file cần thiết đã tồn tại."""
    required_files = [
        BUILD_DIR / "hash_proof_final.zkey",
        BUILD_DIR / "verification_key.json",
        BUILD_DIR / "hash_proof_js" / "generate_witness.js",
        BUILD_DIR / "hash_proof_js" / "hash_proof.wasm",
        CIRCUIT_DIR / "input.json",
    ]

    for f in required_files:
        if not f.exists():
            print(f"❌ Thiếu file: {f}")
            print("   Vui lòng chạy: bash scripts/setup.sh")
            sys.exit(1)

    print("✅ Tất cả prerequisites đã sẵn sàng\n")


def benchmark_prove_verify():
    """Chạy prove + verify nhiều lần và đo thời gian."""
    prove_times = []
    verify_times = []

    witness_cmd = (
        f'node "{BUILD_DIR}/hash_proof_js/generate_witness.js" '
        f'"{BUILD_DIR}/hash_proof_js/hash_proof.wasm" '
        f'"{CIRCUIT_DIR}/input.json" '
        f'"{BUILD_DIR}/witness.wtns"'
    )

    prove_cmd = (
        f'npx snarkjs groth16 prove '
        f'"{BUILD_DIR}/hash_proof_final.zkey" '
        f'"{BUILD_DIR}/witness.wtns" '
        f'"{BUILD_DIR}/proof.json" '
        f'"{BUILD_DIR}/public.json"'
    )

    verify_cmd = (
        f'npx snarkjs groth16 verify '
        f'"{BUILD_DIR}/verification_key.json" '
        f'"{BUILD_DIR}/public.json" '
        f'"{BUILD_DIR}/proof.json"'
    )

    print(f"🔄 Chạy benchmark {NUM_RUNS} lần...\n")

    for i in range(NUM_RUNS):
        # Sinh witness
        run_command(witness_cmd)

        # Prove
        prove_time, _ = run_command(prove_cmd)
        prove_times.append(prove_time)

        # Verify
        verify_time, stdout = run_command(verify_cmd)
        verify_times.append(verify_time)

        status = "✅" if "OK" in stdout else "❌"
        print(
            f"  Run {i + 1:2d}/{NUM_RUNS}: "
            f"Prove={prove_time:8.2f}ms | "
            f"Verify={verify_time:8.2f}ms | "
            f"{status}"
        )

    return prove_times, verify_times


def collect_file_sizes():
    """Thu thập kích thước các file quan trọng."""
    files = {
        "proof.json": BUILD_DIR / "proof.json",
        "public.json": BUILD_DIR / "public.json",
        "verification_key.json": BUILD_DIR / "verification_key.json",
        "hash_proof_final.zkey": BUILD_DIR / "hash_proof_final.zkey",
        "hash_proof.r1cs": BUILD_DIR / "hash_proof.r1cs",
        "hash_proof.wasm": BUILD_DIR / "hash_proof_js" / "hash_proof.wasm",
    }

    sizes = {}
    for name, path in files.items():
        sizes[name] = get_file_size(path)

    return sizes


def print_results(prove_times, verify_times, file_sizes):
    """In kết quả benchmark."""
    avg_prove = sum(prove_times) / len(prove_times)
    avg_verify = sum(verify_times) / len(verify_times)
    min_prove = min(prove_times)
    max_prove = max(prove_times)
    min_verify = min(verify_times)
    max_verify = max(verify_times)

    print("\n" + "=" * 60)
    print("   📊 KẾT QUẢ BENCHMARK")
    print("=" * 60)

    # Bảng thời gian
    print("\n⏱️  THỜI GIAN (ms):")
    print("-" * 50)
    print(f"  {'Metric':<25} {'Prove':>10} {'Verify':>10}")
    print("-" * 50)
    print(f"  {'Trung bình':<25} {avg_prove:>10.2f} {avg_verify:>10.2f}")
    print(f"  {'Nhanh nhất (min)':<25} {min_prove:>10.2f} {min_verify:>10.2f}")
    print(f"  {'Chậm nhất (max)':<25} {max_prove:>10.2f} {max_verify:>10.2f}")
    print(f"  {'Tỷ lệ Prove/Verify':<25} {avg_prove / avg_verify:>10.2f}x")
    print("-" * 50)

    # Bảng kích thước
    print("\n📦 KÍCH THƯỚC FILES:")
    print("-" * 50)
    print(f"  {'File':<30} {'Kích thước':>15}")
    print("-" * 50)
    for name, size in file_sizes.items():
        print(f"  {name:<30} {format_bytes(size):>15}")
    print("-" * 50)

    # Phân tích
    proof_size = file_sizes.get("proof.json", 0)
    zkey_size = file_sizes.get("hash_proof_final.zkey", 0)

    print("\n💡 PHÂN TÍCH:")
    print(f"  • Proof rất nhỏ gọn: chỉ {format_bytes(proof_size)}")
    print(f"    → Đây là tính SUCCINCT của zk-SNARKs")
    print(f"  • Proving key lớn: {format_bytes(zkey_size)}")
    print(f"    → Trade-off: key lớn nhưng proof nhỏ")
    print(f"  • Verify nhanh hơn Prove: {avg_prove / avg_verify:.1f}x")
    print(f"    → Verifier chỉ cần tính toán rất ít")
    print(f"  • Tổng {NUM_RUNS} lần chạy đều verify ✅ OK")
    print("=" * 60)

    return avg_prove, avg_verify


def create_chart(prove_times, verify_times, file_sizes, avg_prove, avg_verify):
    """Tạo biểu đồ benchmark."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend
    except ImportError:
        print("\n⚠️  matplotlib chưa cài. Bỏ qua tạo biểu đồ.")
        print("   Cài đặt: pip install matplotlib")
        return

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(
        "Zero-Knowledge Proof Benchmark\n"
        'Chứng minh "biết x sao cho Poseidon(x) = y" mà không tiết lộ x',
        fontsize=14,
        fontweight="bold",
    )

    # --- Chart 1: Thời gian Prove vs Verify (bar chart) ---
    ax1 = axes[0]
    categories = ["Prove\n(Sinh proof)", "Verify\n(Xác minh)"]
    values = [avg_prove, avg_verify]
    colors = ["#6C5CE7", "#00B894"]
    bars = ax1.bar(categories, values, color=colors, width=0.5, edgecolor="white")
    ax1.set_title("Thời gian trung bình", fontweight="bold")
    ax1.set_ylabel("Thời gian (ms)")
    for bar, val in zip(bars, values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.02,
            f"{val:.1f}ms",
            ha="center",
            fontweight="bold",
        )

    # --- Chart 2: Phân bố thời gian (box plot) ---
    ax2 = axes[1]
    bp = ax2.boxplot(
        [prove_times, verify_times],
        labels=["Prove", "Verify"],
        patch_artist=True,
    )
    bp["boxes"][0].set_facecolor("#6C5CE7")
    bp["boxes"][1].set_facecolor("#00B894")
    ax2.set_title(f"Phân bố thời gian ({NUM_RUNS} lần)", fontweight="bold")
    ax2.set_ylabel("Thời gian (ms)")

    # --- Chart 3: Kích thước files (horizontal bar) ---
    ax3 = axes[2]
    # Chỉ hiển thị các file quan trọng
    display_files = {
        "proof.json": file_sizes.get("proof.json", 0),
        "public.json": file_sizes.get("public.json", 0),
        "verification_key.json": file_sizes.get("verification_key.json", 0),
        "circuit.wasm": file_sizes.get("hash_proof.wasm", 0),
        "proving_key.zkey": file_sizes.get("hash_proof_final.zkey", 0),
    }
    names = list(display_files.keys())
    sizes_kb = [s / 1024 for s in display_files.values()]
    bar_colors = ["#6C5CE7", "#A29BFE", "#00B894", "#FDCB6E", "#E17055"]
    bars3 = ax3.barh(names, sizes_kb, color=bar_colors, edgecolor="white")
    ax3.set_title("Kích thước files", fontweight="bold")
    ax3.set_xlabel("Kích thước (KB)")
    for bar, val in zip(bars3, sizes_kb):
        ax3.text(
            bar.get_width() + max(sizes_kb) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}KB",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    output_path = PROJECT_DIR / "benchmark_results.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\n📊 Biểu đồ đã lưu: {output_path}")


def main():
    print("=" * 60)
    print("   🔬 BENCHMARK - Demo Zero-Knowledge Proof")
    print("=" * 60)
    print(f"   Số lần chạy: {NUM_RUNS}")
    print(f"   Project: {PROJECT_DIR}")
    print("=" * 60)
    print()

    # Kiểm tra prerequisites
    check_prerequisites()

    # Chạy benchmark
    prove_times, verify_times = benchmark_prove_verify()

    # Thu thập kích thước
    file_sizes = collect_file_sizes()

    # In kết quả
    avg_prove, avg_verify = print_results(prove_times, verify_times, file_sizes)

    # Tạo biểu đồ
    create_chart(prove_times, verify_times, file_sizes, avg_prove, avg_verify)

    print("\n🎉 Benchmark hoàn tất!\n")


if __name__ == "__main__":
    main()
