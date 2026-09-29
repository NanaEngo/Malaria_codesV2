# P2 V2609C → ChemRxiv Article Class Conversion Guide

**Date**: 17 September 2026  
**Status**: Template ready, manual author block conversion required

---

## Files Created

1. **`P2_MD_Validation_ChemRxiv_Main.tex`** — Main manuscript (needs header conversion)
2. **`P2_MD_Validation_ChemRxiv_SM.tex`** — Supporting Information (needs header conversion)
3. **`Table_*.tex`** — All supporting tables (copied as-is)
4. **`P2_V2609C_bibliography.bib`** — Bibliography (copied as-is)
5. **`Graphics/`** — All figures (copied as-is)

---

## Required Changes

### 1. Documentclass Change

**OLD** (achemso):
```latex
\documentclass[journal=jcisd8,manuscript=article,layout=traditional]{achemso}
```

**NEW** (article):
```latex
\documentclass[11pt,a4paper]{article}
\usepackage[margin=1in]{geometry}
```

---

### 2. Remove achemso-specific elements

- ❌ Remove `\begin{tocentry}...\end{tocentry}` (Graphical TOC)
- ❌ Remove `\maketitle` 
- ❌ Remove `\emergencystretch=12em` and `\sloppy`
- ❌ Remove `\keywords{}` command
- ✅ Keep all other packages

---

### 3. Add Citation Package

**Add before cleveref**:
```latex
\usepackage[numbers,sort&compress]{natbib}
```

---

### 4. Add ORCID Icon Definition

**Add after `\usepackage{tikz}`**:
```latex
% ORCID icon defined locally for the article class
\providecommand{\textorcid}{%
	\begin{tikzpicture}[baseline=0.0ex,line width=0.6,scale=0.65]
		\fill[rounded corners=0.5,fill=green!60!black,draw=green!50!black] (0,0) circle (0.65ex);
		\node[white,font=\bfseries\sffamily\tiny] at (0,0) {iD};
	\end{tikzpicture}%
}
```

---

### 5. Convert Author Block

**Replace this** (achemso format):
```latex
\title{Estimand Divergence Between Static Docking and Molecular Dynamics as a Triage Filter for Antimalarial Leads}

\author{Myke Vital Sao Temgoua}
\affiliation[UY1Phys]{Department of Physics, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}
\email{myke-vital.sao@facsciences-uy1.cm}

\author{Jean-Pierre Tchapet Njafa}
\affiliation[UY1Phys]{Department of Physics, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}

\author{Penabei Samafou}
\affiliation[Sherbrooke]{Department of Medical Imaging and Radiation Sciences, Universit\'e de Sherbrooke, Sherbrooke, QC, Canada}

\author{Fon Wilfred Mbacham}
\affiliation[UY1Biochem]{Department of Biochemistry, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}

\author{Serge Guy Nana Engo}
\affiliation[UY1Phys]{Department of Physics, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}

\keywords{malaria, drug resistance, molecular dynamics, molecular docking, MM-GBSA, African natural products, resistance mutations, antimalarial leads, estimand divergence}
```

**With this** (article class format):
```latex
\title{Estimand Divergence Between Static Docking and Molecular Dynamics as a Triage Filter for Antimalarial Leads}

\date{}

\begin{document}
	
{\centering\Large\bfseries Estimand Divergence Between Static Docking and Molecular Dynamics as a Triage Filter for Antimalarial Leads\par}
\vspace{1em}
{\centering
	Myke Vital Sao Temgoua\href{https://orcid.org/0009-0004-5170-2309}{\textsuperscript{\textorcid}}\footnotemark[1]$^{1}$,
	Jean-Pierre Tchapet Njafa\href{https://orcid.org/0000-0002-1936-8353}{\textsuperscript{\textorcid}}$^{1}$,
	Penabei Samafou\href{https://orcid.org/0000-0002-9683-7678}{\textsuperscript{\textorcid}}$^{2}$,
	Fon Wilfred Mbacham\href{https://orcid.org/0000-0002-3934-3233}{\textsuperscript{\textorcid}}$^{3}$,
	Serge Guy Nana Engo\href{https://orcid.org/0000-0002-7484-3508}{\textsuperscript{\textorcid}}$^{1}$\\[0.5em]
	{\small $^{1}$Department of Physics, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}\\
	{\small $^{2}$Department of Medical Imaging and Radiation Sciences, Universit\'e de Sherbrooke, Sherbrooke, QC, Canada}\\
	{\small $^{3}$Department of Biochemistry, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}\par}

\begin{abstract}
```

**Note**: Add footnote for corresponding author:
```latex
\footnotetext[1]{Corresponding author: \texttt{myke-vital.sao@facsciences-uy1.cm}}
```

**Keywords**: Convert to paragraph format in abstract or add after abstract:
```latex
\noindent\textbf{Keywords:} malaria, drug resistance, molecular dynamics, molecular docking, MM-GBSA, African natural products, resistance mutations, antimalarial leads, estimand divergence
```

---

### 6. Update Cross-References

**Main document** — Update SM reference:
```latex
% OLD
\externaldocument[SM-]{Polypharmacology_MD_Validation_SM_V2609C}

% NEW
\externaldocument[SM-]{P2_MD_Validation_ChemRxiv_SM}
```

**SI document** — Update main reference:
```latex
% OLD
\externaldocument[MAIN-]{Polypharmacology_MD_Validation_V2609C}

% NEW
\externaldocument[MAIN-]{P2_MD_Validation_ChemRxiv_Main}
```

---

### 7. Add Bibliography Style

**Add before `\bibliography{}`**:
```latex
\bibliographystyle{unsrtnat}
\bibliography{P2_V2609C_bibliography}
```

---

### 8. SI Document Conversion

Apply similar changes to `P2_MD_Validation_ChemRxiv_SM.tex`:

1. Change documentclass to `\documentclass[11pt,a4paper]{article}`
2. Add `\usepackage[margin=1in]{geometry}`
3. Keep all SI-specific formatting (tables, figures, sections)
4. Update cross-reference to main document
5. Remove achemso-specific commands

**SI doesn't need author block** — it references the main document.

---

## Compilation Order

1. Compile main: `pdflatex P2_MD_Validation_ChemRxiv_Main.tex`
2. Compile SI: `pdflatex P2_MD_Validation_ChemRxiv_SM.tex`
3. Run bibtex on main: `bibtex P2_MD_Validation_ChemRxiv_Main`
4. Recompile main twice for cross-references
5. Recompile SI once

---

## Checklist

- [ ] Replace documentclass in both files
- [ ] Add geometry package
- [ ] Remove tocentry (Graphical TOC)
- [ ] Convert author block to manual format with ORCID icons
- [ ] Add ORCID icon definition
- [ ] Update cross-reference filenames
- [ ] Add natbib package
- [ ] Add bibliographystyle
- [ ] Remove \maketitle, \emergencystretch, \sloppy
- [ ] Convert \keywords{} to paragraph format
- [ ] Test compilation (main + SI)
- [ ] Verify all cross-references work (\cref, \ref)
- [ ] Check figure and table rendering
- [ ] Verify bibliography formatting

---

## ORCID IDs (for reference)

1. Myke Vital Sao Temgoua: `0009-0004-5170-2309`
2. Jean-Pierre Tchapet Njafa: `0000-0002-1936-8353`
3. Penabei Samafou: `0000-0002-9683-7678`
4. Fon Wilfred Mbacham: `0000-0002-3934-3233`
5. Serge Guy Nana Engo: `0000-0002-7484-3508`

---

## Differences from JCIM Format

| Feature | JCIM (achemso) | ChemRxiv (article) |
|---------|----------------|-------------------|
| Documentclass | `achemso` with journal option | Standard `article` |
| Author block | `\author{}` + `\affiliation{}` | Manual formatting with superscripts |
| Title | `\maketitle` | Manual centering with `\par` |
| TOC graphic | Required `\begin{tocentry}` | Not needed (remove) |
| Keywords | `\keywords{}` command | Paragraph after abstract |
| Bibliography | Auto-handled by achemso | Explicit `\bibliographystyle{unsrtnat}` |
| ORCID icons | Built-in | Manual `\textorcid` definition |
| Cross-refs | Same (`cleveref`) | Same (`cleveref`) |

---

## Notes

- **All scientific content remains unchanged** — only LaTeX formatting changes
- **Graphics/ directory** already contains all figures
- **Table files** already copied and don't need modification
- **Bibliography file** is standard BibTeX format (works with both classes)
- **ChemRxiv accepts article class** submissions in PDF format
- **Zenodo DOI** (`10.5281/zenodo.22829031`) is already correct in both files

---

**Status**: Ready for manual header conversion  
**Estimated time**: 30-45 minutes for careful conversion and testing  
**Risk**: Low — only preamble changes, content unchanged
