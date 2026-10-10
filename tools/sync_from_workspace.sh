#!/bin/sh
# Refresh this repository from the science workspace. Usage: tools/sync_from_workspace.sh [workspace] (default ~/Terramind/science)
# The experiment keeps its own history and comes in with git subtree, so its commit ids stay the ones the paper cites.
# Paper files and the journey log are copied. Unsent correspondence (paper/emails.md) and third-party sources stay out.
set -e
W="${1:-$HOME/Terramind/science}"; cd "$(dirname "$0")/.."
git subtree pull --prefix=fly-brain/experiment "$W/video-01-fly-brain/experiment" main -m "Update fly-brain experiment from the workspace"
rsync -a --delete --exclude 'emails.md' --exclude '*.html' --exclude '__pycache__' "$W/video-01-fly-brain/paper/" fly-brain/paper/
cp "$W/video-01-fly-brain/JOURNEY.md" fly-brain/JOURNEY.md
git status --short
