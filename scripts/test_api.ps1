# PowerShell script to test API endpoints (local and ngrok)

param(
    [string]$NgrokUrl = ""
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "API Connection Test" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$localUrl = "http://localhost:8000"

Write-Host ""
Write-Host "Testing Local API (http://localhost:8000)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

# Test Health Endpoint
try {
    $healthResponse = Invoke-RestMethod -Uri "$localUrl/api/health" -Method Get -ErrorAction Stop
    Write-Host "[OK] Health Check (Local): SUCCESS" -ForegroundColor Green
    Write-Host "     Response: $($healthResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
    $localHealthOk = $true
} catch {
    Write-Host "[FAIL] Health Check (Local): FAILED" -ForegroundColor Red
    Write-Host "       Error: $($_.Exception.Message)" -ForegroundColor Red
    $localHealthOk = $false
}

# Test Root Endpoint
try {
    $rootResponse = Invoke-RestMethod -Uri "$localUrl/" -Method Get -ErrorAction Stop
    Write-Host "[OK] Root Endpoint (Local): SUCCESS" -ForegroundColor Green
    Write-Host "     Response: $($rootResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
    $localRootOk = $true
} catch {
    Write-Host "[FAIL] Root Endpoint (Local): FAILED" -ForegroundColor Red
    Write-Host "       Error: $($_.Exception.Message)" -ForegroundColor Red
    $localRootOk = $false
}

if ($localHealthOk -and $localRootOk) {
    Write-Host ""
    Write-Host "[OK] Local API is working!" -ForegroundColor Green
    
    # Test Diff Endpoint
    Write-Host ""
    Write-Host "Testing Diff Endpoint..." -ForegroundColor Yellow
    try {
        $diffBody = @{
            source_content = "key1=value1`nkey2=value2"
            target_content = "key1=value1`nkey2=value3"
            normalize = $true
        } | ConvertTo-Json
        
        $diffResponse = Invoke-RestMethod -Uri "$localUrl/api/diff" -Method Post -Body $diffBody -ContentType "application/json" -ErrorAction Stop
        Write-Host "[OK] Diff Endpoint (Local): SUCCESS" -ForegroundColor Green
        Write-Host "     Changes detected: $($diffResponse.changes.Count)" -ForegroundColor Gray
        Write-Host "     Summary: $($diffResponse.summary | ConvertTo-Json -Compress)" -ForegroundColor Gray
    } catch {
        Write-Host "[FAIL] Diff Endpoint (Local): FAILED" -ForegroundColor Red
        Write-Host "       Error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "[FAIL] Local API is not responding. Make sure the server is running:" -ForegroundColor Red
    Write-Host "       poetry run python scripts/run_api.py" -ForegroundColor Yellow
}

# Test ngrok if URL provided
if ($NgrokUrl) {
    $NgrokUrl = $NgrokUrl.TrimEnd('/')
    Write-Host ""
    Write-Host "Testing ngrok URL ($NgrokUrl)" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    # Test Health Endpoint
    try {
        $ngrokHealthResponse = Invoke-RestMethod -Uri "$NgrokUrl/api/health" -Method Get -ErrorAction Stop
        Write-Host "[OK] Health Check (ngrok): SUCCESS" -ForegroundColor Green
        Write-Host "     Response: $($ngrokHealthResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
        $ngrokHealthOk = $true
    } catch {
        Write-Host "[FAIL] Health Check (ngrok): FAILED" -ForegroundColor Red
        Write-Host "       Error: $($_.Exception.Message)" -ForegroundColor Red
        $ngrokHealthOk = $false
    }
    
    # Test Root Endpoint
    try {
        $ngrokRootResponse = Invoke-RestMethod -Uri "$NgrokUrl/" -Method Get -ErrorAction Stop
        Write-Host "[OK] Root Endpoint (ngrok): SUCCESS" -ForegroundColor Green
        Write-Host "     Response: $($ngrokRootResponse | ConvertTo-Json -Compress)" -ForegroundColor Gray
        $ngrokRootOk = $true
    } catch {
        Write-Host "[FAIL] Root Endpoint (ngrok): FAILED" -ForegroundColor Red
        Write-Host "       Error: $($_.Exception.Message)" -ForegroundColor Red
        $ngrokRootOk = $false
    }
    
    if ($ngrokHealthOk -and $ngrokRootOk) {
        Write-Host ""
        Write-Host "[OK] ngrok tunnel is working!" -ForegroundColor Green
        
        # Test Diff Endpoint
        Write-Host ""
        Write-Host "Testing Diff Endpoint through ngrok..." -ForegroundColor Yellow
        try {
            $diffBody = @{
                source_content = "key1=value1`nkey2=value2"
                target_content = "key1=value1`nkey2=value3"
                normalize = $true
            } | ConvertTo-Json
            
            $ngrokDiffResponse = Invoke-RestMethod -Uri "$NgrokUrl/api/diff" -Method Post -Body $diffBody -ContentType "application/json" -ErrorAction Stop
            Write-Host "[OK] Diff Endpoint (ngrok): SUCCESS" -ForegroundColor Green
            Write-Host "     Changes detected: $($ngrokDiffResponse.changes.Count)" -ForegroundColor Gray
            Write-Host "     Summary: $($ngrokDiffResponse.summary | ConvertTo-Json -Compress)" -ForegroundColor Gray
        } catch {
            Write-Host "[FAIL] Diff Endpoint (ngrok): FAILED" -ForegroundColor Red
            Write-Host "       Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host ""
        Write-Host "[FAIL] ngrok tunnel is not working. Check:" -ForegroundColor Red
        Write-Host "       1. Is ngrok running? (ngrok http 8000)" -ForegroundColor Yellow
        Write-Host "       2. Is the API server running?" -ForegroundColor Yellow
        Write-Host "       3. Is the ngrok URL correct?" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "To test ngrok, run:" -ForegroundColor Cyan
    Write-Host "   .\scripts\test_api.ps1 -NgrokUrl https://your-ngrok-url.ngrok-free.app" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
