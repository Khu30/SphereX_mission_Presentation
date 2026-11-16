"""
test_benchmarks.py
Executes Step 5 Verification & Target Benchmark Suite:
1. Barnard's Star (High proper-motion star tracking)
2. Epsilon Indi B (Brown dwarf binary spectral resolution)
3. WISE 0855 (Coldest Y-dwarf tracking @ RA 08h55m10.831s, Dec -7d14m42.53s)
4. RW Aurigae (Time-series brightness tracking for eruptive variable)
5. R Draconis (Time-series periodic tracking for pulsating Mira variable)
"""

import sys
from benchmark_suite import run_full_benchmark_suite


def main():
    print("=" * 70)
    print("NASA SPHEREx HACKATHON: STEP 5 BENCHMARK VERIFICATION SUITE")
    print("=" * 70)

    suite_results = run_full_benchmark_suite()

    print(f"\nSuite Name: {suite_results['suite_name']}")
    print(f"Overall Status: {suite_results['status']}")
    print(f"Passed: {suite_results['passed_benchmarks']} / {suite_results['total_benchmarks']} ({suite_results['pass_rate_pct']}%)")
    print("-" * 70)

    for idx, bench in enumerate(suite_results["benchmark_results"], 1):
        status_symbol = "[PASS]" if bench["status"] == "PASSED" else "[FAIL]"
        print(f"\n{idx}. {bench['target_name']} {status_symbol}")
        print(f"   Test Category: {bench['test_type']}")
        print(f"   Verdict: {bench['scientific_verdict']}")
        print("   Key Metrics:")
        for k, v in bench["metrics"].items():
            print(f"     - {k}: {v}")

    print("\n" + "=" * 70)
    if suite_results["status"] == "ALL_BENCHMARKS_PASSED":
        print("ALL 5 BENCHMARK VERIFICATION TESTS PASSED SUCCESSFULLY.")
        print("=" * 70)
        return 0
    else:
        print("WARNING: SOME TESTS FAILED.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
