"""Build and audit the Hadwiger-Nelson lemma-dependency DB.

Reads schema.sql + seed_lemmas.json, materializes a SQLite proof-dependency DAG
under _cache/lemma_db.sqlite, then runs the control-object firewall.

The firewall is HN's structural-honesty gate (the analog of the zeta repo's
Davenport-Heilbronn firewall): it FAILS (non-zero exit) if any node whose
argument is also valid on a control object (Q^2 chi=2, L^infty chi=4, R^1 chi=2)
sits on a load-bearing path to a strictly larger chi lower-bound claim. Such an
argument would over-prove on the control, so it is circular or wrong.

Usage:
  python -m experiments.lemma_db.build_db                # build + audit (CI gate)
  python -m experiments.lemma_db.build_db --frontier     # open nodes ready to attack
  python -m experiments.lemma_db.build_db --deps chi_r2_ge6   # load-bearing prerequisites
  python -m experiments.lemma_db.build_db --selftest     # prove the firewall actually fires

Exit code = number of firewall violations (0 = clean).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

HERE = pathlib.Path(__file__).parent
SCHEMA = HERE / "schema.sql"
SEED = HERE / "seed_lemmas.json"
CACHE = HERE / "_cache"
DB_PATH = CACHE / "lemma_db.sqlite"


def build(db_path: pathlib.Path = DB_PATH) -> sqlite3.Connection:
    """Materialize a fresh DB from schema.sql + seed_lemmas.json."""
    CACHE.mkdir(exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    seed = json.loads(SEED.read_text(encoding="utf-8"))

    con.executemany(
        "INSERT INTO controls(name, known_chi, note) VALUES (:name, :known_chi, :note)",
        seed["controls"],
    )
    for n in seed["nodes"]:
        con.execute(
            "INSERT INTO nodes(id, title, kind, arch, status, claims_bound, learnings, note) "
            "VALUES (:id, :title, :kind, :arch, :status, :claims_bound, :learnings, :note)",
            {
                "id": n["id"], "title": n["title"], "kind": n["kind"], "arch": n["arch"],
                "status": n["status"], "claims_bound": n.get("claims_bound"),
                "learnings": n.get("learnings", ""), "note": n.get("note", ""),
            },
        )
        for c in n.get("control_buildable", []):
            con.execute(
                "INSERT INTO node_controls(node_id, control) VALUES (?, ?)", (n["id"], c)
            )
    con.executemany(
        "INSERT INTO edges(src, dst, rel, note) VALUES (:src, :dst, :rel, :note)",
        [{"src": e["src"], "dst": e["dst"], "rel": e["rel"], "note": e.get("note", "")}
         for e in seed["edges"]],
    )
    con.commit()
    return con


def audit(con: sqlite3.Connection) -> list[sqlite3.Row]:
    return con.execute("SELECT * FROM control_audit").fetchall()


def frontier(con: sqlite3.Connection) -> list[sqlite3.Row]:
    return con.execute("SELECT id, title, arch, learnings FROM frontier ORDER BY arch").fetchall()


def load_bearing_deps(con: sqlite3.Connection, target: str) -> list[sqlite3.Row]:
    rows = con.execute(
        """
        WITH RECURSIVE deps(id) AS (
            SELECT dst FROM v_load_bearing WHERE src = ?
            UNION
            SELECT e.dst FROM v_load_bearing e JOIN deps d ON e.src = d.id
        )
        SELECT n.id, n.title, n.status, n.learnings
        FROM deps JOIN nodes n ON n.id = deps.id
        ORDER BY CASE n.status WHEN 'open' THEN 0 WHEN 'conjectural' THEN 1 ELSE 2 END, n.id
        """,
        (target,),
    ).fetchall()
    return rows


def _print_audit(violations: list[sqlite3.Row]) -> None:
    if not violations:
        print("  [ok] control-object firewall: 0 violations")
        return
    print(f"  [FAIL] control-object firewall: {len(violations)} violation(s)")
    for v in violations:
        print(f"    - target {v['target']} (claims chi>={v['claimed_bound']}) "
              f"load-bearing-depends on {v['offending_node']}, which is buildable on "
              f"{v['control']} (chi={v['known_chi']}). It would over-prove on {v['control']}.")


def selftest(con: sqlite3.Connection) -> int:
    """Inject a load-bearing edge from a control-buildable kill node to the goal
    and confirm the firewall fires; then roll back. Returns 0 if the firewall
    behaves correctly (clean before, dirty after), 1 otherwise.
    """
    before = len(audit(con))
    con.execute(
        "INSERT INTO edges(src, dst, rel, note) VALUES "
        "('chi_r2_ge6', 'kill_norm_blind_borel', 'depends_on', 'SELFTEST injected')"
    )
    after = len(audit(con))
    con.execute(
        "DELETE FROM edges WHERE src='chi_r2_ge6' AND dst='kill_norm_blind_borel' "
        "AND note='SELFTEST injected'"
    )
    restored = len(audit(con))
    ok = (before == 0 and after > 0 and restored == 0)
    print(f"  firewall self-test: clean={before==0}, fires-on-injection={after>before}, "
          f"rolls-back-clean={restored==0} -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier", action="store_true", help="list open nodes ready to attack")
    parser.add_argument("--deps", metavar="NODE_ID", help="list load-bearing prerequisites of a node")
    parser.add_argument("--selftest", action="store_true", help="prove the firewall fires on a planted violation")
    args = parser.parse_args(argv)

    con = build()
    n_nodes = con.execute("SELECT count(*) FROM nodes").fetchone()[0]
    n_edges = con.execute("SELECT count(*) FROM edges").fetchone()[0]
    print(f"built lemma_db: {n_nodes} nodes, {n_edges} edges -> {DB_PATH}")

    if args.deps:
        print(f"\nload-bearing prerequisites of {args.deps} (open/conjectural first):")
        for r in load_bearing_deps(con, args.deps):
            tag = f" [{r['learnings']}]" if r["learnings"] else ""
            print(f"  {r['status']:11s} {r['id']:28s} {r['title']}{tag}")
        return 0

    if args.frontier:
        print("\nfrontier (open, all load-bearing prerequisites settled):")
        for r in frontier(con):
            tag = f" [{r['learnings']}]" if r["learnings"] else ""
            print(f"  {r['arch']:6s} {r['id']:28s} {r['title']}{tag}")
        return 0

    if args.selftest:
        print()
        return selftest(con)

    print()
    violations = audit(con)
    _print_audit(violations)
    print("\nfrontier (attack these now):")
    for r in frontier(con):
        print(f"  {r['arch']:6s} {r['id']:28s} {r['title']}")
    return len(violations)


if __name__ == "__main__":
    raise SystemExit(main())
