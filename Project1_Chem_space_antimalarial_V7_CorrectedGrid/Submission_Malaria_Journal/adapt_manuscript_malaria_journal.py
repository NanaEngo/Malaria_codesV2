#!/usr/bin/env python3
"""
Adapt JCAMD manuscript to Malaria Journal format
Created: 28 September 2026

Malaria Journal requirements:
1. Structured abstract: Background/Methods/Results/Conclusions sections
2. Abbreviations section
3. Introduction → Background (section title)
4. Expanded Conclusions (2-3 paragraphs instead of brief summary)
5. Authors' Contributions section (already present in JCAMD version)
"""

import re

def adapt_abstract(text):
    """Restructure abstract with Background/Methods/Results/Conclusions sections"""
    
    # Find abstract content
    abstract_pattern = r'\\begin\{abstract\}(.*?)\\end\{abstract\}'
    match = re.search(abstract_pattern, text, re.DOTALL)
    
    if not match:
        print("WARNING: Abstract not found")
        return text
    
    old_abstract = match.group(0)
    abstract_content = match.group(1).strip()
    
    # Remove the TOC graphic from abstract content
    abstract_content = re.sub(r'\\begin\{center\}.*?\\end\{center\}', '', abstract_content, flags=re.DOTALL).strip()
    
    # Build structured abstract
    new_abstract = r'''\begin{abstract}
\noindent\textbf{Background:} Antimalarial resistance threatens treatment efficacy, particularly where single-target compounds lose activity after parasitemutations. Chemotypes engaging multiple resistance-relevant targets may provide broader starting points, yet target breadth, mutation tolerance, and experimental activity must be measured separately. African natural products offer chemically rich, incompletely explored scaffolds that can be computationally expanded into tractable antimalarial leads.

\noindent\textbf{Methods:} A hybrid library of 65\,856 molecules was generated from 396 African natural products and 454 synthetic antimalarial compounds using scaffold-preserving expansion (STONED-SELFIES, Cheese API). Multi-parameter optimization and synthetic-accessibility filtering prioritized 19\,913 candidates. A 17-member polypharmacology-oriented cohort was docked against PfDHFR, PfCRT, PfClpP, and PfATP4 using AutoDock Vina. Per-target resistance-resilience scores (RRS) quantified docking-score retention across PfDHFR (N51I, C59R, S108N, I164L) and PfCRT (K76T, K76A) mutant panels, excluding non-binding wild-type baselines.

\noindent\textbf{Results:} All 68 candidate--target pairs passed geometric quality criteria, with Vina scores ranging from $-12.01$ to $-4.63$~kcal~mol$^{-1}$. RRS analysis classified the cohort into seven A*, four B, and six C profiles (RRS 73.2--115.6\%). After Bonferroni correction, polypharmacology network score correlated negatively with RRS ($\rho = -0.714$, $p < 0.017$), RRS correlated positively with wild-type score magnitude ($\rho = +0.691$), and number of favorable targets correlated positively with RRS ($\rho = 0.714$). African-centered structural index showed no significant RRS association ($\rho = -0.190$). Five candidates (PP-15, PP-05, PP-06, PP-11, PP-13) combined favorable four-target profiles with A* RRS classification. PfCRT K76T/K76A mutations showed no detectable signal (RRS 99.1--100.6\%, null control 99.4--100.5\%).

\noindent\textbf{Conclusions:} Target breadth and mutation resilience provide complementary, non-interchangeable chemotype prioritization criteria. The workflow identified structurally diverse candidates with heterogeneous target-specific mutation-tolerance profiles. These computational hypotheses require experimental validation before claiming biological potency, target engagement, or resistance circumvention. Five priority candidates are recommended for biochemical assays, mutant-panel testing, and molecular-dynamics refinement.

	\begin{center}
		\includegraphics[width=0.95\linewidth]{p1_v7_toc_graphic.pdf}
	\end{center}
\end{abstract}'''
    
    return text.replace(old_abstract, new_abstract)


def add_abbreviations_section(text):
    """Add Abbreviations section after Keywords"""
    
    # Find the position after keywords
    keywords_pattern = r'(\\noindent\\textbf\{Keywords:\}.*?\n)'
    match = re.search(keywords_pattern, text, re.DOTALL)
    
    if not match:
        print("WARNING: Keywords not found")
        return text
    
    abbreviations_section = r'''
\section*{Abbreviations}
\noindent ACSI: African-Centered Structural Index; ADMET: Absorption, Distribution, Metabolism, Excretion, Toxicity; AUC: Area Under the Curve; CI: Confidence Interval; DEKOIS: Demanding Evaluation Kits for Objective In Silico Screening; MMV: Medicines for Malaria Venture; MPO: Multi-Parameter Optimization; MTX: Methotrexate; PAINS: Pan-Assay Interference Compounds; PDB: Protein Data Bank; PfATP4: \emph{Plasmodium falciparum} Ca$^{2+}$-ATPase 4; PfClpP: \emph{Plasmodium falciparum} Caseinolytic Protease P; PfCRT: \emph{Plasmodium falciparum} Chloroquine Resistance Transporter; PfDHFR: \emph{Plasmodium falciparum} Dihydrofolate Reductase; PNS: Polypharmacology Network Score; QED: Quantitative Estimate of Drug-likeness; RMSD: Root Mean Square Deviation; ROC: Receiver Operating Characteristic; RRS: Resistance-Resilience Score; SELFIES: SELF-referencIng Embedded Strings; SMILES: Simplified Molecular-Input Line-Entry System; STONED: Stochastic Exploration of Chemical Space; WT: Wild-Type.

'''
    
    # Insert after keywords
    insertion_pos = match.end()
    return text[:insertion_pos] + abbreviations_section + text[insertion_pos:]


def rename_introduction_to_background(text):
    """Rename Introduction section to Background"""
    
    # Replace section title
    text = re.sub(
        r'\\section\{Introduction\}',
        r'\\section{Background}',
        text
    )
    
    return text


def expand_conclusions(text):
    """Expand the Conclusions section to 2-3 substantial paragraphs"""
    
    # Find current conclusion section
    conclusion_pattern = r'(\\section\{Conclusion\}\\label\{sec:conclusion\})(.*?)(\\bibliographystyle)'
    match = re.search(conclusion_pattern, text, re.DOTALL)
    
    if not match:
        print("WARNING: Conclusion section not found")
        return text
    
    # Build expanded conclusions
    expanded_conclusions = r'''\section{Conclusions}\label{sec:conclusion}
This study demonstrates that target breadth and mutation resilience can be evaluated as distinct, complementary properties when prioritizing antimalarial chemotypes from African-natural-product-inspired chemical space. By separating chemical-space expansion, target-anchored docking, and per-target mutation analysis into independent evidence layers, the workflow generated testable hypotheses about chemotype utility without conflating computational estimates with biological activity. The resulting 17-member cohort exhibits heterogeneous target-specific profiles: seven A*, four B, and six C resistance-resilience classifications spanning 73.2--115.6\% of wild-type docking-score magnitudes across PfDHFR and PfCRT mutant panels. Five candidates (PP-15, PP-05, PP-06, PP-11, and PP-13) combine favorable docking estimates on all four mechanistically distinct targets (PfDHFR, PfCRT, PfClpP, PfATP4) with A* mutation-resilience classification, defining the priority tier for experimental follow-up. These operational classifications represent computational hypotheses, not confirmed biological activity or validated resistance circumvention.

The workflow's target-specific design preserves interpretive precision that would be lost in cross-target averaging. PfDHFR and PfCRT anchor the analysis in established resistance biology with mutant-panel validation; PfClpP extends the profile to proteostasis vulnerabilities; and PfATP4 tests ion-homeostasis engagement. Because these targets differ in binding-site architecture, structural evidence quality, and availability of co-crystallized inhibitors, no uncalibrated arithmetic mean can substitute for target-wise reporting. The per-target RRS framework quantifies mutation tolerance without pooling evidence from non-binding baselines, preventing artifactual resilience scores. The PfCRT K76T/K76A result illustrates this boundary: the corrected 3D7-like wild-type receptor showed no detectable mutant signal (RRS 99.1--100.6\%, null control 99.4--100.5\%), indicating that the RRS framework correctly reports neutral-within-null findings rather than false-positive resistance circumvention. This honest-negative result strengthens confidence in the A* classifications on other targets where genuine mutant-to-wild-type differences were detected.

The centroid-based library reduction achieved 99.3\% computational-cost reduction (1\,936 versus 263\,424 docking calculations) while retaining 69.3\% scaffold recovery from the African-natural-product seed set, making systematic multi-target and mutation-panel screening accessible to research groups with limited infrastructure. This efficiency advantage enabled exploration of a 65\,856-molecule hybrid library that combined scaffold-preserving expansion (STONED-SELFIES, Cheese API) with multi-parameter optimization and synthetic-accessibility filtering, yielding 19\,913 computationally prioritized candidates. The workflow does not claim exhaustive chemical-space coverage or preserved activity cliffs; centroid representatives may not generalize to all cluster members. Experimental validation should include cluster-neighbor sampling around promising centroids.

For the five priority candidates, the recommended follow-up experiments combine biochemical potency measurements against wild-type \emph{P. falciparum} parasites and recombinant proteins, testing against isogenic mutant parasite lines (N51I, C59R, S108N, I164L for PfDHFR; K76T, K76A for PfCRT), orthogonal binding assays (surface plasmon resonance, isothermal titration calorimetry, or thermal shift assays), molecular-dynamics refinement of bound complexes to assess pose stability and identify key interactions, and candidate-specific ADMET profiling before lead optimization. The DEKOIS near-chance result (PfDHFR AUC 0.45) and the approved-drug retrospective (pyrimethamine and chloroquine RRS indistinguishable from null) constrain interpretation of absolute Vina scores but do not invalidate relative within-target rankings or the RRS framework, which depends on mutant-to-wild-type ratios on the same receptor. These validation boundaries should inform experimental design: RRS profiles define which mutant-panel experiments to prioritize, while absolute docking scores require orthogonal binding validation.

African natural products contributed chemically rich scaffolds with stereochemical complexity that complement synthetic antimalarial chemistry. The 92.6\% whole-molecule novelty (Tanimoto $<$ 0.4 to seed set) coexisted with 69.3\% scaffold retention, indicating successful peripheral diversification around privileged ring systems. However, structural relatedness to African natural products (ACSI) showed no significant association with mutation resilience ($\rho = -0.190$, $p = 0.48$), reinforcing that natural-product character cannot substitute for target-specific mutation analysis. The negative PNS--RRS correlation ($\rho = -0.714$, $p < 0.017$) suggests that candidates targeting network-peripheral proteins may show greater computational mutation resilience, though this exploratory association requires experimental validation and may reflect PfCRT's network absence rather than genuine biological mechanism.

The study has important limitations. Docking scores are empirical scoring-function outputs calibrated neither across heterogeneous binding sites nor against experimental free energies. PfCRT is represented by a corrected proxy cavity (Y01 A501), and PfATP4 by a mechanism-motivated region without co-crystallized inhibitors; these exploratory anchors do not provide the same evidential strength as PfDHFR's co-crystallized inhibitor. RRS covers only PfDHFR and PfCRT mutation panels; no PfClpP or PfATP4 mutant data were available. The 17-member cohort is purposefully enriched for predicted polypharmacology and lacks statistical power to detect weak associations (80\% power requires $|\rho| \geq 0.62$ at $\alpha = 0.05$). The four MD validation systems are separate from Set C and cannot validate the Set C RRS profiles. No IC$_{50}$/EC$_{50}$ measurements were performed. Independent structural assessment through co-crystallization or cryo-EM remains necessary before the target panel can support stronger structural conclusions.

This integrated workflow advances computational antimalarial discovery by keeping target breadth and mutation resilience as separate, falsifiable hypotheses rather than collapsing them into a single composite score. The resulting candidate profiles define which chemotypes, targets, and mutant panels should be tested next. They propose experimental priorities; they do not claim biological potency, target engagement, or resistance circumvention. Five candidates warrant immediate biochemical follow-up; the remaining cohort provides a structurally diverse hypothesis space for secondary screening. The computational framework is reproducible, accessible to groups with limited infrastructure, and grounded in African-natural-product chemical space, aligning discovery efforts with endemic-region research capacity.

'''
    
    return text[:match.start(1)] + expanded_conclusions + '\n\t' + match.group(3) + text[match.end():]


def update_title_comment(text):
    """Update document title comment for Malaria Journal"""
    
    text = re.sub(
        r'% Main Manuscript for.*?\n',
        '% Main Manuscript for Malaria Journal\n',
        text
    )
    
    return text


def main():
    """Main adaptation function"""
    
    # Read source file
    source_path = '../Submission_JCAMD/P1_Integrated_Polypharmacology_RRS_Main_JCAMD.tex'
    print(f"Reading source file: {source_path}")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Applying Malaria Journal adaptations:")
    
    # Apply all adaptations
    print("  1. Updating title comment...")
    content = update_title_comment(content)
    
    print("  2. Restructuring abstract (Background/Methods/Results/Conclusions)...")
    content = adapt_abstract(content)
    
    print("  3. Adding Abbreviations section...")
    content = add_abbreviations_section(content)
    
    print("  4. Renaming Introduction → Background...")
    content = rename_introduction_to_background(content)
    
    print("  5. Expanding Conclusions section (2-3 paragraphs)...")
    content = expand_conclusions(content)
    
    # Write output file
    output_path = 'P1_Integrated_Polypharmacology_RRS_Main_MalJ.tex'
    print(f"\nWriting adapted manuscript: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ Malaria Journal adaptation complete!")
    print("\nKey changes applied:")
    print("  - Structured abstract with Background/Methods/Results/Conclusions sections")
    print("  - Abbreviations section added after Keywords")
    print("  - Introduction section renamed to Background")
    print("  - Conclusions expanded to comprehensive 2-3 paragraph summary")
    print("  - All other content preserved from JCAMD version")
    print("\nNext steps:")
    print("  1. Compile manuscript: pdflatex + bibtex + 2x pdflatex")
    print("  2. Adapt Supporting Information (same format changes)")
    print("  3. Create Malaria Journal cover letter with APC waiver request")
    print("  4. Verify all cross-references and figures compile correctly")


if __name__ == '__main__':
    main()
