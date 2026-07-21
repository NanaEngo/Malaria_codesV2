#!/bin/bash
# Prepare MD repository for GitHub push
# Keeps essential files, excludes large GROMACS outputs

set -e

echo "================================================================================"
echo "PREPARING MD PROJECT FOR GITHUB"
echo "================================================================================"
echo ""

cd /home/vital/Documents/GitHub/Malaria_codes/Project2_Polypharmacology_MD_Validation/Tuto_MD_MC

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "❌ .gitignore not found! Run this from Tuto_MD_MC directory."
    exit 1
fi

echo "✓ Found .gitignore"
echo ""

# Show what will be tracked vs ignored
echo "================================================================================"
echo "CHECKING WHAT WILL BE COMMITTED"
echo "================================================================================"
echo ""

echo "📁 Essential files that WILL be tracked:"
echo "  - Python scripts (*.py)"
echo "  - Shell scripts (*.sh)"
echo "  - Documentation (*.md, *.txt)"
echo "  - MDP files (*.mdp)"
echo "  - Topology files (*.top, *.itp)"
echo "  - Initial structures (complex.gro, restraint.gro)"
echo "  - Index files (*.ndx)"
echo "  - Analysis plots (*.png in comprehensive_analysis/)"
echo ""

echo "🚫 Large files that will be IGNORED:"
echo "  - Trajectories (*.xtc, *.trr, *.dcd)"
echo "  - Binary files (*.tpr, *.cpt, *.edr)"
echo "  - Log files (*.log)"
echo "  - Intermediate structures (step*.gro)"
echo "  - Large analysis outputs (*.xvg)"
echo ""

# Check for large files that might accidentally be staged
echo "================================================================================"
echo "CHECKING FOR LARGE FILES"
echo "================================================================================"
echo ""

large_files=$(find . -type f -size +10M 2>/dev/null | grep -v ".git" | head -10 || true)

if [ -n "$large_files" ]; then
    echo "⚠️  Found large files (>10 MB):"
    echo "$large_files" | while read file; do
        size=$(du -h "$file" | cut -f1)
        echo "  - $file ($size)"
    done
    echo ""
    echo "These should be in .gitignore. Verifying..."
    echo ""
    
    # Check if they're ignored
    ignored_count=0
    total_count=0
    echo "$large_files" | while read file; do
        total_count=$((total_count + 1))
        if git check-ignore -q "$file" 2>/dev/null; then
            ignored_count=$((ignored_count + 1))
            echo "  ✓ $file (ignored)"
        else
            echo "  ⚠️  $file (NOT IGNORED - will be committed!)"
        fi
    done
else
    echo "✓ No large files found (or all are properly ignored)"
fi

echo ""

# Show directory sizes
echo "================================================================================"
echo "DIRECTORY SIZES"
echo "================================================================================"
echo ""

echo "Total project size:"
du -sh . | cut -f1
echo ""

echo "Size breakdown:"
du -sh Gromacs_inputs/ 2>/dev/null || echo "  Gromacs_inputs/: not found"
du -sh Test/ 2>/dev/null || echo "  Test/: not found"
du -sh ligands/ 2>/dev/null || echo "  ligands/: not found"
du -sh protein_prep/ 2>/dev/null || echo "  protein_prep/: not found"
echo ""

# Estimate what will be committed
echo "================================================================================"
echo "ESTIMATED COMMIT SIZE"
echo "================================================================================"
echo ""

echo "Calculating size of tracked files..."
tracked_size=$(git ls-files | xargs -I {} du -ch "{}" 2>/dev/null | tail -1 | cut -f1 || echo "unknown")
echo "Current tracked files: $tracked_size"
echo ""

# Show git status summary
echo "================================================================================"
echo "GIT STATUS SUMMARY"
echo "================================================================================"
echo ""

git status --short | wc -l | xargs echo "Files with changes:"
git status --short | grep "^M" | wc -l | xargs echo "  Modified:"
git status --short | grep "^A" | wc -l | xargs echo "  Added:"
git status --short | grep "^D" | wc -l | xargs echo "  Deleted:"
git status --short | grep "^??" | wc -l | xargs echo "  Untracked:"
echo ""

# Show untracked files that WILL be added
echo "================================================================================"
echo "NEW FILES TO ADD (first 20)"
echo "================================================================================"
echo ""

untracked=$(git ls-files --others --exclude-standard | head -20)
if [ -n "$untracked" ]; then
    echo "$untracked"
    total_untracked=$(git ls-files --others --exclude-standard | wc -l)
    echo ""
    echo "Total untracked files: $total_untracked"
else
    echo "No untracked files (all new files already staged or ignored)"
fi

echo ""

# Check if we're on a git branch
echo "================================================================================"
echo "GIT BRANCH INFO"
echo "================================================================================"
echo ""

current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"

# Check for remote
remote=$(git remote -v | head -1 || echo "")
if [ -n "$remote" ]; then
    echo "Remote configured:"
    git remote -v
else
    echo "⚠️  No remote configured. You'll need to add one:"
    echo "   git remote add origin <your-github-repo-url>"
fi

echo ""

# Final recommendations
echo "================================================================================"
echo "NEXT STEPS"
echo "================================================================================"
echo ""

echo "1. REVIEW .gitignore (already created)"
echo "   - Edit if needed: nano .gitignore"
echo ""

echo "2. ADD AND COMMIT essential files:"
echo "   git add ."
echo "   git status  # Review what will be committed"
echo "   git commit -m 'Add MD analysis scripts and documentation'"
echo ""

echo "3. ADD REMOTE (if not already configured):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo ""

echo "4. PUSH TO GITHUB:"
echo "   git push -u origin main  # or 'master' depending on your default branch"
echo ""

echo "5. VERIFY on GitHub:"
echo "   - Check repository size (should be small, <100 MB)"
echo "   - Verify no .xtc, .trr, or other large files present"
echo "   - Confirm all documentation and scripts are there"
echo ""

echo "================================================================================"
echo "⚠️  IMPORTANT REMINDERS"
echo "================================================================================"
echo ""
echo "✓ Large trajectory files (.xtc, .trr) will be IGNORED"
echo "✓ Binary files (.tpr, .cpt, .edr) will be IGNORED"
echo "✓ Only essential inputs and scripts will be tracked"
echo "✓ Analysis plots and documentation WILL be tracked"
echo ""
echo "To regenerate GROMACS outputs on another machine:"
echo "  1. Clone repository"
echo "  2. Run MD simulations with provided input files"
echo "  3. Run analysis scripts on generated trajectories"
echo ""

echo "================================================================================"
echo "PREPARATION COMPLETE!"
echo "================================================================================"
