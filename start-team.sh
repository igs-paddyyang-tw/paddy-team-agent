#!/bin/bash
cd "$(dirname "$0")"

while true; do
    echo "[$(date)] Starting Ark Agent Platform..."
    python3 start.py

    if [ -f "restart.flag" ]; then
        rm "restart.flag"
        echo "[$(date)] Restart requested, restarting in 3s..."
        sleep 3
    else
        echo "[$(date)] Stopped."
        break
    fi
done
