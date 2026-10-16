#!/bin/bash
cd /home/madhukumarm/SweetyAI
export DISPLAY=:0
export XDG_SESSION_TYPE=wayland

echo "[$(date)] Starting SweetyAI Morning Briefing Generation..."
python3 sweety.py diary briefing > /dev/null 2>&1

echo "[$(date)] Dispatching WhatsApp Briefing via CUA..."
python3 sweety_cua.py --env local --grant-control --task whatsapp --target "9844637595"
echo "[$(date)] Morning briefing dispatch complete."
