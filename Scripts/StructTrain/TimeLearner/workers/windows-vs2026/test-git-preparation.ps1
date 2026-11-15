param([Parameter(Mandatory=$true)][string]$OutputDirectory,
      [Parameter(Mandatory=$true)][string]$SdkRoot,
      [Parameter(Mandatory=$true)][string]$SdkCommit,
      [Parameter(Mandatory=$true)][string]$SdkNamespaceBlob,
      [ValidateRange(1,10000000)][int]$ExpectedSdkFiles=4052)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Import-Module (Join-Path $PSScriptRoot 'GitPreparation.psm1') -Force
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Fresh test output required' }
$output = [IO.Path]::GetFullPath($OutputDirectory)
if (-not $output.StartsWith('C:\Projects\TimeLearnerWorker\jobs\',[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Test output must be in the private worker jobs directory'
}
$null = New-Item -ItemType Directory -Path $output
$script:cases = @()
function Check([string]$Name,[scriptblock]$Action) {
    & $Action
    $script:cases += [pscustomobject]@{name=$Name;passed=$true}
}
function Reject([scriptblock]$Action,[string]$Reason) {
    $rejected = $false
    try { & $Action | Out-Null } catch {
        if ($_.ToString() -notmatch $Reason) { throw }
        $rejected = $true
    }
    if (-not $rejected) { throw ('Expected rejection: '+$Reason) }
}
$utf8 = [Text.UTF8Encoding]::new($false)
function Write-Blob([string]$Repository,[string]$Name,[object]$Value) {
    $file = Join-Path $output $Name
    [IO.File]::WriteAllText($file,($Value|ConvertTo-Json -Depth 8 -Compress)+"`n",$utf8)
    return (Invoke-CheckedGit @('-C',$Repository,'hash-object','-w',$file)) -join ''
}
$donor = Join-Path $output 'donor'
$receiver = Join-Path $output 'receiver'
try {
    Check 'ZeroNativeExitAccepted' { Assert-NativeExitCode 0 'controlled zero' }
    Check 'ActualNegativeCmdExitRejected' {
        & $env:ComSpec /d /c 'exit /b -1'
        $negative = $LASTEXITCODE
        if ($negative -eq 0) { throw 'Actual cmd did not produce nonzero exit' }
        Reject { Assert-NativeExitCode $negative 'controlled negative' } 'native exit code'
    }
    Check 'PositiveAndUnsignedExitRejected' {
        foreach ($code in @(1,4294967295)) { Reject { Assert-NativeExitCode $code 'controlled nonzero' } 'native exit code' }
    }
    Check 'MissingGitRepositoryRejected' {
        Reject { Invoke-CheckedGit @('-C',(Join-Path $output 'missing'),'status') } 'native exit code'
    }
    Check 'PersonalProjectRefusedBeforeGitWrite' {
        Reject { Complete-PreparedGitClone 'C:/Projects/Nmsdk' ('0'*40) } 'private TimeLearnerWorker workspace'
    }
    $null = Invoke-CheckedGit @('init','--quiet',$donor)
    $null = Invoke-CheckedGit @('-C',$donor,'config','user.name','TimeLearner metadata fixture')
    $null = Invoke-CheckedGit @('-C',$donor,'config','user.email','metadata-fixture@example.invalid')
    $null = Invoke-CheckedGit @('-C',$donor,'config','core.autocrlf','false')
    [IO.File]::WriteAllText((Join-Path $donor 'fixture.txt'),"metadata fixture`n",$utf8)
    $null = Invoke-CheckedGit @('-C',$donor,'add','fixture.txt')
    $null = Invoke-CheckedGit @('-C',$donor,'commit','-m','controlled metadata fixture')
    $commit = (Invoke-CheckedGit @('-C',$donor,'rev-parse','HEAD')) -join ''
    $bundle = Join-Path $output 'fixture.bundle'
    $null = Invoke-CheckedGit @('-C',$donor,'bundle','create',$bundle,'HEAD')
    $null = Invoke-CheckedGit @('init','--quiet',$receiver)
    $null = Invoke-CheckedGit @('-C',$receiver,'fetch','--no-tags',$bundle,$commit)
    $patterns = @('!/*','/fixture.txt') + @(1..320 | ForEach-Object { '/absent-pattern-'+$_ })
    $spec = Write-Blob $receiver 'clone-spec.json' @{destination=$receiver;commit=$commit;patterns=$patterns}
    Check 'FreshCloneWith322SparsePatterns' {
        $result = Complete-PreparedGitClone $receiver $spec
        if ($result.head -ne $commit -or -not [IO.File]::Exists((Join-Path $receiver 'fixture.txt'))) {
            throw 'Fresh fixture clone not materialized'
        }
    }
    Check 'CompletedCloneRefusedWithoutResettingIt' {
        Reject { Complete-PreparedGitClone $receiver $spec } 'not fresh/unborn'
        if (((Invoke-CheckedGit @('-C',$receiver,'rev-parse','HEAD')) -join '') -ne $commit) { throw 'Refused clone changed' }
    }
    $file = Join-Path $receiver 'fixture.txt'
    $record = @{bytes=([IO.FileInfo]$file).Length;sha256=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()}
    $namespace = Write-Blob $receiver 'namespace.json' @{'fixture.txt'=$record}
    Check 'Utf8GitJsonSurvivesOemConsoleAndRestoresCallerEncoding' {
        $unicode = -join ([char[]]@(0x0442,0x0435,0x0441,0x0442))
        $blob = Write-Blob $receiver 'unicode.json' @{name=$unicode;path=('Catalog/'+$unicode+'.json')}
        $previousEncoding = [Console]::OutputEncoding
        try {
            [Console]::OutputEncoding = [Text.Encoding]::GetEncoding(866)
            $raw = (Invoke-CheckedGit @('-C',$receiver,'cat-file','blob',$blob)) -join "`n"
            $value = ConvertFrom-Json -InputObject $raw
            if ($value.name -cne $unicode -or $value.path -cne ('Catalog/'+$unicode+'.json')) {
                throw 'Git UTF-8 JSON changed in an OEM console'
            }
            if ([Console]::OutputEncoding.CodePage -ne 866) { throw 'Caller console encoding was not restored' }
        } finally { [Console]::OutputEncoding = $previousEncoding }
    }
    Check 'FixtureExactNamespaceAccepted' {
        $result = Test-PreparedSdk $receiver $commit $namespace 1 1
        if ($result.verified_files -ne 1) { throw 'Fixture namespace count differs' }
    }
    Check 'ExtraIgnoredFileCannotPassTrackedCleanCheck' {
        $extra = Join-Path $receiver '.untracked-extra'
        [IO.File]::WriteAllText($extra,'untracked extra',$utf8)
        try { Reject { Test-PreparedSdk $receiver $commit $namespace 1 1 } 'Physical source namespace differs' }
        finally { Remove-Item -LiteralPath $extra }
    }
    Check 'WrongDeclaredSizeRejectedBeforeHashing' {
        $badRecord = @{bytes=$record.bytes+1;sha256=$record.sha256}
        $bad = Write-Blob $receiver 'bad-namespace.json' @{'fixture.txt'=$badRecord}
        Reject { Test-PreparedSdk $receiver $commit $bad 1 1 } 'Source file type/size differs'
    }
    Check 'ActualDeclaredSdkAndEightRepositories' {
        $result = Test-PreparedSdk $SdkRoot $SdkCommit $SdkNamespaceBlob $ExpectedSdkFiles 8
        [IO.File]::WriteAllText((Join-Path $output 'actual-sdk.json'),($result|ConvertTo-Json -Depth 5)+"`n",$utf8)
    }
    $receipt = [pscustomobject]@{kind='windows_git_preparation_tests';executed=$script:cases.Count;
        cases=$script:cases;status='passed';native_models_or_cpp_tests=$false;scientific_verdict=$null}
    [IO.File]::WriteAllText((Join-Path $output 'result.json'),($receipt|ConvertTo-Json -Depth 5)+"`n",$utf8)
    $receipt | ConvertTo-Json -Depth 5
} catch {
    $receipt = [pscustomobject]@{kind='windows_git_preparation_tests';executed=$script:cases.Count;
        cases=$script:cases;status='failed';reason=$_.ToString();native_models_or_cpp_tests=$false;scientific_verdict=$null}
    [IO.File]::WriteAllText((Join-Path $output 'result.json'),($receipt|ConvertTo-Json -Depth 5)+"`n",$utf8)
    throw
}
