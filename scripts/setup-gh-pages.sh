#!/bin/bash

# Setup script for GitHub Pages coverage badge
# This script creates the gh-pages branch if it doesn't exist

set -e

echo "🚀 Setting up GitHub Pages for coverage badge..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if gh-pages branch already exists
if git show-ref --verify --quiet refs/remotes/origin/gh-pages; then
    echo "✅ gh-pages branch already exists on remote"
    echo "📝 You can skip to step 2 in the documentation"
    exit 0
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "💡 Consider committing or stashing them before proceeding"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Create orphan gh-pages branch
echo "🌿 Creating orphan gh-pages branch..."
git switch --orphan gh-pages

# Create initial commit
echo "📝 Creating initial commit..."
git commit --allow-empty -m "Initial commit for GitHub Pages"

# Push to remote
echo "🚀 Pushing gh-pages branch to remote..."
git push -u origin gh-pages

# Return to original branch
echo "🔄 Returning to original branch: $CURRENT_BRANCH"
git switch "$CURRENT_BRANCH"

echo ""
echo "✅ GitHub Pages setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your repository Settings -> Pages"
echo "2. Select 'Deploy from a branch'"
echo "3. Choose 'gh-pages' branch and '/' folder"
echo "4. Click Save"
echo ""
echo "🔧 Also ensure workflow permissions:"
echo "   Settings -> Actions -> General -> Workflow permissions"
echo "   Select 'Read and Write permissions'"
echo ""
echo "🎉 Your coverage badge will appear after the next push to main!" 