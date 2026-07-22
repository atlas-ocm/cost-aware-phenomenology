# check_repo.selftest.ps1
#
# Adversarial regression proof for the check_repo.ps1 fail-fast mechanism.
#
# It does NOT touch any real committed validator. It writes a tiny isolated
# harness that dot-sources the SAME check_repo.helpers.ps1 used by check_repo.ps1
# and mirrors its try/catch structure, then runs that harness as a child
# PowerShell process against a deliberately failing child command and against a
# passing one. It asserts:
#
#   failing child  => parent observes the non-zero exit, aborts before the
#                     sentinel / success footer, and itself exits non-zero
#                     (preserving the child's exit code);
#   passing child  => parent runs the sentinel and success footer and exits 0.
#
# Exit code: 0 if every assertion holds, 1 otherwise.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Helper = Join-Path $ScriptDir "check_repo.helpers.ps1"

if (-not (Test-Path $Helper)) {
    Write-Host "SELFTEST ERROR: helper not found at $Helper"
    exit 1
}

# Isolated harness that mirrors check_repo.ps1's structure. Single-quoted
# here-string: nothing here is expanded by this parent script.
$harness = @'
param(
    [Parameter(Mandatory = $true)][string]$HelperPath,
    [Parameter(Mandatory = $true)][int]$ChildExit
)
$ErrorActionPreference = "Stop"
. $HelperPath
try {
    Invoke-Checked "selftest child" { cmd /c "echo All checks passed OK & exit $ChildExit" }
    Write-Host "SENTINEL_AFTER_VALIDATION"
    Write-Host "CAP reproducibility check passed."
}
catch {
    Write-Host ("SELFTEST_ABORTED: " + $_.Exception.Message)
    if ($script:LastFailedExitCode) { exit $script:LastFailedExitCode }
    exit 1
}
'@

$harnessPath = Join-Path ([System.IO.Path]::GetTempPath()) "cap_check_repo_selftest_harness.ps1"
Set-Content -Path $harnessPath -Value $harness -Encoding UTF8

$failures = @()

try {
    # --- Failure path: child exits 7 ---
    $failOut = & powershell -NoProfile -ExecutionPolicy Bypass -File $harnessPath -HelperPath $Helper -ChildExit 7 2>&1
    $failCode = $LASTEXITCODE
    $failText = ($failOut | Out-String)

    Write-Host "== Failure-path child output (exit code $failCode) =="
    Write-Host $failText

    if ($failCode -eq 0) { $failures += "failure path: parent exit code was 0 (expected non-zero)" }
    if ($failCode -ne 7) { $failures += "failure path: parent exit code was $failCode (expected 7, the child's code preserved)" }
    if ($failText -match "SENTINEL_AFTER_VALIDATION") { $failures += "failure path: subsequent step ran (SENTINEL printed) after a failed validation" }
    if ($failText -match "CAP reproducibility check passed") { $failures += "failure path: success footer was emitted after a failed validation" }
    if ($failText -notmatch "SELFTEST_ABORTED") { $failures += "failure path: abort message was not emitted" }

    # --- Success path: child exits 0 ---
    $okOut = & powershell -NoProfile -ExecutionPolicy Bypass -File $harnessPath -HelperPath $Helper -ChildExit 0 2>&1
    $okCode = $LASTEXITCODE
    $okText = ($okOut | Out-String)

    Write-Host "== Success-path child output (exit code $okCode) =="
    Write-Host $okText

    if ($okCode -ne 0) { $failures += "success path: parent exit code was $okCode (expected 0)" }
    if ($okText -notmatch "SENTINEL_AFTER_VALIDATION") { $failures += "success path: subsequent step did not run (SENTINEL missing)" }
    if ($okText -notmatch "CAP reproducibility check passed") { $failures += "success path: success footer was not emitted" }
}
finally {
    Remove-Item -Path $harnessPath -Force -ErrorAction SilentlyContinue
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "check_repo.selftest: PASS - fail-fast mechanism aborts on non-zero and continues on zero."
    exit 0
}

Write-Host "check_repo.selftest: FAIL"
foreach ($f in $failures) {
    Write-Host "  - $f"
}
exit 1
