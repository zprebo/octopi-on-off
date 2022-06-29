#!/bin/bash

export API_URL="http://octopi.local/api"
export VOICE_MONKEY_API_URL="https://api.voicemonkey.io/trigger"
export AUTO_SHUTDOWN_MONKEY="ender3-auto-shutdown-monkey"
export VOICE_MONKEY_AUTO_SHUTDOWN_SECRET="967c613f62904e5e987fab2ad7309bf9"
export VOICE_MONKEY_AUTO_SHUTDOWN_TOKEN="9e6bb598ce86a24a74a590398f26459e"
export OCTOPI_TOKEN="4AF348B820D64B27B5C9DA1403131A5F"
echo "$(date -d -7hours)MST: Starting Smart Startup launcher.sh"
python3 /home/pi/octopi-on-off/pi_scripts/smart_startup.py >> logs/smart_startup.log
if [ $? -eq 0 ]; then
    echo "$(date -d -7hours)MST: Starting Auto Shutdown launcher.sh"
    python3 /home/pi/octopi-on-off/pi_scripts/auto_shutdown_trigger.py >> logs/auto_shutdown_trigger.log
    if [ $? -eq 0 ]; then
        echo "$(date -d -7hours) MST: Successful Routine Trigger"
    else
        echo "$(date -d -7hours) MST: Command Exited Unsuccessfully"
    fi
else
    echo "$(date -d -7hours) MST: Command Exited Unsuccessfully" 
fi