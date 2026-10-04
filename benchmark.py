"""
benchmark.py - Baseline vs Optimized comparison
Uses cProfile (profiling) + timeit/time.perf_counter (benchmarks).
Run: python benchmark.py
Outputs: benchmark_results.txt with before/after numbers.
"""

import cProfile
import pstats
import io
import time
import timeit

import original_app as orig
import optimized_app as opt


def profile_module(mod, label, outfile):
    """Run cProfile on mod.main() and write top functions to file."""
    pr = cProfile.Profile()
    pr.enable()
    mod.main()
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(12)
    text = s.getvalue()
    outfile.write(f"\n{'='*60}\ncProfile - {label}\n{'='*60}\n")
    outfile.write(text)
    return text


def timed_runs(mod, n=2):
    """Return best wall-clock time of n runs of main()."""
    times = []
    for _ in range(n):
        t = mod.main()
        times.append(t)
    return min(times)


def timeit_section():
    """timeit comparison of the heaviest functions directly."""
    recs_o = orig.generate_data(8000)
    recs_n = opt.generate_data(8000)
    results = {}
    results["find_duplicates"] = (
        min(timeit.repeat(lambda: orig.find_duplicates(recs_o), number=1, repeat=2)),
        min(timeit.repeat(lambda: opt.find_duplicates(recs_n), number=1, repeat=2)),
    )
    results["total_amount"] = (
        min(timeit.repeat(lambda: orig.total_amount(recs_o), number=1, repeat=2)),
        min(timeit.repeat(lambda: opt.total_amount(recs_n), number=1, repeat=2)),
    )
    results["region_summary"] = (
        min(timeit.repeat(lambda: orig.region_summary(recs_o), number=1, repeat=2)),
        min(timeit.repeat(lambda: opt.region_summary(recs_n), number=1, repeat=2)),
    )
    results["top_customers"] = (
        min(timeit.repeat(lambda: orig.top_customers(recs_o), number=1, repeat=2)),
        min(timeit.repeat(lambda: opt.top_customers(recs_n), number=1, repeat=2)),
    )
    return results


def correctness_check():
    """Verify optimized == baseline outputs (same functionality)."""
    a = orig.generate_data(5000)
    b = opt.generate_data(5000)
    assert sorted(orig.find_duplicates(a)) == opt.find_duplicates(b)
    ta, ca = orig.total_amount(a)
    tb, cb = opt.total_amount(b)
    assert abs(ta - tb) < 0.01 and ca == cb
    sa = orig.region_summary(a)
    sb = opt.region_summary(b)
    for k in sa:
        assert abs(sa[k][0] - sb[k][0]) < 0.01 and sa[k][1] == sb[k][1]
    na, va = orig.top_customers(a, 10)
    nb, vb = opt.top_customers(b, 10)
    assert sorted(na) == sorted(nb)
    return True


def main():
    with open("benchmark_results.txt", "w", encoding="utf-8") as f:
        f.write("WEEK 4 - PERFORMANCE BENCHMARK RESULTS\n")
        f.write("=" * 60 + "\n")

        # 1. Correctness first
        correctness_check()
        f.write("Correctness: optimized output == baseline output -> PASS\n\n")

        # 2. Wall clock (best of 3)
        print("Timing baseline...")
        t_base = timed_runs(orig, 3)
        print("Timing optimized...")
        t_opt = timed_runs(opt, 3)
        speedup = t_base / t_opt if t_opt > 0 else 0
        f.write("--- Whole-App Wall Clock (best of 3) ---\n")
        f.write(f"Baseline : {t_base:.4f} sec\n")
        f.write(f"Optimized: {t_opt:.4f} sec\n")
        f.write(f"Speedup  : {speedup:.1f}x faster "
                f"({(1 - t_opt/t_base)*100:.1f}% time reduced)\n\n")

        # 3. timeit per function
        f.write("--- timeit per function (best of 3) ---\n")
        f.write(f"{'function':22} {'baseline':>10} {'optimized':>10} {'speedup':>8}\n")
        sec = timeit_section()
        for name, (b, o) in sec.items():
            sp = b / o if o > 0 else 0
            f.write(f"{name:22} {b:9.4f}s {o:9.4f}s {sp:7.1f}x\n")

        # 4. cProfile snapshots
        profile_module(orig, "BASELINE original_app.py", f)
        profile_module(opt, "OPTIMIZED optimized_app.py", f)

        # 5. Memory hint via sys.getsizeof on biggest structures
        f.write("\nDone. See report for analysis.\n")

    print("benchmark_results.txt written.")


if __name__ == "__main__":
    main()
