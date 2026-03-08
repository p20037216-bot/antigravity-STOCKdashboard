#!/bin/bash
echo "Starting Antigravity Trending Crawler Daemon..."
while true; do
  /Users/paengsuseong/.gemini/antigravity/scratch/antigravity-workspace-template/venv/bin/python /Users/paengsuseong/.gemini/antigravity/scratch/antigravity-workspace-template/src/backend/trending_crawler.py >> /Users/paengsuseong/.gemini/antigravity/scratch/antigravity-workspace-template/cron_trending.log 2>&1
  sleep 3600
done
