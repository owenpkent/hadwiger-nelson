# hn_solver benchmark results

Node budget: 1,500,000. MapleChrono in-process (pysat). BUDGET = hn_solver hit the node limit. Times are wall-clock; MapleChrono is a compiled C CDCL solver, hn_solver is pure Python.

| instance | n | m | chi | k | hn | nodes | hn time | maple | maple time | agree | winner |
|---|--:|--:|:--:|--:|:--:|--:|--:|:--:|--:|:--:|:--:|
| K6 | 6 | 15 | 6 | 5 | UNSAT | 0 | 0.1 ms | UNSAT | 0.5 ms | OK | hn 7.7x |
| K6 | 6 | 15 | 6 | 6 | SAT | 1 | 0.0 ms | SAT | 0.1 ms | OK | hn 5.4x |
| K7 | 7 | 21 | 7 | 6 | UNSAT | 0 | 0.0 ms | UNSAT | 2.0 ms | OK | hn 79.2x |
| K7 | 7 | 21 | 7 | 7 | SAT | 1 | 0.0 ms | SAT | 0.2 ms | OK | hn 7.9x |
| K8 | 8 | 28 | 8 | 7 | UNSAT | 0 | 0.0 ms | UNSAT | 10.6 ms | OK | hn 407.6x |
| K8 | 8 | 28 | 8 | 8 | SAT | 1 | 0.0 ms | SAT | 0.3 ms | OK | hn 7.2x |
| Moser spindle (7v) | 7 | 11 | 4 | 3 | UNSAT | 6 | 0.1 ms | UNSAT | 0.1 ms | OK | hn 2.4x |
| Moser spindle (7v) | 7 | 11 | 4 | 4 | SAT | 5 | 0.0 ms | SAT | 0.1 ms | OK | hn 2.9x |
| Grotzsch M(C5) 11v (tri-free) | 11 | 20 | 4 | 3 | UNSAT | 25 | 0.1 ms | UNSAT | 0.2 ms | OK | hn 1.3x |
| Grotzsch M(C5) 11v (tri-free) | 11 | 20 | 4 | 4 | SAT | 10 | 0.1 ms | SAT | 0.1 ms | OK | hn 1.9x |
| M^2(C5) 23v (tri-free) | 23 | 71 | 5 | 4 | UNSAT | 882 | 9.5 ms | UNSAT | 1.24 s | OK | hn 130.9x |
| M^2(C5) 23v (tri-free) | 23 | 71 | 5 | 5 | SAT | 22 | 0.4 ms | SAT | 0.6 ms | OK | hn 1.4x |
| M^3(C5) 47v (tri-free) | 47 | 236 | 6 | 5 | UNSAT | 447,720 | 11.81 s | UNSAT | 31.90 s | OK | hn 2.7x |
| M^3(C5) 47v (tri-free) | 47 | 236 | 6 | 6 | SAT | 46 | 1.7 ms | SAT | 1.5 ms | OK | maple 1x |
| M^4(C5) 95v (tri-free) | 95 | 755 | ? | 7 | SAT | 94 | 8.3 ms | SAT | 4.7 ms | OK | maple 2x |
| rand G(15,0.5) | 15 | 49 | 5 | 4 | UNSAT | 3 | 0.1 ms | UNSAT | 0.6 ms | OK | hn 6.0x |
| rand G(15,0.5) | 15 | 49 | 5 | 5 | SAT | 12 | 0.1 ms | SAT | 0.3 ms | OK | hn 2.4x |
| rand G(25,0.4) | 25 | 117 | 5 | 4 | UNSAT | 4 | 0.2 ms | UNSAT | 2.4 ms | OK | hn 12.3x |
| rand G(25,0.4) | 25 | 117 | 5 | 5 | SAT | 22 | 0.4 ms | SAT | 7.9 ms | OK | hn 18.2x |
| rand G(40,0.3) | 40 | 230 | 6 | 5 | UNSAT | 122 | 4.4 ms | UNSAT | 5.43 s | OK | hn 1242.4x |
| rand G(40,0.3) | 40 | 230 | 6 | 6 | SAT | 38 | 1.2 ms | SAT | 1.0 ms | OK | maple 1x |
| rand G(60,0.25) | 60 | 432 | 6 | 5 | UNSAT | 335 | 24.2 ms | UNSAT | 5.31 s | OK | hn 219.3x |
| rand G(60,0.25) | 60 | 432 | 6 | 6 | SAT | 1,828 | 110.9 ms | SAT | 1.02 s | OK | hn 9.2x |
| lineage P510 (k=5 SAT) | 510 | 2504 | ? | 5 | SAT | 508 | 168.0 ms | SAT | 9.28 s | OK | hn 55.2x |

Total instances/k: 24. Correctness disagreements: 0. hn_solver hit the node budget on 0. hn_solver faster on 21/24.
