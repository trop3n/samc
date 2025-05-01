# configurable variables
$nasPath = "Z:\Path\To\Monitor" # NAS Directory to Watch
$localPath = "C:\Local\Target"  # Local directory to move files to

$logFile = "$env:TEMP\FileMover.log"
function Log-Message {
    Param ([string]$message)
    "$timestamp - $message" | Out-File -Append -FilePath $logFile
}