"""GPU-scaled (batched, multi-start) gradient search for the HN program.

Everything here PROPOSES float unit-distance configurations at scale; the SAT
firewall (adversarial.sat_chi / f1pt_lib.sat_kcolor) decides every hard chromatic
claim. GD never proves chi >= 6. See batched_core.py for the discipline note.
"""
