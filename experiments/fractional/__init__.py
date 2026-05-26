"""Architecture 3 experiments: fractional chromatic number, Lovász $\\vartheta$,
spectral bounds for $\\chi(\\mathbb{R}^2)$.

Lineage anchors:
  - Cranston-Rabern $\\chi_f \\geq 76/21$ (2017)
  - Matolcsi-Ruzsa-Varga-Zsámboki $\\chi_f \\geq 4$ (2023, arXiv:2311.10069)
  - Bachoc-Nebe-Oliveira Filho-Vallentin generalized Lovász $\\vartheta$ SDP

Wrong-approach detector for Arch 3: $L^\\infty$-plane ($\\chi = 4$;
methods using only abstract norm structure should also bound the
$L^\\infty$ unit-distance graph). The Euclidean inner product /
rotation-invariance must enter essentially.

Cross-architecture coupling: Arch 3's Lovász $\\vartheta$ SDP is the
same infinite-SDP object whose LP relaxation gives the Arch 2 OFV
bound on $m_1(\\mathbb{R}^2)$.
"""
