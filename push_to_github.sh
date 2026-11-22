#!/bin/bash
# Network Transformation Command Centre — GitHub Push Script
# Usage: ./push_to_github.sh <github_username> <repo_name>

USERNAME=${1:-"YOUR_USERNAME"}
REPO=${2:-"network-transformation-command-centre"}

if [ "$USERNAME" = "YOUR_USERNAME" ]; then
    echo "Usage: ./push_to_github.sh <github_username> <repo_name>"
    echo "Example: ./push_to_github.sh johndoe network-command-centre"
    exit 1
fi

# Create repo on GitHub (manual step — user does this in browser first)
echo "Step 1: Create repo at https://github.com/new"
echo "         Name: $REPO (public or private)"
echo "         Do NOT initialize with README"
echo ""
read -p "Press Enter after creating the repo..."

# Clone the empty repo
git clone https://github.com/$USERNAME/$REPO.git
cd $REPO

# Copy external folder contents into repo root
cp -r ../assets ../data ../docs ../generate_dashboard.py ../generate_risk_model.py ../requirements.txt ../LICENSE ../.gitignore ../.gitattributes ../README.md . 2>/dev/null || true

git add .
git commit -m "Initial portfolio: Network Transformation Command Centre

- Executive dashboard with synthetic programme data
- AI risk-scoring model (RF, AUC=0.846)
- Governance simulation pack (board pack, steering minutes, escalation, QBR, weekly flash)
- Reproducible synthetic dataset (seed 42)
- Dashboard + model generation scripts"

git push -u origin main

echo ""
echo "Done! Your portfolio is live at:"
echo "https://github.com/$USERNAME/$REPO"
echo ""
echo "Preview the README:"
echo "https://github.com/$USERNAME/$REPO/blob/main/README.md"
