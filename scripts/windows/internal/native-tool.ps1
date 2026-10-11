# Keep native execution in PowerShell: argument arrays, console cancellation and
# waiting for the ordinary CLI/child process lifetime remain owned by the shell.
function Invoke-ConfectoryNativeTool {
    param([string]$Executable, [string[]]$ToolArguments, [string]$LogPath)
    $runState = @{ ExitCode = -1 }
    $writer = New-Object System.IO.StreamWriter($LogPath, $true, (New-Object System.Text.UTF8Encoding($false)))
    $writer.AutoFlush = $true
    try {
        & {
            # Windows PowerShell 5.1 wraps redirected native stderr in ErrorRecord.
            # Continue applies ONLY at this native boundary, not to log IO/callers.
            $ErrorActionPreference = 'Continue'
            $global:LASTEXITCODE = -1
            & $Executable @ToolArguments 2>&1
            $runState.ExitCode = $LASTEXITCODE
        } | ForEach-Object {
            # Normalize before host formatting: keep the actual stderr message,
            # without misleading NativeCommandError/CategoryInfo decorations.
            $line = $_.ToString()
            $writer.WriteLine($line)
            Write-Host $line
        }
    } finally {
        $writer.Dispose()
    }
    return [int]$runState.ExitCode
}
