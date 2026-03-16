#!/usr/bin/env bash
# Hub Health Watchdog
# Checks Hub health every 60 seconds, restarts if down
# Run as: nohup bash hub_watchdog.sh &

LOG="/tmp/hub-watchdog.log"
MAX_FAILURES=3
failures=0

while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:8080/health 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        failures=0
    else
        failures=$((failures + 1))
        echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Hub health check FAILED (HTTP $response, failure $failures/$MAX_FAILURES)" >> "$LOG"
        
        if [ "$failures" -ge "$MAX_FAILURES" ]; then
            echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Hub DOWN — restarting gunicorn..." >> "$LOG"
            
            # Kill existing gunicorn
            pkill -f 'gunicorn.*server:app' 2>/dev/null
            sleep 2
            pkill -9 -f 'gunicorn.*server:app' 2>/dev/null
            sleep 1
            
            # Restart
            cd /home/openclaw/.openclaw/workspace/hub
            export HUB_DATA_DIR=/home/openclaw/.openclaw/workspace/hub-data
            export WORKSPACE_DIR=/home/openclaw/.openclaw/workspace
            export OPENCLAW_CONFIG=/home/openclaw/.openclaw/openclaw.json
            export PATH="/home/openclaw/.local/bin:$PATH"
            
            nohup /home/openclaw/.local/bin/gunicorn -k gevent -w 4 -b 127.0.0.1:8080 --timeout 120 server:app >> /tmp/hub-gunicorn.log 2>&1 &
            echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Gunicorn restarted (PID $!)" >> "$LOG"
            
            failures=0
            sleep 10  # Give it time to boot
        fi
    fi
    
    sleep 60
done
