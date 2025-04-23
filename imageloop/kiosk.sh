#!/bin/bash

# Ensure XAUTHORITY is set
export XAUTHORITY=/home/pi/.Xauthority

# Infinite loop to keep service active
while true; do
  # Wait for X server
  while ! xset q &>/dev/null; do sleep 1; done
  
  # Prevent power management
  xset s noblank
  xset s off
  xset -dpms

  # Hide cursor
  unclutter -idle 0.5 -root &
  
  # Launch browser (foreground, no &)
  chromium-browser --noerrdialogs --kiosk --incognito "http://your-url"
  
  # If browser crashes, wait before restart
  sleep 5
done