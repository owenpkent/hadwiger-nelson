-- lemma_db schema: a queryable proof-dependency DAG for the Hadwiger-Nelson
-- program, with a control-object firewall.
--
-- Adapted from the zeta repo's Davenport-Heilbronn firewall. The firewall here
-- is HN's three control objects: any node whose argument is ALSO valid on a
-- control (Q^2 chi=2, L^infty chi=4, R^1 chi=2) must NOT be load-bearing for a
-- claim of a strictly larger chi bound, or it would over-prove on that control.
--
-- Edge relations split into two classes:
--   LOAD-BEARING: depends_on, specializes   (src's validity rests on dst)
--   ANNOTATION:   motivates, constrains, refutes, would_prove  (commentary only)
-- Only load-bearing edges propagate the firewall.

PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS frontier;
DROP VIEW  IF EXISTS v_load_bearing;
DROP VIEW  IF EXISTS control_audit;
DROP TABLE IF EXISTS node_controls;
DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS controls;

CREATE TABLE controls (
    name      TEXT PRIMARY KEY,   -- Q2 | Linf | R1
    known_chi INTEGER NOT NULL,   -- the KNOWN chromatic number of this control
    note      TEXT
);

CREATE TABLE nodes (
    id           TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    kind         TEXT NOT NULL,    -- target | result | theorem | lemma | conjecture | note | kill
    arch         TEXT NOT NULL,    -- arch1 | arch2 | arch3 | arch4 | shared
    status       TEXT NOT NULL,    -- proven | external | open | conjectural | refuted
    claims_bound INTEGER,          -- N for a "chi(R^2) >= N" claim; NULL otherwise
                                   -- (chi_m / upper-bound / enabling nodes are NULL,
                                   -- so the firewall guards only ordinary-chi lower bounds)
    learnings    TEXT,             -- provenance, e.g. "L51-L53" or "C1"
    note         TEXT
);

-- The controls on which a node's argument/object is ALSO valid. Empty for a
-- genuinely-Euclidean node. A non-empty row is what the firewall watches.
CREATE TABLE node_controls (
    node_id TEXT NOT NULL REFERENCES nodes(id),
    control TEXT NOT NULL REFERENCES controls(name),
    PRIMARY KEY (node_id, control)
);

CREATE TABLE edges (
    src  TEXT NOT NULL REFERENCES nodes(id),
    dst  TEXT NOT NULL REFERENCES nodes(id),
    rel  TEXT NOT NULL,            -- depends_on | specializes | motivates | constrains | refutes | would_prove
    note TEXT,
    PRIMARY KEY (src, dst, rel)
);

-- Load-bearing sub-DAG.
CREATE VIEW v_load_bearing AS
    SELECT src, dst, rel, note FROM edges
    WHERE rel IN ('depends_on', 'specializes');

-- Frontier: open nodes whose every load-bearing prerequisite is already settled
-- (proven or external). These are the things you can actually attack now.
CREATE VIEW frontier AS
    SELECT n.* FROM nodes n
    WHERE n.status = 'open'
      AND NOT EXISTS (
          SELECT 1 FROM v_load_bearing e
          JOIN nodes d ON d.id = e.dst
          WHERE e.src = n.id
            AND d.status NOT IN ('proven', 'external')
      );

-- Control-object firewall. A violation row means: a bound-claiming target
-- transitively (load-bearing) depends on a node that is buildable on a control
-- whose known chi is strictly less than the claimed bound. That argument would
-- over-prove on the control, so it is structurally wrong / circular.
CREATE VIEW control_audit AS
    WITH RECURSIVE reach(target, bound, dep) AS (
        SELECT n.id, n.claims_bound, e.dst
        FROM nodes n
        JOIN v_load_bearing e ON e.src = n.id
        WHERE n.claims_bound IS NOT NULL
        UNION
        SELECT r.target, r.bound, e.dst
        FROM reach r
        JOIN v_load_bearing e ON e.src = r.dep
    )
    SELECT DISTINCT
        r.target,
        r.bound        AS claimed_bound,
        r.dep          AS offending_node,
        nc.control,
        c.known_chi
    FROM reach r
    JOIN node_controls nc ON nc.node_id = r.dep
    JOIN controls c        ON c.name = nc.control
    WHERE r.bound > c.known_chi;
