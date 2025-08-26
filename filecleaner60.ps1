<#
.SYNOPSIS
Deletes files older than a specified number of days from a directory.

.DESCRIPTION
This script removes files from a given directory that are older than the specified threshold (60 days, be default)
Use with caution.

.PARAMETER Path
The target directory path (default is current directory).

.PARAMETER Days
Age threshold in days (default is 60).

.PARAMETER Force
Skip confirmation prompt (optional)

.EXAMPLE
.\DeleteOldFiles.ps1 -Path "C:\Temp" -Days 30 -Force
#>

param (
    [string]$Path = $PWD.Path,
    [int]$Days = 60,
    [switch]$Force
)

# Validate if directory exists
if (-not (Test-Path -Path $Path -PathType Container)) {
    Write-Error "Directory '$Path' does not exist or is not a directory."
    exit 1
}

# Calculate the cutoff date
$cutoffDate = (Get-Date).AddDays(-$Days)

# Get files older than specified days
$oldFiles = Get-ChildItem -Path $Path -File | Where-Object { $_.LastWriteTime -lt $cutoffDate }

if (-not $oldFiles) {
    Write-Host "No files older than $Days days found in '$Path'."
}

# Show files to be deleted
Write-Host "The following files will be deleted (older than $Days days):`n"
$oldFiles | ForEach-Object { Write-Host "  $($_.Name)" }

# Confirm deletion unless -Force is used
if (-not $Force) {
    $confirmation = Read-Host "`nContinue with deletion? (y/N)"
    if ($confirmation -notmatch '^[Yy]') {
        Write-Host "Deletion cancelled."
        exit 0
    }
}

# Delete files
$oldFiles | Remove-Item -Verbose
Write-Host "`nDeleted $($oldFiles.Count) file(s)."