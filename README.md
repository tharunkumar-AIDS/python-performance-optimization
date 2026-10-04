# Week 4 – Performance Optimization in Python Applications

## 1. The Application
Sales Data Analyzer (self-contained, generates its own data — no external input files):
- `original_app.py` – baseline version with intentional bottlenecks
- `optimized_app.py` – same functionality, optimized
- `benchmark.py` – cProfile + timeit before/after comparison
- `benchmark_results.txt` – real measured results from my machine

Dataset: 8,800 records (8,000 + 800 injected duplicates), seed fixed → both versions process identical data.

## 2. How to Run
```bash
cd Week4_Optimization
python original_app.py     # baseline
python optimized_app.py    # optimized
python benchmark.py        # full comparison -> benchmark_results.txt
```
Python 3.8+, standard library only.

## 3. Baseline Profile (cProfile) — Bottlenecks Identified
Total (with profiler): **11.741 s**

| Function | cumtime | % of app | Problem |
|---|---|---|---|
| total_amount | 5.256 s | 45% | recomputes running sum inside loop → O(n²) |
| top_customers | 3.717 s | 32% | linear list search per record + selection sort → O(n²) |
| find_duplicates | 2.661 s | 23% | list membership scan → O(n²) |
| region_summary | 0.002 s | <1% | 4 full scans, not a bottleneck |
| string building (`+=`) | small at this size | — | quadratic memory copying, scales badly |

## 4. Optimizations Applied (functionality unchanged)
1. **set() membership** for duplicate detection → O(n)
2. **sum() + len()** built-ins, removed redundant recompute → O(n) (this was the 45% hotspot)
3. **defaultdict single pass** — build all region totals in one loop instead of 4 scans; also aggregates customers in the same loop → uses built-in `collections`
4. **heapq.nlargest(k, ...)** for Top-10 → O(n log k) instead of O(n²) selection sort
5. **list.append + str.join** instead of `+=` string concatenation → avoids repeated object copying
6. **Refactor:** removed dead code (`temp` recompute, `if temp != total: pass`), clear one-pass structure

## 5. Before/After Benchmarks (measured, benchmark_results.txt)
**Whole app (best of 3):** Baseline 3.8829 s → Optimized 0.0053 s = **733.8x faster, 99.9% time reduced**

**timeit per function:**
| Function | Baseline | Optimized | Speedup |
|---|---|---|---|
| find_duplicates | 0.8257 s | 0.0010 s | 851x |
| total_amount | 2.1437 s | 0.0004 s | 5342x |
| top_customers | 0.9256 s | 0.0027 s | 345x |
| region_summary | 0.0016 s | 0.0020 s | ~parity (both O(n), sub-ms noise) |

**cProfile total:** 11.741 s → 0.267 s (remaining time is just data generation).

## 6. Final Verification
`benchmark.py` runs `correctness_check()`: duplicates, totals, region summary and top-10 outputs of both versions compared → **PASS (identical results)**. Report values in both runs are byte-for-byte equal.

## 7. Report
See `Week4_Optimization_Report.docx` for full documentation: identified issues, profiling data, strategies, benchmarks and verification.
