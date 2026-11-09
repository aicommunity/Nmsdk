Set-StrictMode -Version Latest

function Assert-NativeExitCode {
    param([Parameter(Mandatory=$true)][long]$Code, [Parameter(Mandatory=$true)][string]$Operation)
    # Windows native programs can report negative signed exit codes.
    if ($Code -ne 0) { throw "$Operation failed with native exit code $Code" }
}

function Invoke-CheckedGit {
    param([Parameter(Mandatory=$true)][string[]]$ArgumentList)
    $gitCommand = Get-Command git.exe -CommandType Application -ErrorAction Stop
    $previous = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $lines = @(& $gitCommand.Source @ArgumentList 2>&1)
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $previous }
    foreach ($entry in $lines) {
        # Windows PowerShell 5.1 wraps the first stderr line and subsequent
        # stderr lines with different IDs, even when Git exits successfully.
        if ($entry -is [System.Management.Automation.ErrorRecord] -and
            $entry.FullyQualifiedErrorId -notin @('NativeCommandError','NativeCommandErrorMessage')) { throw $entry }
    }
    if ($null -eq $code) { throw 'Git did not supply a native exit code' }
    Assert-NativeExitCode $code ('git '+($ArgumentList -join ' '))
    return @($lines | ForEach-Object { $_.ToString() })
}

function Get-PrivateSdkPath {
    param([string]$Path)
    $workspace = [IO.Path]::GetFullPath('C:/Projects/TimeLearnerWorker').TrimEnd('\','/')
    $actual = [IO.Path]::GetFullPath($Path).TrimEnd('\','/')
    if (-not $actual.StartsWith($workspace+'\',[StringComparison]::OrdinalIgnoreCase)) {
        throw 'SDK path must be inside the private TimeLearnerWorker workspace'
    }
    $cursor = $actual
    while ($cursor.Length -ge $workspace.Length) {
        if ([IO.Directory]::Exists($cursor) -and
            (([IO.File]::GetAttributes($cursor) -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw 'SDK path contains a reparse directory'
        }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    return $actual
}

function Complete-PreparedGitClone {
    param([string]$Repository, [ValidatePattern('^[0-9a-f]{40}$')][string]$SpecificationBlob)
    $repositoryPath = Get-PrivateSdkPath $Repository
    $raw = (Invoke-CheckedGit @('-C',$repositoryPath,'cat-file','blob',$SpecificationBlob)) -join "`n"
    $spec = ConvertFrom-Json -InputObject $raw
    if ((Get-PrivateSdkPath $spec.destination) -ne $repositoryPath -or
        $spec.commit -notmatch '^[0-9a-f]{40}$') { throw 'Clone specification differs from destination' }
    foreach ($pattern in $spec.patterns) {
        if ($pattern -isnot [string] -or $pattern -match '[\r\n\x00]' -or
            $pattern -notmatch '^!?/' -or ($pattern -split '/') -contains '..') {
            throw 'Invalid sparse pattern'
        }
    }
    $gitDirectory = Join-Path $repositoryPath '.git'
    $head = [IO.File]::ReadAllText((Join-Path $gitDirectory 'HEAD')).Trim()
    $headMatch = [regex]::Match($head,'^ref: (refs/heads/[A-Za-z0-9_.-]+)$')
    if (-not $headMatch.Success) { throw 'Clone is not fresh/unborn' }
    if ([IO.File]::Exists((Join-Path $gitDirectory $headMatch.Groups[1].Value)) -or
        [IO.File]::Exists((Join-Path $gitDirectory 'packed-refs')) -or
        [IO.File]::Exists((Join-Path $gitDirectory 'index.lock'))) { throw 'Clone already has history or active index write' }
    if (@(Get-ChildItem -Force -LiteralPath $repositoryPath | Where-Object Name -ne '.git').Count) {
        throw 'Fresh clone contains non-Git files'
    }
    $utf8 = [Text.UTF8Encoding]::new($false)
    [IO.File]::WriteAllText((Join-Path $gitDirectory 'shallow'),$spec.commit+"`n",$utf8)
    foreach ($setting in @(@('core.repositoryformatversion','1'),@('extensions.partialClone','origin'),
        @('remote.origin.promisor','true'),@('core.autocrlf','false'),@('core.eol','lf'),@('core.longpaths','true'))) {
        $null = Invoke-CheckedGit @('-C',$repositoryPath,'config',$setting[0],$setting[1])
    }
    $null = Invoke-CheckedGit @('-C',$repositoryPath,'sparse-checkout','init','--no-cone')
    [IO.File]::WriteAllText((Join-Path $gitDirectory 'info/sparse-checkout'),
        ([string[]]$spec.patterns -join "`n")+"`n",$utf8)
    $null = Invoke-CheckedGit @('-C',$repositoryPath,'-c','submodule.recurse=false','checkout','--detach',$spec.commit)
    $actual = (Invoke-CheckedGit @('-C',$repositoryPath,'rev-parse','HEAD')) -join ''
    if ($actual -ne $spec.commit) { throw 'Delivered HEAD differs from specification' }
    return [pscustomobject]@{repository=$repositoryPath;head=$actual;scientific_verdict=$null}
}

function Test-PreparedSdk {
    param([string]$SourceRoot, [ValidatePattern('^[0-9a-f]{40}$')][string]$RootCommit,
          [ValidatePattern('^[0-9a-f]{40}$')][string]$NamespaceBlob,
          [ValidateRange(1,10000000)][int]$ExpectedFiles,
          [ValidateRange(1,128)][int]$ExpectedRepositories)
    $root = Get-PrivateSdkPath $SourceRoot
    $head = (Invoke-CheckedGit @('-C',$root,'rev-parse','HEAD')) -join ''
    if ($head -ne $RootCommit) { throw 'Root HEAD differs' }
    $specs = @(@{role='root';path=$root;commit=$head})
    foreach ($line in (Invoke-CheckedGit @('-C',$root,'ls-tree','-r','HEAD'))) {
        if ($line -match '^160000 commit ([0-9a-f]{40})\t(.+)$') {
            $specs += @{role=$Matches[2];path=(Join-Path $root $Matches[2]);commit=$Matches[1]}
        }
    }
    if ($specs.Count -ne $ExpectedRepositories) { throw 'Repository count differs' }
    $closure = @()
    foreach ($r in $specs) {
        $actual = (Invoke-CheckedGit @('-C',$r.path,'rev-parse','HEAD')) -join ''
        if ($actual -ne $r.commit -or
            @(Invoke-CheckedGit @('-C',$r.path,'status','--porcelain','--untracked-files=no')).Count -ne 0) {
            throw ('Source closure differs: '+$r.role)
        }
        if ([IO.File]::Exists((Join-Path $r.path '.git/objects/info/alternates'))) { throw 'Source uses alternates' }
        $closure += [pscustomobject]@{role=$r.role;head=$actual;tracked_clean=$true;alternates=$false}
    }
    $raw = (Invoke-CheckedGit @('-C',$root,'cat-file','blob',$NamespaceBlob)) -join "`n"
    $namespace = ConvertFrom-Json -InputObject $raw
    $sha = [Security.Cryptography.SHA256]::Create()
    $verified = 0
    try {
        foreach ($property in $namespace.PSObject.Properties) {
            $relative = $property.Name
            if ($relative.StartsWith('/') -or $relative.Contains('\') -or
                @($relative -split '/' | Where-Object { $_ -in @('.','..','.git','') }).Count) {
                throw 'Invalid relative namespace path'
            }
            $record = $property.Value
            if (($record.bytes -isnot [int] -and $record.bytes -isnot [long] -and $record.bytes -isnot [double]) -or
                $record.bytes -lt 0 -or
                [long]$record.bytes -ne $record.bytes -or $record.bytes -gt 64MB -or
                $record.sha256 -notmatch '^[0-9a-f]{64}$') { throw 'Invalid namespace file record' }
            $file = Join-Path $root $relative
            $info = Get-Item -Force -LiteralPath $file
            if (($info.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $info.Length -ne $record.bytes) {
                throw ('Source file type/size differs: '+$relative)
            }
            $stream = [IO.File]::OpenRead($file)
            try { $digest = ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
            finally { $stream.Dispose() }
            if ($digest -ne $record.sha256) { throw ('Source bytes differ: '+$relative) }
            $verified++
        }
    } finally { $sha.Dispose() }
    $stack = New-Object 'System.Collections.Generic.Stack[string]'
    $stack.Push($root); $physical = 0
    while ($stack.Count) {
        $directory = $stack.Pop()
        foreach ($child in [IO.Directory]::EnumerateDirectories($directory)) {
            if ([IO.Path]::GetFileName($child) -ne '.git') {
                if (([IO.File]::GetAttributes($child) -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw 'Source namespace has a reparse directory'
                }
                $stack.Push($child)
            }
        }
        foreach ($file in [IO.Directory]::EnumerateFiles($directory)) {
            if ([IO.Path]::GetFileName($file) -ne '.git') { $physical++ }
        }
    }
    if ($verified -ne $ExpectedFiles -or $physical -ne $verified) { throw 'Physical source namespace differs' }
    return [pscustomobject]@{kind='windows_verified_sdk';schema_version=1;source_root=$root;
        namespace_git_blob=$NamespaceBlob;verified_files=$verified;physical_files=$physical;
        closure=$closure;compiled_or_models_or_tests=$false;scientific_verdict=$null}
}

Export-ModuleMember -Function Assert-NativeExitCode,Invoke-CheckedGit,Complete-PreparedGitClone,Test-PreparedSdk
