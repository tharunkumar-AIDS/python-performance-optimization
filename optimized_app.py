"""
optimized_app.py - OPTIMIZED VERSION (Week 4 Task)
Same functionality as original_app.py with performance optimizations:

Optimizations applied:
1. set() for duplicate detection -> O(n) instead of O(n^2)
2. str.join / list of lines instead of += concatenation -> O(n)
3. Single-pass aggregation with dict (built-in library collections.Counter-like)
   -> removes redundant recomputations
4. heapq.nlargest for top-N -> O(n log k) instead of O(n^2) selection sort
5. One pass builds ALL summaries (region + customer) instead of re-filtering

Result: identical output, big speedup.
"""

import random
import time
import heapq
from collections import defaultdict


def generate_data(n=8000):
    """Identical data generation (same seed => same data as baseline)."""
    random.seed(42)
    regions = ["North", "South", "East", "West"]
    records = []
    for i in range(n):
        records.append({
            "id": i,
            "customer": "CUST" + str(random.randint(1, 8000)),
            "region": regions[random.randint(0, 3)],
            "amount": round(random.uniform(10, 1000), 2),
            "product": "P" + str(random.randint(1, 500))
        })
    for i in range(0, n // 10):
        records.append(dict(records[i]))
    return records


def find_duplicates(records):
    """OPT 1: set membership O(1) -> overall O(n)."""
    seen = set()
    dup_ids = set()
    for r in records:
        rid = r["id"]
        if rid in seen:
            dup_ids.add(rid)
        else:
            seen.add(rid)
    return sorted(dup_ids)


def total_amount(records):
    """OPT 3: sum() built-in, one pass, no redundant recompute."""
    total = sum(r["amount"] for r in records)   # generator, no temp list
    count = len(records)                        # O(1) instead of counting loop
    return total, count


def region_summary(records):
    """OPT 5a: single pass with defaultdict instead of 4 full scans."""
    sums = defaultdict(float)
    counts = defaultdict(int)
    for r in records:
        sums[r["region"]] += r["amount"]
        counts[r["region"]] += 1
    return {reg: (sums[reg], counts[reg])
            for reg in ("North", "South", "East", "West")}


def top_customers(records, k=10):
    """OPT 4+5b: one pass dict agg + heapq.nlargest O(n log k)."""
    totals = defaultdict(float)
    for r in records:
        totals[r["customer"]] += r["amount"]
    top = heapq.nlargest(k, totals.items(), key=lambda x: x[1])
    top_names = [name for name, _ in top]
    top_vals = [val for _, val in top]
    return top_names, top_vals


def build_report(records, dup_ids, total, count, summary, top_names, top_vals):
    """OPT 2: collect lines in list, single str.join at end."""
    lines = []
    lines.append("=== SALES ANALYSIS REPORT ===")
    lines.append("Records: " + str(count))
    lines.append("Total Amount: " + str(round(total, 2)))
    lines.append("Duplicate IDs: " + str(len(dup_ids)))
    lines.append("--- Region Summary ---")
    for reg in sorted(summary.keys()):
        lines.append(reg + ": total=" + str(round(summary[reg][0], 2))
                     + " count=" + str(summary[reg][1]))
    lines.append("--- Top Customers ---")
    for i in range(len(top_names)):
        lines.append(str(i + 1) + ". " + top_names[i]
                     + " - " + str(round(top_vals[i], 2)))
    return "\n".join(lines) + "\n"


def main():
    print("Generating data...")
    records = generate_data(8000)
    start = time.perf_counter()

    dup_ids = find_duplicates(records)
    total, count = total_amount(records)
    summary = region_summary(records)
    top_names, top_vals = top_customers(records, 10)
    report = build_report(records, dup_ids, total, count, summary,
                          top_names, top_vals)

    elapsed = time.perf_counter() - start
    print(report)
    print(f"[OPTIMIZED] Analysis time: {elapsed:.4f} sec")
    return elapsed


if __name__ == "__main__":
    main()
