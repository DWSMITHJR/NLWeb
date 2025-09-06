#Requires -Version 7.0
<#
.SYNOPSIS
    Test script for Windows NLWeb AutoRAG
.DESCRIPTION
    This script tests the NLWeb AutoRAG system, including environment setup,
    package installations, and API endpoints.
    
    Features:
    - Comprehensive environment validation
    - Service health checks
    - API endpoint testing
    - Colored console output
    - Detailed test reporting
.PARAMETER BackendPort
    Port number for the backend server (default: 8000)
.PARAMETER FrontendPort
    Port number for the frontend server (default: 3000)
.PARAMETER TestTimeout
    Timeout in seconds for API tests (default: 30)
.PARAMETER SkipFrontend
    Skip frontend-related tests
.PARAMETER SkipBackend
    Skip backend-related tests
.EXAMPLE
    .\test_system.ps1
    .\test_system.ps1 -BackendPort 8080 -TestTimeout 60
#>

[CmdletBinding()]
param (
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000,
    [int]$TestTimeout = 30,
    [switch]$SkipFrontend,
    [switch]$SkipBackend
)

# Set error action preference
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Global variables
$script:projectRoot = $PSScriptRoot
$script:backendProcess = $null
$script:frontendProcess = $null
$script:testResults = @{
    Total = 0
    Passed = 0
    Failed = 0
    Skipped = 0
    StartTime = Get-Date
    EndTime = $null
}

# ANSI color codes for cross-platform colored output
$script:colors = @{
    Reset = "`e[0m"
    Red = "`e[91m"
    Green = "`e[92m"
    Yellow = "`e[93m"
    Blue = "`e[94m"
    Cyan = "`e[96m"
    White = "`e[97m"
    BgRed = "`e[41m"
    BgGreen = "`e[42m"
    BgYellow = "`e[43m"
}

function Write-TestLog {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [ValidateSet("Info", "Success", "Warning", "Error", "Debug")]
        [string]$Level = "Info",
        
        [switch]$NoNewline,
        [switch]$NoTimestamp,
        [int]$Indent = 0
    )
    
    $indentStr = '  ' * $Indent
    $timestamp = if (-not $NoTimestamp) { "[$(Get-Date -Format 'HH:mm:ss')]" } else { ' ' * 12 }
    
    $symbol = switch ($Level) {
        "Success" { "$($script:colors.Green)✓" }
        "Error"   { "$($script:colors.Red)✗" }
        "Warning" { "$($script:colors.Yellow)!" }
        "Debug"   { "$($script:colors.Blue)⚙" }
        default   { "$($script:colors.Cyan)•" }
    }
    
    # Color is used in the messageToWrite construction
    
    $messageToWrite = "$timestamp $symbol $indentStr$Message$($script:colors.Reset)"
    
    if ($NoNewline) {
        Write-Host -NoNewline $messageToWrite
    } else {
        Write-Host $messageToWrite
    }
    
    # Log to file as well
    $logMessage = "$($timestamp.Trim()) [$Level] $indentStr$Message"
    $logMessage | Out-File -Append -FilePath "$($script:projectRoot)/test_results.log" -Encoding utf8
}

function Test-CommandExists {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        
        [string]$MinVersion,
        [string]$HelpUrl,
        [switch]$Required
    )
    
    try {
        $null = Get-Command $Command -ErrorAction Stop
        $version = $null
        
        # Try to get version info
        try {
            if ($Command -eq 'python' -or $Command -eq 'python3') {
                $version = (python --version 2>&1 | Select-String -Pattern 'Python (\d+\.\d+\.\d+)').Matches.Groups[1].Value
            } elseif ($Command -eq 'node') {
                $version = (node --version) -replace '^v', ''
            } elseif ($Command -eq 'npm') {
                $version = npm --version
            } elseif ($Command -eq 'git') {
                $version = (git --version) -replace '^git version ', ''
            }
        } catch {
            Write-TestLog "Warning: Could not determine version for $Command" -Level Warning
        }
        
        # Check minimum version if specified
        if ($version -and $MinVersion) {
            $versionObj = [version]$version
            $minVersionObj = [version]$MinVersion
            
            if ($versionObj -lt $minVersionObj) {
                if ($Required) {
                    throw "$Command version $MinVersion or higher is required. Found version $version"
                }
                Write-TestLog "$Command version $version is below recommended version $MinVersion" -Level Warning
                if ($HelpUrl) {
                    Write-TestLog "  Update from: $HelpUrl" -Level Info -Indent 1
                }
                return $false
            }
        }
        
        return $true
    } catch {
        if ($Required) {
            $errorMsg = "Command '$Command' is required but not found in PATH"
            if ($HelpUrl) {
                $errorMsg += ". Download from: $HelpUrl"
            }
            throw $errorMsg
        }
        return $false
    }
}

function Test-Environment {
    [CmdletBinding()]
    param()
    
    $script:testResults.Total++
    
    try {
        Write-TestLog "Testing system environment..." -Level Info -Indent 1
        
        # Check required commands
        $requiredCommands = @(
            @{ Name = 'python'; MinVersion = '3.8.0'; HelpUrl = 'https://www.python.org/downloads/' },
            @{ Name = 'pip'; HelpUrl = 'https://pip.pypa.io/en/stable/installation/' },
            @{ Name = 'node'; MinVersion = '16.0.0'; HelpUrl = 'https://nodejs.org/' },
            @{ Name = 'npm'; HelpUrl = 'https://www.npmjs.com/get-npm' },
            @{ Name = 'git'; HelpUrl = 'https://git-scm.com/download/win' }
        )
        
        foreach ($cmd in $requiredCommands) {
            $result = Test-CommandExists @cmd -Required
            if ($result) {
                $version = if ($cmd.Name -eq 'python') { 
                    (python --version 2>&1) -replace 'Python ', '' 
                } elseif ($cmd.Name -eq 'node') { 
                    (node --version) -replace 'v', '' 
                } else { 
                    & $cmd.Name --version 
                }
                Write-TestLog "✓ $($cmd.Name) v$version" -Level Success -Indent 2
            }
        }
        
        # Check Python environment
        Write-TestLog "Checking Python packages..." -Level Info -Indent 1
        $requiredPackages = @(
            @{ Name = 'pydantic'; MinVersion = '1.10.0' },
            @{ Name = 'fastapi'; MinVersion = '0.95.0' },
            @{ Name = 'uvicorn'; MinVersion = '0.21.0' },
            @{ Name = 'sentence_transformers'; MinVersion = '2.2.0' },
            @{ Name = 'faiss-cpu'; MinVersion = '1.7.0' },
            @{ Name = 'rank_bm25'; MinVersion = '0.2.2' },
            @{ Name = 'pytest'; MinVersion = '7.0.0' }
        )
        
        $installedPackages = pip list --format=json | ConvertFrom-Json -AsHashtable
        $missingOrOutdated = @()
        
        foreach ($pkg in $requiredPackages) {
            $installed = $installedPackages | Where-Object { $_.name -eq $pkg.Name }
            
            if (-not $installed) {
                Write-TestLog "✗ $($pkg.Name): Not installed" -Level Error -Indent 2
                $missingOrOutdated += $pkg.Name
            } else {
                $versionOk = $true
                if ($pkg.MinVersion) {
                    $installedVersion = [version]$installed.version
                    $requiredVersion = [version]$pkg.MinVersion
                    $versionOk = $installedVersion -ge $requiredVersion
                }
                
                if ($versionOk) {
                    Write-TestLog "✓ $($pkg.Name) v$($installed.version)" -Level Success -Indent 2
                } else {
                    Write-TestLog "! $($pkg.Name) v$($installed.version) (update to v$($pkg.MinVersion) or higher)" -Level Warning -Indent 2
                    $missingOrOutdated += $pkg.Name
                }
            }
        }
        
        if ($missingOrOutdated.Count -gt 0) {
            Write-TestLog "Installing/updating Python packages..." -Level Info -Indent 1
            foreach ($pkg in $missingOrOutdated) {
                $pkgInfo = $requiredPackages | Where-Object { $_.Name -eq $pkg }
                $versionSpec = if ($pkgInfo.MinVersion) { ">=$($pkgInfo.MinVersion)" } else { "" }
                
                Write-TestLog "Installing $pkg $versionSpec..." -Level Info -Indent 2
                $installCmd = "pip install --upgrade $pkg$versionSpec"
                Invoke-Expression $installCmd
                
                if ($LASTEXITCODE -ne 0) {
                    throw "Failed to install/update $pkg"
                }
            }
        }
        
        # Check Node.js environment
        if (-not $SkipFrontend) {
            Write-TestLog "Checking Node.js environment..." -Level Info -Indent 1
            
            $nodeVersion = (node --version) -replace 'v', ''
            $npmVersion = npm --version
            
            Write-TestLog "Node.js v$nodeVersion, npm v$npmVersion" -Level Success -Indent 2
            
            # Check frontend dependencies
            $frontendPath = Join-Path $script:projectRoot "frontend"
            if (Test-Path $frontendPath) {
                Push-Location $frontendPath
                
                if (-not (Test-Path "node_modules")) {
                    Write-TestLog "Installing frontend dependencies..." -Level Info -Indent 2
                    npm install
                    if ($LASTEXITCODE -ne 0) {
                        throw "Failed to install frontend dependencies"
                    }
                }
                
                Pop-Location
            }
        }
        
        $script:testResults.Passed++
        Write-TestLog "Environment validation completed successfully" -Level Success -Indent 1
        return $true
        
    } catch {
        $script:testResults.Failed++
        Write-TestLog "Environment validation failed: $_" -Level Error -Indent 1
        Write-TestLog $_.ScriptStackTrace -Level Debug -Indent 2
        return $false
    }
}

function Test-BackendService {
    [CmdletBinding()]
    param(
        [int]$Port = 8000,
        [int]$TimeoutSeconds = 30
    )
    
    $script:testResults.Total++
    
    try {
        Write-TestLog "Testing backend service on port $Port..." -Level Info -Indent 1
        
        $backendPath = Join-Path $script:projectRoot "backend"
        if (-not (Test-Path $backendPath)) {
            throw "Backend directory not found at $backendPath"
        }
        
        # Run tests
        try {
            Push-Location $backendPath
            
            # Check for test files
            $testFiles = Get-ChildItem -Path $backendPath -Filter "test_*.py" -File
            if (-not $testFiles) {
                Write-TestLog "No test files found in backend directory" -Level Warning
                return $true
            }
            
            Write-TestLog "Running backend tests..."
            $testOutput = & python -m pytest test_*.py -v 2>&1 | Out-String
            
            if ($LASTEXITCODE -ne 0) {
                Write-TestLog "Backend tests failed:" -Level Error
                Write-Host $testOutput -ForegroundColor Red
                return $false
            }
            
            Write-TestLog "Backend tests passed" -Level Success
            
            # Start backend server if not already running
            $serviceUrl = "http://localhost:$Port"
            $healthCheckUrl = "$serviceUrl/health"
            
            $isRunning = $false
            try {
                $response = Invoke-WebRequest -Uri $healthCheckUrl -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    $isRunning = $true
                    Write-TestLog "Backend service is already running" -Level Success -Indent 2
                }
            } catch {
                # Service is not running, we'll start it
            }
            
            if (-not $isRunning) {
                Write-TestLog "Starting backend server..." -Level Info -Indent 2
                
                # Activate virtual environment
                $venvPath = Join-Path $backendPath "venv"
                if (-not (Test-Path $venvPath)) {
                    throw "Virtual environment not found at $venvPath. Please run setup.ps1 first."
                }
                
                $activatePath = Join-Path $venvPath "Scripts\Activate.ps1"
                if (-not (Test-Path $activatePath)) {
                    throw "Could not find virtual environment activation script at $activatePath"
                }
                
                # Start the backend process
                $script:backendProcess = Start-Process -NoNewWindow -PassThru -FilePath "python" -WorkingDirectory $backendPath -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port $Port"
                
                # Wait for server to start
                $startTime = Get-Date
                $serverReady = $false
                
                Write-TestLog -Message "Waiting for backend to start..." -NoNewline -Indent 2
                
                while (((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
                    try {
                        $response = Invoke-WebRequest -Uri $healthCheckUrl -Method Get -TimeoutSec 1 -ErrorAction SilentlyContinue
                        if ($response.StatusCode -eq 200) {
                            $serverReady = $true
                            break
                        }
                    } catch {
                        # Ignore errors while waiting for server to start
                    }
                    
                    Write-Host "." -NoNewline -ForegroundColor $script:colors.Cyan
                    Start-Sleep -Milliseconds 500
                }
                
                Write-Host ""  # New line after progress dots
                
                if (-not $serverReady) {
                    throw "Backend service did not start within $TimeoutSeconds seconds"
                }
                
                Write-TestLog "Backend service started successfully" -Level Success -Indent 2
            }
            
            # Test API endpoints
            $endpointsToTest = @(
                @{ Path = "/"; Method = "GET"; ExpectedStatus = 200; Description = "Root endpoint" },
                @{ Path = "/docs"; Method = "GET"; ExpectedStatus = 200; Description = "API documentation" },
                @{ Path = "/health"; Method = "GET"; ExpectedStatus = 200; Description = "Health check" },
                @{ Path = "/documents/"; Method = "GET"; ExpectedStatus = 200; Description = "List documents" }
            )
            
            Write-TestLog "Testing API endpoints..." -Level Info -Indent 2
            $allEndpointsOk = $true
            
            foreach ($endpoint in $endpointsToTest) {
                $url = "$serviceUrl$($endpoint.Path)"
                Write-TestLog -Message "$($endpoint.Description) ($($endpoint.Method) $($endpoint.Path))..." -NoNewline -Indent 3
                
                try {
                    $response = Invoke-WebRequest -Uri $url -Method $endpoint.Method -TimeoutSec 5 -ErrorAction Stop
                    
                    if ($response.StatusCode -eq $endpoint.ExpectedStatus) {
                        Write-TestLog " ✓ (Status: $($response.StatusCode))" -Level Success -NoNewline -NoTimestamp
                    } else {
                        Write-TestLog " ✗ Expected $($endpoint.ExpectedStatus) but got $($response.StatusCode)" -Level Error -NoNewline -NoTimestamp
                        $allEndpointsOk = $false
                    }
                } catch [System.Net.WebException] {
                    $statusCode = [int][System.Net.HttpStatusCode]::ServiceUnavailable
                    if ($_.Exception.Response) {
                        $statusCode = [int]$_.Exception.Response.StatusCode
                    }
                    Write-TestLog " ✗ Failed with status $statusCode" -Level Error -NoNewline -NoTimestamp
                    $allEndpointsOk = $false
                } catch {
                    Write-TestLog " ✗ $($_.Exception.Message)" -Level Error -NoNewline -NoTimestamp
                    $allEndpointsOk = $false
                }
                
                Write-Host ""  # New line after status
            }
            
            if ($allEndpointsOk) {
                $script:testResults.Passed++
                Write-TestLog "All backend endpoints are working correctly" -Level Success -Indent 2
                return $true
            } else {
                throw "Some backend endpoints are not responding as expected"
            }
            
        } catch {
            throw "Backend test failed: $_"
        } finally {
            Pop-Location
        }
    } catch {
        $script:testResults.Failed++
        Write-TestLog "Backend test failed: $_" -Level Error -Indent 1
        Write-TestLog $_.ScriptStackTrace -Level Debug -Indent 2
        return $false
    }
}

function Stop-BackendServer {
    if ($script:backendProcess -and -not $script:backendProcess.HasExited) {
        Write-TestLog "Stopping backend server..."
        try {
            Stop-Process -Id $script:backendProcess.Id -Force -ErrorAction SilentlyContinue
            Wait-Process -Id $script:backendProcess.Id -Timeout 5 -ErrorAction SilentlyContinue
        } catch {
            Write-TestLog "Warning: Failed to stop backend process: $_" -Level Warning
        }
        $script:backendProcess = $null
    }
}

# Main script execution
function Show-TestSummary {
    [CmdletBinding()]
    param()
    
    $script:testResults.EndTime = Get-Date
    $duration = $script:testResults.EndTime - $script:testResults.StartTime
    $durationStr = "{0:hh\:mm\:ss\.fff}" -f [timespan]::fromseconds($duration.TotalSeconds)
    
    Write-Host "`n$($script:colors.White)$($script:colors.BgBlue) TEST SUMMARY $($script:colors.Reset)"
    Write-Host "$($script:colors.White)Duration: $($script:colors.Reset)$durationStr"
    Write-Host "$($script:colors.White)Total:    $($script:colors.Reset)$($script:testResults.Total) tests"
    
    if ($script:testResults.Passed -gt 0) {
        Write-Host "$($script:colors.White)Passed:   $($script:colors.Green)✓ $($script:testResults.Passed)$($script:colors.Reset)"
    }
    
    if ($script:testResults.Failed -gt 0) {
        Write-Host "$($script:colors.White)Failed:   $($script:colors.Red)✗ $($script:testResults.Failed)$($script:colors.Reset)"
    }
    
    if ($script:testResults.Skipped -gt 0) {
        Write-Host "$($script:colors.White)Skipped:  $($script:colors.Yellow)⚠ $($script:testResults.Skipped)$($script:colors.Reset)"
    }
    
    Write-Host ""
    
    # Exit with appropriate code
    if ($script:testResults.Failed -gt 0) {
        exit 1
    }
    
    exit 0
}

# Main execution
try {
    # Clear previous log file
    if (Test-Path "$($script:projectRoot)/test_results.log") {
        Remove-Item "$($script:projectRoot)/test_results.log" -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "$($script:colors.White)$($script:colors.BgBlue) NLWeb AutoRAG Test Runner $($script:colors.Reset)"
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
    
    # Check if running as administrator (only required for some tests)
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($isAdmin) {
        Write-TestLog "Running with administrator privileges" -Level Info
    } else {
        Write-TestLog "Running without administrator privileges (some tests may be skipped)" -Level Warning
    }
    
    # Run environment validation
    if (-not (Test-Environment)) {
        throw "Environment validation failed"
    }
    
    # Run backend tests if not skipped
    if (-not $SkipBackend) {
        if (-not (Test-BackendService -Port $BackendPort -TimeoutSeconds $TestTimeout)) {
            throw "Backend tests failed"
        }
    } else {
        $script:testResults.Skipped++
        Write-TestLog "Skipping backend tests as requested" -Level Warning
    }
    
    # Test frontend if not skipped
    if (-not $SkipFrontend) {
        Write-Host "`nTesting frontend..." -ForegroundColor Cyan
        $frontendPath = Join-Path $script:projectRoot "frontend"
        if (-not (Test-Path $frontendPath)) {
            Write-TestLog "Frontend directory not found at $frontendPath" -Level Warning
        } else {
            Push-Location $frontendPath
            
            # Install frontend dependencies if needed
            if (-not (Test-Path "node_modules")) {
                Write-TestLog "Installing frontend dependencies..." -Level Info
                $npmInstall = Start-Process -NoNewWindow -PassThru -FilePath "npm" -ArgumentList "install" -Wait
                if ($npmInstall.ExitCode -ne 0) {
                    throw "Failed to install frontend dependencies"
                }
            }
            
            # Run frontend tests
            Write-TestLog "Running frontend tests..." -Level Info
            $testProcess = Start-Process -NoNewWindow -PassThru -FilePath "npm" -ArgumentList "test -- --watchAll=false" -Wait -PassThru
            
            if ($testProcess.ExitCode -ne 0) {
                throw "Frontend tests failed"
            }
            
            Pop-Location
            Write-TestLog "Frontend tests passed" -Level Success
        }
    } else {
        $script:testResults.Skipped++
        Write-TestLog "Skipping frontend tests as requested" -Level Warning
    }
    
    # Show test summary
    Show-TestSummary
    
} catch {
    Write-TestLog "FATAL ERROR: $_" -Level Error
    Write-TestLog $_.ScriptStackTrace -Level Error
    exit 1
} finally {
    # Cleanup
    Stop-BackendServer
}
