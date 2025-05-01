# configurable variables
$nasPath = "Z:\Path\To\Monitor" # NAS Directory to Watch
$localPath = "C:\Local\Target"  # Local directory to move files to

$logFile = "$env:TEMP\FileMover.log"
function Log-Message {
    Param ([string]$message)
    "$timestamp - $message" | Out-File -Append -FilePath $logFile
}

# Create FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $nasPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $folderName = $Event.SourceEventArgs.Name
    $fullPath = Join-Path -Path $nasPath -ChildPath $folderName

    if (Test-Path $fullPath -PathType Container) {
        Start-Sleep -Seconds 5 # wait to avoid partial copies

        Get-ChildItem $fullPath -File | ForEach-Object {
            $destination = Join-Path -Path $localPath -ChildPath $_.Name
            Move-Item $_FullName -Destination $destination -Force
            Log-Message "Moved $($_.Name) to $localPath"
        }
    
        Remove-Item $fullPath - Recurse -Force
        Log-Message "Removed empty folder: $folderName"
    }
}

# register the event and keep the script running
Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action
Log-Message "Starting watcher for $nasPath..."

# Keep the script running indefinitely
while ($true) { Start-Sleep -Seconds 60 }