"""
original_app.py - BASELINE VERSION (Week 4 Task)
Sales Data Analyzer with INTENTIONAL performance bottlenecks.
Processes a generated dataset (self-contained, no external files).

Bottlenecks present:
1. O(n^2) duplicate check using list membership
2. String concatenation with += in loop (quadratic copy)
3. Redundant recomputation of sum/count inside loops
4. Repeated linear searches for top-N items
5. Re-reading/re-filtering the full list many times
"""

import random
import time


def generate_data(n=8000):
    """Generate sales records with some duplicates (deterministic)."""
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
    # inject duplicate ids to make duplicate detection meaningful
    for i in range(0, n // 10):
        records.append(dict(records[i]))
    return records


def find_duplicates(records):
    """BOTTLENECK 1: O(n^2) - nested loop + list membership scan."""
    dup_ids = []
    seen_list = []
    for r in records:
        # linear scan over ever-growing list -> quadratic overall
        found = False
        for s in seen_list:
            if s == r["id"]:
                found = True
                break
        if found:
            if r["id"] not in dup_ids:  # another linear scan
                dup_ids.append(r["id"])
        else:
            seen_list.append(r["id"])
    return dup_ids


def total_amount(records):
    """BOTTLENECK 3: recomputes running totals redundantly."""
    total = 0.0
    count = 0
    for i in range(len(records)):
        total = total + records[i]["amount"]
        count = count + 1
        # redundant inner recomputation every iteration (pointless work)
        temp = 0.0
        for j in range(0, i + 1):
            temp = temp + records[j]["amount"]
        if temp != total:
            pass
    return total, count


def region_summary(records):
    """BOTTLENECK 5: re-filters full list once per region."""
    regions = ["North", "South", "East", "West"]
    summary = {}
    for reg in regions:
        s = 0.0
        c = 0
        for r in records:                      # full scan per region
            if r["region"] == reg:
                s = s + r["amount"]
                c = c + 1
        summary[reg] = (s, c)
    return summary


def top_customers(records, k=10):
    """BOTTLENECK 4: recomputes per-customer totals with repeated searches."""
    totals = []
    names = []
    for r in records:
        # search customer in names list -> O(n) each -> O(n^2) overall
        idx = -1
        for i in range(len(names)):
            if names[i] == r["customer"]:
                idx = i
                break
        if idx == -1:
            names.append(r["customer"])
            totals.append(r["amount"])
        else:
            totals[idx] = totals[idx] + r["amount"]
    # selection sort top k (O(n^2) style)
    top_names, top_vals = [], []
    used = [False] * len(names)
    for _ in range(k):
        best = -1
        for i in range(len(names)):
            if not used[i] and (best == -1 or totals[i] > totals[best]):
                best = i
        used[best] = True
        top_names.append(names[best])
        top_vals.append(totals[best])
    return top_names, top_vals


def build_report(records, dup_ids, total, count, summary, top_names, top_vals):
    """BOTTLENECK 2: quadratic string concatenation with +=."""
    report = ""
    report = report + "=== SALES ANALYSIS REPORT ===\n"
    report = report + "Records: " + str(count) + "\n"
    report = report + "Total Amount: " + str(round(total, 2)) + "\n"
    report = report + "Duplicate IDs: " + str(len(dup_ids)) + "\n"
    report = report + "--- Region Summary ---\n"
    for reg in sorted(summary.keys()):
        report = report + reg + ": total=" + str(round(summary[reg][0], 2))
        report = report + " count=" + str(summary[reg][1]) + "\n"
    report = report + "--- Top Customers ---\n"
    for i in range(len(top_names)):
        report = report + str(i + 1) + ". " + top_names[i]
        report = report + " - " + str(round(top_vals[i], 2)) + "\n"
    return report


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
    print(f"[BASELINE] Analysis time: {elapsed:.4f} sec")
    return elapsed


if __name__ == "__main__":
    main()
