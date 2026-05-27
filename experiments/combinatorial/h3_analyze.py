"""h3_analyze: post-process h3_pair_minima.json into the final table and
structural observations.

This is the analysis step. Run after h3_enumerate_pairs.py finishes (or
mid-run, since h3_enumerate_pairs.py saves incrementally).
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
DATA_PATH = CACHE / "h3_pair_minima.json"


def main():
    data = json.loads(DATA_PATH.read_text())
    pairs = data["pair_results"]

    # Build table rows
    rows = []
    for r in pairs:
        if r.get("skipped"):
            rows.append({"label": r["label"], "skipped": True, "reason": r.get("reason", "")})
            continue
        regs = r["regimes"]
        unc = regs.get("unconstrained", {})
        nk5 = regs.get("no_K5", {})
        nk4 = regs.get("no_K4", {})
        rows.append({
            "label": r["label"],
            "N1": r["N1"], "N2": r["N2"], "V_combined": r["N1"] + r["N2"],
            "n_C1": r["n_C1"], "n_C2": r["n_C2"],
            "omega1": r["omega1"], "omega2": r["omega2"],
            "unc_B": unc.get("B_size"),
            "nk5_B": nk5.get("B_size"),
            "nk4_B": nk4.get("B_size"),
            "nk4_omega": nk4.get("omega_combined"),
            "nk4_F": nk4.get("F_profile_sorted"),
            "nk4_chi5": nk4.get("chi_eq_5_verified"),
            "nk4_sat_time": nk4.get("sat_time"),
        })

    # Print full table sorted by V_combined then nk4_B
    print("# Full table\n")
    print("| Pair | $\\|V_1\\|+\\|V_2\\|$ | $\\omega_1, \\omega_2$ | $\\|C_1\\|$ | $\\|C_2\\|$ | unc $\\|B\\|$ | no-$K_5$ $\\|B\\|$ | no-$K_4$ $\\|B\\|$ | $\\omega$(comb, nk4) | F profile (nk4, sorted desc) |")
    print("|---|---:|---|---:|---:|---:|---:|---:|---:|---|")
    valid = [r for r in rows if not r.get("skipped")]
    valid.sort(key=lambda r: (r["V_combined"], r["nk4_B"] if r["nk4_B"] is not None else 9999))
    for r in valid:
        nk4_B = r["nk4_B"] if r["nk4_B"] is not None else "inf"
        nk5_B = r["nk5_B"] if r["nk5_B"] is not None else "inf"
        unc_B = r["unc_B"] if r["unc_B"] is not None else "inf"
        nk4_omega = r["nk4_omega"] if r["nk4_omega"] is not None else "-"
        nk4_F = r["nk4_F"] if r["nk4_F"] else "-"
        print(f"| {r['label']} | {r['V_combined']} | {r['omega1']}, {r['omega2']} | "
              f"{r['n_C1']} | {r['n_C2']} | {unc_B} | {nk5_B} | {nk4_B} | {nk4_omega} | {nk4_F} |")
    print()

    skipped = [r for r in rows if r.get("skipped")]
    if skipped:
        print(f"Skipped pairs: {len(skipped)}")
        for r in skipped:
            print(f"  {r['label']}: {r.get('reason', '')}")
        print()

    # No-K_4 chi=5 with omega(combined) <= 3 (UDG-compatible structural records)
    no_k4_records = [r for r in valid
                     if r["nk4_B"] is not None and r["nk4_omega"] is not None
                     and r["nk4_omega"] <= 3 and r["nk4_chi5"]]
    no_k4_records.sort(key=lambda r: (r["V_combined"], r["nk4_B"]))
    print("# No-K_4 chi=5 graphs (omega=3, UDG-shape-compatible)\n")
    print("| Pair | V_combined | $\\|B\\|$ | $\\omega$ | F profile |")
    print("|---|---:|---:|---:|---|")
    for r in no_k4_records:
        print(f"| {r['label']} | {r['V_combined']} | {r['nk4_B']} | {r['nk4_omega']} | {r['nk4_F']} |")
    print()

    # Smallest no-K_4 chi=5 by V_combined
    if no_k4_records:
        smallest = no_k4_records[0]
        print(f"**Smallest no-K_4 chi=5 (omega=3)**: {smallest['label']} with V={smallest['V_combined']}, |B|={smallest['nk4_B']}, F={smallest['nk4_F']}")
        print()

    # Bridge / vertex density patterns
    print("# Bridge density patterns\n")
    print("| Pair | V | $\\|B\\|$ | $\\|B\\| / V$ | F max | F profile |")
    print("|---|---:|---:|---:|---:|---|")
    for r in no_k4_records:
        ratio = r["nk4_B"] / r["V_combined"]
        f_max = max(r["nk4_F"]) if r["nk4_F"] else 0
        print(f"| {r['label']} | {r['V_combined']} | {r['nk4_B']} | {ratio:.3f} | {f_max} | {r['nk4_F']} |")
    print()


if __name__ == "__main__":
    main()
