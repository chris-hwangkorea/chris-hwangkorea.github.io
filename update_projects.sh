#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

python3 generate_projects.py
python3 -m unittest discover -s tests -v

git add projects.html projects.json generate_projects.py update_projects.sh tests/test_generate_projects.py
if git diff --cached --quiet; then
  echo "프로젝트 목록에 변경이 없습니다."
  exit 0
fi

git commit -m "chore: 프로젝트 대시보드 자동 갱신"
git push origin master
