#!/usr/bin/env sh
# Commit and push new reports. Run from the repository root after the daily report.
# Example crontab line (the reporter runs at 07:00 UTC):
#   30 7 * * * cd /opt/kalshi-maker && sh scripts/publish_reports.sh >> publish.log 2>&1
set -eu
git add reports
if git diff --cached --quiet; then
  echo "no new report"
  exit 0
fi
git commit -m "report: $(date -u +%F)" --quiet
git push --quiet
echo "pushed report $(date -u +%F)"
