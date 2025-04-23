#!/bin/bash
# Wait for network connection and X server to load
sleep 10

# prevent xset noblank
xset s noblank
xset s off
xset -dpms

# hide mouse cursor
# unclutter -idle 0.5 -root &

chromium-browser --noerrdialogs --kiosk --incognito "http://192.168.6.54/Students" &