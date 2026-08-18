#!/usr/bin/env python3
"""Fix Unicode characters in LaTeX files by converting them to proper LaTeX commands."""

# Read the file
with open('Chapters/chap_to_met.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements - simple string replacements (no regex)
replacements = [
    # Superscripts
    ('⁻', '$^{-}$'),
    ('⁰', '$^{0}$'),
    ('¹', '$^{1}$'),
    ('²', '$^{2}$'),
    ('³', '$^{3}$'),
    ('⁴', '$^{4}$'),
    ('⁵', '$^{5}$'),
    ('⁶', '$^{6}$'),
    ('⁷', '$^{7}$'),
    ('⁸', '$^{8}$'),
    ('⁹', '$^{9}$'),
    ('⊗', r'$\otimes$'),
    
    # Subscripts
    ('₀', '$_{0}$'),
    ('₁', '$_{1}$'),
    ('₂', '$_{2}$'),
    ('₃', '$_{3}$'),
    ('₄', '$_{4}$'),
    ('₅', '$_{5}$'),
    ('₆', '$_{6}$'),
    ('₇', '$_{7}$'),
    ('₈', '$_{8}$'),
    ('₉', '$_{9}$'),
    ('ᵢ', '$_{i}$'),
    ('ⱼ', '$_{j}$'),
    ('ₜ', '$_{t}$'),
    ('ᵥ', '$_{v}$'),
    ('ᵤ', '$_{u}$'),
    
    # Mathematical symbols
    ('∈', r'$\in$'),
    ('∩', r'$\cap$'),
    ('∪', r'$\cup$'),
    ('⋃', r'$\bigcup$'),
    ('≤', r'$\leq$'),
    ('−', '-'),
    ('×', r'$\times$'),
    ('·', r'$\cdot$'),
    
    # Greek letters - replace individually since they're in different contexts
    ('Σᵢ', r'$\Sigma_i$'),
    ('Σₜ', r'$\Sigma_t$'),
    ('Σⱼ', r'$\Sigma_j$'),
    ('γ ', r'$\gamma$ '),
    ('ε^', r'$\varepsilon$\^{}'),
    ('φ(', r'$\phi$('),
    ('α ', r'$\alpha$ '),
]

# Apply replacements
for old, new in replacements:
    content = content.replace(old, new)

# Fix specific patterns requiring more careful handling
content = content.replace('n_estimators', r'n\_estimators')
content = content.replace('max_depth', r'max\_depth')
content = content.replace('min_samples_split', r'min\_samples\_split')
content = content.replace('min_samples_leaf', r'min\_samples\_leaf')
content = content.replace('max_features', r'max\_features')
content = content.replace('class_weight', r'class\_weight')
content = content.replace('gmx_MMPBSA', r'gmx\_MMPBSA')

# Write back
with open('Chapters/chap_to_met.tex', 'w', encoding='utf-8') as f:
    f.write(content)

print("Unicode characters fixed successfully!")
