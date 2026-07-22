# check_repo.helpers.ps1
#
# Centralized fail-fast helper for check_repo.ps1.
#
# Background: under $ErrorActionPreference = "Stop", a *native* process
# (python, pytest, ...) that exits non-zero does NOT terminate the script,
# and its failure is not reflected in the script's final exit code. So the
# orchestrator could print "CAP reproducibility check passed" even though a
# validator process had died. Invoke-Checked closes that gap: it inspects the
# observed process exit code (not printed text) and aborts on the first failure.
#
# Acceptance contract enforced by callers of this helper:
#   CHECK_REPO_PASS := every required child was invoked
#                      AND every required child exited 0
#                      AND the success footer was reached
#
# This file is dot-sourced by check_repo.ps1 and by check_repo.selftest.ps1 so
# both exercise the identical mechanism.

# Populated by Invoke-Checked immediately before it throws, so a catch block in
# the caller can preserve the original failing exit code.
$script:LastFailedExitCode = $null

function Invoke-Checked {
    <#
    .SYNOPSIS
    Run a native-command scriptblock and throw if it exits non-zero.

    .DESCRIPTION
    Executes $Command, then reads $LASTEXITCODE (the exit code of the last
    native process run by the scriptblock). If it is non-zero, records the code
    in $script:LastFailedExitCode and throws a terminating error so the caller's
    try/catch aborts before any subsequent step or success footer runs.
    #>
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Label,

        [Parameter(Mandatory = $true, Position = 1)]
        [scriptblock]$Command
    )

    $global:LASTEXITCODE = 0
    & $Command
    $code = $LASTEXITCODE

    if ($null -ne $code -and $code -ne 0) {
        $script:LastFailedExitCode = $code
        throw "validation step failed: $Label (exit code $code)"
    }
}
