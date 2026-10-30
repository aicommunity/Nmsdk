# PowerShell скрипт для запуска теста QMessageBox в Windows
# Использование: .\run_qmessagebox_test.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QMessageBox Test Runner for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверяем наличие Qt
$qtFound = $false
$qtPath = $null

if ($env:QTDIR) {
    $qtPath = $env:QTDIR
    $qtFound = Test-Path "$qtPath\include\QtWidgets\QMessageBox"
    if ($qtFound) {
        Write-Host "Found QTDIR: $qtPath" -ForegroundColor Green
    }
}

if (-not $qtFound) {
    Write-Host "QTDIR not set or invalid, trying default locations..." -ForegroundColor Yellow
    
    $possiblePaths = @(
        "C:\Qt\5.15.2\msvc2019_64",
        "C:\Qt\5.15.2\msvc2022_64",
        "C:\Qt\6.5.0\msvc2019_64",
        "C:\Qt\6.5.0\msvc2022_64",
        "C:\Qt\6.6.0\msvc2019_64",
        "C:\Qt\6.6.0\msvc2022_64"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path "$path\include\QtWidgets\QMessageBox") {
            $qtPath = $path
            $qtFound = $true
            Write-Host "Found Qt at: $qtPath" -ForegroundColor Green
            break
        }
    }
}

if (-not $qtFound) {
    Write-Host "ERROR: Qt not found!" -ForegroundColor Red
    Write-Host "Please install Qt5 or Qt6 and set QTDIR environment variable" -ForegroundColor Red
    Write-Host "Or place Qt in one of the standard locations:" -ForegroundColor Yellow
    foreach ($path in $possiblePaths) {
        Write-Host "  - $path" -ForegroundColor Yellow
    }
    Read-Host "Press Enter to exit"
    exit 1
}

# Проверяем наличие исходного файла
$testFile = "Test_QMessageBox_Standalone.cpp"
if (-not (Test-Path $testFile)) {
    Write-Host "ERROR: Test file not found: $testFile" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Compiling test..." -ForegroundColor Cyan
Write-Host ""

# Определяем компилятор
$compiler = $null
$useMsvc = $false

# Проверяем MSVC
$msvcPath = & where.exe cl 2>$null
if ($LASTEXITCODE -eq 0) {
    $compiler = "MSVC"
    $useMsvc = $true
    Write-Host "Using MSVC compiler: $msvcPath" -ForegroundColor Green
} else {
    # Проверяем MinGW/GCC
    $gccPath = & where.exe g++ 2>$null
    if ($LASTEXITCODE -eq 0) {
        $compiler = "GCC"
        Write-Host "Using GCC compiler: $gccPath" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No compiler found!" -ForegroundColor Red
        Write-Host "Please install Visual Studio (MSVC) or MinGW" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Компилируем
$exeName = "Test_QMessageBox_Standalone.exe"
$qtInclude = "$qtPath\include"
$qtLib = "$qtPath\lib"

if ($useMsvc) {
    Write-Host "Compiling with MSVC..." -ForegroundColor Yellow
    & cl /EHsc /MD "$testFile" /I"$qtInclude" /link /LIBPATH:"$qtLib" Qt5Core.lib Qt5Widgets.lib /SUBSYSTEM:WINDOWS /OUT:"$exeName" 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Compilation failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Compiling with GCC..." -ForegroundColor Yellow
    & g++ -o "$exeName" "$testFile" -I"$qtInclude" -L"$qtLib" -lQt5Core -lQt5Widgets -fPIC -mwindows 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Compilation failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Compilation successful!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Running test..." -ForegroundColor Cyan
Write-Host ""

# Запускаем тест
if (Test-Path $exeName) {
    & ".\$exeName"
    Write-Host ""
    Write-Host "Test completed." -ForegroundColor Green
} else {
    Write-Host "ERROR: Executable not found: $exeName" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
