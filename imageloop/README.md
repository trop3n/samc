### Make the Script Executable

```
chmod +x ~/kiosk.sh
```

### Configure Autostart

#### For Raspberry Pi OS with desktop (using LXDE):


```
mkdir -p ~/.config/lxsession/LXDE-pi
echo "@lxterminal -e /home/pi/kiosk.sh" > ~/.config/lxsession/LXDE-pi/autostart
```

### Or for system-wide configuration:

```
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

#### Add this line at the end:


```
@/home/pi/kiosk.sh
```

### Optional: Install Unclutter (for hiding mouse cursor)

```
sudo apt update && sudo apt install unclutter
```

### Reboot to Test

```
sudo reboot
```

#### Important Notes:

    The script waits 10 seconds to ensure network connectivity

    --kiosk flag enables fullscreen mode in Chromium

    --incognito prevents browser from restoring previous session

    xset commands disable screen blanking

    Adjust the sleep time if needed for your network speed

### Troubleshooting:

    Check if Chromium is installed: sudo apt install chromium-browser

    Test the script manually before setting up autostart

    Check system logs with journalctl -u lightdm