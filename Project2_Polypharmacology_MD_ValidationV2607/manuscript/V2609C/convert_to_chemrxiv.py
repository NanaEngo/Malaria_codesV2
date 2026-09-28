#!/usr/bin/env python3
"""
Convert P2 V2609C JCIM (achemso) manuscripts to ChemRxiv article-class format.

Strategy (rewritten 2026-09-28):
  - The article-class preambles (fonts, caption, natbib, hyperref, ORCID icon,
    author block with real ORCID iDs) are frozen templates below. They mirror
    the hand-crafted conversion that produced the first compilable preprints.
  - The body of each output is reassembled from the CURRENT canonical ACS
    sources (everything after \\begin{document}/\\maketitle), so every content
    fix made in the canonical tree propagates automatically.
  - achemso-only constructs are translated: tocentry is dropped,
    acknowledgement/suppinfo become plain sections, achemso.bst -> unsrtnat,
    and the bibliography key is repointed at the bundled preprint bib.

Run from anywhere; paths are resolved relative to this script's directory
(manuscript/V2609C/). Build order after conversion:
  pdflatex main; pdflatex SM; pdflatex main; pdflatex SM  (xr cross-refs)
"""

import re
import shutil
from pathlib import Path

MAIN_OUT = "P2_MD_Validation_ChemRxiv_Main.tex"
SM_OUT = "P2_MD_Validation_ChemRxiv_SM.tex"
BIB_OUT = "P2_V2609C_bibliography.bib"

MAIN_TEMPLATE = r"""%% ============================================================================
%% Paper 2: Estimand Divergence Between Static Docking and Molecular Dynamics as a Triage Filter for Antimalarial Leads
%% ChemRxiv Preprint Version (converted from JCIM achemso format)
%% Article source — September 2026 (V2609C: literature-integrated reframing)
%% ============================================================================

\documentclass[11pt,a4paper]{article}

\usepackage[margin=1in]{geometry}

% Fonts and encoding
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}

% Mathematics
\usepackage{amsmath, amsfonts, amssymb, mathtools}

% Figures and tables
\usepackage{graphicx}
\usepackage{booktabs, tabularx, array, multirow, longtable}
\usepackage{tikz}

% ORCID icon defined locally for the article class
\providecommand{\textorcid}{%
	\begin{tikzpicture}[baseline=0.0ex,line width=0.6,scale=0.65]
		\fill[rounded corners=0.5,fill=green!60!black,draw=green!50!black] (0,0) circle (0.65ex);
		\node[white,font=\bfseries\sffamily\tiny] at (0,0) {iD};
	\end{tikzpicture}%
}

\usepackage{rotating}
\usepackage[table]{xcolor}
\usepackage[labelfont=bf,textfont={footnotesize,it}]{caption}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\usepackage{microtype}
\usepackage[numbers,sort&compress]{natbib}

% Units and SI
\usepackage[
  group-minimum-digits = 5,
  per-mode             = symbol,
  range-phrase         = {--},
  range-units          = single,
  separate-uncertainty = true,
  retain-explicit-plus = true,
]{siunitx}
\DeclareSIUnit\molar{M}
\DeclareSIUnit\angstrom{\text{\AA}}
\DeclareSIUnit\kcalmol{kcal\,mol^{-1}}
\DeclareSIUnit\barpressure{\mathrm{bar}}

% Cross-referencing
\usepackage[nameinlink,noabbrev]{cleveref}
% SM cross-refs (labels SM-* live in the supplementary document)
\usepackage{xr}
\externaldocument[SM-]{P2_MD_Validation_ChemRxiv_SM}

% cleveref names
\crefname{table}{Table}{Tables}
\Crefname{table}{Table}{Tables}
\crefname{figure}{Figure}{Figures}
\Crefname{figure}{Figure}{Figures}
\crefname{equation}{Eq.}{Eqs.}
\crefname{section}{Section}{Sections}
\crefname{subsection}{Section}{Sections}

% Path configuration
\graphicspath{{Graphics/}}

% ============================================================================
% TITLE AND AUTHOR INFORMATION
% ============================================================================

\title{{{TITLE}}}

\date{}

% ============================================================================
% BEGIN DOCUMENT
% ============================================================================

\begin{document}

{{TITLE_BLOCK}}

\footnotetext[1]{Corresponding author: \texttt{myke-vital.sao@facsciences-uy1.cm}}
"""

MAIN_TITLE_BLOCK = r"""{\centering\Large\bfseries {{TITLE}}\par}
\vspace{1em}
{\centering
	Myke Vital Sao Temgoua\href{https://orcid.org/0009-0004-5170-2309}{\textsuperscript{\textorcid}}\footnotemark[1]$^{1}$,
	Jean-Pierre Tchapet Njafa\href{https://orcid.org/0000-0002-1936-8353}{\textsuperscript{\textorcid}}$^{1}$,
	Penabei Samafou\href{https://orcid.org/0000-0002-9683-7678}{\textsuperscript{\textorcid}}$^{2}$,
	Wilfred Fon Mbacham\href{https://orcid.org/0000-0002-3934-3233}{\textsuperscript{\textorcid}}$^{3}$,
	Serge Guy Nana Engo\href{https://orcid.org/0000-0002-7484-3508}{\textsuperscript{\textorcid}}$^{1}$\\[0.5em]
	{\small $^{1}$Department of Physics, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}\\
	{\small $^{2}$Department of Medical Imaging and Radiation Sciences, Universit\'e de Sherbrooke, Sherbrooke, QC, Canada}\\
	{\small $^{3}$Department of Biochemistry, Faculty of Science, University of Yaound\'e I, P.O. Box 812, Yaound\'e, Cameroon}\par}"""

SM_TEMPLATE = r"""%% ============================================================================
%% Supporting Information: Calibrating the Interpretation of Docking-Derived Resistance-Retention Scores with a Short Molecular-Dynamics Structural Stress Test
%% ChemRxiv Preprint Version (converted from JCIM achemso format)
%% Aligned with main manuscript P2_MD_Validation_ChemRxiv_Main.tex
%% ============================================================================

\documentclass[11pt,a4paper]{article}

\usepackage[margin=1in]{geometry}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amsmath, amsfonts, amssymb}
\usepackage{graphicx}
\usepackage{booktabs, tabularx, array, multirow}
\usepackage{pdflscape}  % For landscape pages
\usepackage[table]{xcolor}
\usepackage[labelfont=bf,textfont={footnotesize,it}]{caption}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\usepackage{microtype}
\usepackage[numbers,sort&compress]{natbib}
\usepackage[
  group-minimum-digits = 4,
  per-mode             = symbol,
  range-phrase         = {--},
  range-units          = single,
  separate-uncertainty = true,
  retain-explicit-plus = true,
]{siunitx}
\DeclareSIUnit\kcalmol{kcal\,mol^{-1}}
\DeclareSIUnit\molar{M}
\DeclareSIUnit\angstrom{\text{\AA}}

\usepackage[nameinlink,noabbrev]{cleveref}
\crefname{table}{Table}{Tables}
\Crefname{table}{Table}{Tables}
\crefname{figure}{Figure}{Figures}
\Crefname{figure}{Figure}{Figures}
\crefname{equation}{Eq.}{Eqs.}
\crefname{section}{Section}{Sections}
\crefname{subsection}{Section}{Sections}

\usepackage{xr}
\externaldocument[MAIN-]{P2_MD_Validation_ChemRxiv_Main}
% Build order: pdflatex main; pdflatex SM; pdflatex main; pdflatex SM

% Configure S-prefixed numbering for SI
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\theequation}{S\arabic{equation}}
\renewcommand{\thesection}{S\arabic{section}}

\graphicspath{{Graphics/}}

\title{Supporting Information: {{TITLE}}}

\author{Myke Vital Sao Temgoua \and Jean-Pierre Tchapet Njafa \and Penabei Samafou \and Wilfred Fon Mbacham \and Serge Guy Nana Engo}

\date{}

\begin{document}

\maketitle
"""


def extract_canonical_title(main_source: str) -> str:
    m = re.search(r"\\title\{(.+?)\}", main_source, re.DOTALL)
    if not m:
        raise SystemExit("ERROR: could not locate \\title{...} in the canonical main source")
    return m.group(1).strip()


def canonical_body(source: str, is_si: bool) -> str:
    """Return the canonical document body (after \begin{document} and \maketitle),
    with achemso-only constructs translated for the article class."""
    body = source.split(r"\begin{document}", 1)[1]
    body = body.split(r"\maketitle", 1)[1] if r"\maketitle" in body else body

    # Drop the achemso graphical TOC (article has no tocentry environment)
    body = re.sub(r"\\begin\{tocentry\}.*?\\end\{tocentry\}", "", body, flags=re.DOTALL)

    # achemso environments -> plain sections
    body = re.sub(
        r"\\begin\{acknowledgement\}(.*?)\\end\{acknowledgement\}",
        lambda m: "\\section*{Acknowledgements}\n\n" + m.group(1).strip(),
        body,
        flags=re.DOTALL,
    )
    body = re.sub(
        r"\\begin\{suppinfo\}(.*?)\\end\{suppinfo\}",
        lambda m: "\\section*{Supporting Information}\n\n" + m.group(1).strip(),
        body,
        flags=re.DOTALL,
    )

    # Bibliography: achemso class supplies the style internally; the converted
    # article body must declare one explicitly or bibtex fails (no \bibstyle).
    body = body.replace(r"\bibliographystyle{achemso}", r"\bibliographystyle{unsrtnat}")
    if "\\bibliographystyle" not in body:
        body = body.replace(
            r"\bibliography{Project2_Polypharmacology_MD_Validation}",
            "\\bibliographystyle{unsrtnat}\n\\bibliography{P2_V2609C_bibliography}",
        )
    body = body.replace(
        r"\bibliography{Project2_Polypharmacology_MD_Validation}",
        r"\bibliography{P2_V2609C_bibliography}",
    )
    return body.strip()


def main():
    base_dir = Path(__file__).resolve().parent
    chemrxiv_dir = base_dir / "ChemRxiv_version"
    chemrxiv_dir.mkdir(exist_ok=True)

    # Re-sync Graphics from the canonical sources on every run
    graphics_src = base_dir / "Graphics"
    graphics_dst = chemrxiv_dir / "Graphics"
    if graphics_src.exists():
        shutil.copytree(graphics_src, graphics_dst, dirs_exist_ok=True)
        print(f"✅ Re-synced Graphics directory ({len(list(graphics_src.glob('*')))} entries)")

    # Copy table files
    table_files = list(base_dir.glob("Table_*.tex"))
    for table_file in table_files:
        shutil.copy(table_file, chemrxiv_dir / table_file.name)
    print(f"✅ Copied {len(table_files)} table files")

    # Copy bibliography (canonical project bib -> preprint bib name)
    bib_src = base_dir / "Project2_Polypharmacology_MD_Validation.bib"
    if bib_src.exists():
        shutil.copy(bib_src, chemrxiv_dir / BIB_OUT)
        print("✅ Copied bibliography file (from canonical project bib)")

    # Read canonical sources
    main_src = (base_dir / "Polypharmacology_MD_Validation_V2609C.tex").read_text(encoding="utf-8")
    sm_src = (base_dir / "Polypharmacology_MD_Validation_SM_V2609C.tex").read_text(encoding="utf-8")
    title = extract_canonical_title(main_src)

    # Assemble main
    main_out = MAIN_TEMPLATE.replace("{{TITLE}}", title).replace("{{TITLE_BLOCK}}", MAIN_TITLE_BLOCK.replace("{{TITLE}}", title))
    main_body = canonical_body(main_src, is_si=False)
    # achemso carries keywords in the preamble; re-inject them after the abstract
    kw_match = re.search(r"\\keywords\{(.+?)\}", main_src, re.DOTALL)
    if kw_match:
        kw_line = "\\noindent\\textbf{Keywords:} " + kw_match.group(1).strip()
        main_body = main_body.replace(r"\end{abstract}", "\\end{abstract}\n\n" + kw_line, 1)
    main_out += "\n" + main_body + "\n\n\\end{document}\n"
    (chemrxiv_dir / MAIN_OUT).write_text(main_out, encoding="utf-8")
    print(f"✅ Converted main -> {chemrxiv_dir / MAIN_OUT}")

    # Assemble SM
    sm_out = SM_TEMPLATE.replace("{{TITLE}}", title)
    sm_out += "\n" + canonical_body(sm_src, is_si=True) + "\n\n\\end{document}\n"
    (chemrxiv_dir / SM_OUT).write_text(sm_out, encoding="utf-8")
    print(f"✅ Converted SM   -> {chemrxiv_dir / SM_OUT}")

    print("\n🎉 Conversion complete!")
    print(f"📁 Output directory: {chemrxiv_dir}")
    print("\n⚠️  Build order: pdflatex main; pdflatex SM; pdflatex main; pdflatex SM (xr cross-refs)")


if __name__ == "__main__":
    main()
