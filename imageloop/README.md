### Modify the Service File

```
sudo nano /etc/systemd/system/kiosk.service
```

Change to:

```
[Unit]
Description=Kiosk Mode
After=graphical.target network-online.target
Wants=network-online.target

[Service]
User=pi
Environment=DISPLAY=:0
ExecStart=/home/pi/kiosk.sh
Restart=on-failure
RestartSec=5
# Keep service active even if main process forks
Type=simple

[Install]
WantedBy=graphical.target
```

### Critical Follow-Up Commands

```
# Reload systemd config
sudo systemctl daemon-reload
# Restart service
sudo systemctl restart kiosk.service
# Monitor logs in real-time
journalctl -u kiosk.service -f
```

### Troubleshooting Checklist

    Verify Chromium path


    which chromium-browser || which chromium

    (Update script with correct path if needed)

    Check X permissions

    ls -l /home/pi/.Xauthority

    Test browser manually
    bash

    startx /home/pi/kiosk.sh

    Increase GPU memory
    In /boot/config.txt:

    gpu_mem=256

### Expected Behavior

Now your service should:

    Wait for X server and network

    Keep Chromium running continuously

    Auto-restart on crashes

    Maintain active status in systemd

Let me know if you see specific errors in the updated logs!