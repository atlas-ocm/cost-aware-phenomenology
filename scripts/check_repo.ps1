param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CapRoot = Split-Path -Parent $ScriptDir
$ReferenceRoot = Join-Path $CapRoot "reference\python"
$Requirements = Join-Path $ReferenceRoot "requirements.txt"

Push-Location $CapRoot
try {
    Write-Host "CAP reproducibility check"
    Write-Host "Root: $CapRoot"

    if ($Install) {
        Write-Host ""
        Write-Host "Installing Python requirements..."
        python -m pip install -r $Requirements
    }

    Write-Host ""
    Write-Host "Checking dependency imports..."
    $previousErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $depCheck = & python -c "import jsonschema, pytest; print('dependencies ok')" 2>&1
    $depExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorPreference
    if ($depExitCode -ne 0) {
        Write-Host $depCheck
        Write-Host ""
        Write-Host "Missing Python dependencies. Run:"
        Write-Host "  .\scripts\check_repo.ps1 -Install"
        exit 2
    }
    Write-Host $depCheck

    Write-Host ""
    Write-Host "Compiling reference Python..."
    python -m compileall -q reference\python

    Write-Host ""
    Write-Host "Running unit tests..."
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    python -m pytest -q -p no:cacheprovider reference\python\tests

    Write-Host ""
    Write-Host "Validating artifact integrity..."
    python reference\python\scripts\validate_artifacts.py

    Write-Host ""
    Write-Host "Running LLM proxy policy pack..."
    python reference\python\scripts\run_proxy_policy_pack.py --print-md

    Write-Host ""
    Write-Host "Running LLM proxy policy demo..."
    python reference\python\scripts\demo_llm_proxy_policy.py --counter-source

    Write-Host ""
    Write-Host "Running CAP Lite middleware demo..."
    python reference\python\cap_lite.py

    Write-Host ""
    Write-Host "Running LLM dialogue benchmark scaffold..."
    python reference\python\scripts\run_llm_dialogue_benchmark.py --print-md

    Write-Host ""
    Write-Host "Rendering LLM dialogue benchmark prompt manifest..."
    $PromptManifest = Join-Path $env:TEMP "cap_llm_dialogue_prompt_manifest.json"
    python reference\python\scripts\generate_llm_dialogue_outputs.py --dry-run --output-json $PromptManifest

    Write-Host ""
    Write-Host "Running hard holdout scaffold..."
    $HardHoldoutReport = Join-Path $env:TEMP "cap_hard_holdout_report.md"
    $HardHoldoutReportJson = Join-Path $env:TEMP "cap_hard_holdout_report.json"
    python reference\python\scripts\run_llm_dialogue_benchmark.py `
        --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
        --outputs-json validation_artifacts\llm_dialogue_benchmark\hard_holdout\fixture_outputs\smoke_outputs.json `
        --output-md $HardHoldoutReport `
        --output-json $HardHoldoutReportJson | Out-Null
    Write-Host "Hard holdout scaffold report written: $HardHoldoutReport"

    Write-Host ""
    Write-Host "Running hard holdout deterministic rewrite shaper smoke..."
    $ShapedOutputs = Join-Path $env:TEMP "cap_hard_holdout_shaped_outputs.json"
    $ShaperSummary = Join-Path $env:TEMP "cap_hard_holdout_shaper_summary.json"
    python reference\python\scripts\run_proxy_rewrite_shaper.py `
        --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
        --outputs-json validation_artifacts\llm_dialogue_benchmark\hard_holdout\model_outputs\qwen35_9b_no_thinking_hard_holdout_outputs.json `
        --output-json $ShapedOutputs `
        --summary-json $ShaperSummary | Out-Null
    Write-Host "Hard holdout shaped outputs written: $ShapedOutputs"

    Write-Host ""
    Write-Host "Rendering hard holdout prompt manifest..."
    $HardHoldoutPromptManifest = Join-Path $env:TEMP "cap_hard_holdout_prompt_manifest.json"
    python reference\python\scripts\generate_llm_dialogue_outputs.py `
        --dry-run `
        --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
        --template-dir validation_artifacts\llm_dialogue_benchmark\prompt_templates_hardened_v2 `
        --output-json $HardHoldoutPromptManifest

    Write-Host ""
    Write-Host "Rendering presentable prompt manifest..."
    $PresentablePromptManifest = Join-Path $env:TEMP "cap_presentable_prompt_manifest.json"
    python reference\python\scripts\generate_llm_dialogue_outputs.py `
        --dry-run `
        --case-dir validation_artifacts\llm_dialogue_benchmark\hard_holdout\cases `
        --template-dir validation_artifacts\llm_dialogue_benchmark\prompt_templates_presentable `
        --output-json $PresentablePromptManifest

    Write-Host ""
    Write-Host "Rendering blinded adjudication pack..."
    $AdjudicationDir = Join-Path $env:TEMP "cap_llm_dialogue_adjudication"
    python reference\python\scripts\prepare_llm_dialogue_adjudication.py --output-dir $AdjudicationDir

    Write-Host ""
    Write-Host "Rendering TSV adjudication label sheet..."
    $AdjudicationTsv = Join-Path $AdjudicationDir "manual_labels_template.tsv"
    python reference\python\scripts\adjudication_labels_tsv.py export --adjudication-dir $AdjudicationDir --output-tsv $AdjudicationTsv

    Write-Host ""
    Write-Host "Rendering model-graded auditor prompt pack..."
    $AuditorDir = Join-Path $env:TEMP "cap_model_graded_auditor"
    python reference\python\scripts\prepare_model_graded_auditor.py --output-dir $AuditorDir --limit-records 3 --print-summary

    Write-Host ""
    Write-Host "Rendering adjudication disagreement scaffold..."
    python reference\python\scripts\analyze_adjudication_disagreements.py --adjudication-dir $AdjudicationDir --labels-tsv $AdjudicationTsv --print-md

    Write-Host ""
    Write-Host "CAP reproducibility check passed."
}
finally {
    Pop-Location
}
