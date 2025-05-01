## Step 1: Map the NAS Network Drive

    Open File Explorer.

    Map the Synology NAS folder as a network drive (e.g., Z:\).

    Ensure "Reconnect at sign-in" is checked to persist the connection.

## Step 2: Run Script as Administrator

    Open PowerShell as Administrator.

    Run the script:

        Set-ExecutionPolicy RemoteSigned -Force  # Allow script execution if blocked
        .\MoveFilesFromNAS.ps1

    To close, press Ctrl + C.

## Step 3: Schedule to Run at Statup

    Press Win + R, type taskschd.msc, and open Task Scheduler.

    Create a new task:

        Trigger: "At log on".

        Action: Start a program: powershell.exe.

        Arguments: -WindowStyle Hidden -File "C:\Path\To\MoveFilesFromNAS.ps1".

    Set it to run with highest privileges.

### Notes

    Permissions: Ensure the script has read/write access to both the NAS and local directory.

    Network Reliability: If the NAS disconnects, remap the drive or add reconnection logic.

    File Locks: The Start-Sleep gives time for files to finish copying.

    Logs: Check %TEMP%\FileMover.log for activity or errors.