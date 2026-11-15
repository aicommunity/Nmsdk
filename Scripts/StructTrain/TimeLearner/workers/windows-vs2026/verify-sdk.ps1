param(
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [Parameter(Mandatory=$true)][string]$RootCommit,
    [Parameter(Mandatory=$true)][string]$NamespaceBlob,
    [Parameter(Mandatory=$true)][int]$ExpectedFiles,
    [Parameter(Mandatory=$true)][int]$ExpectedRepositories
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Import-Module (Join-Path $PSScriptRoot 'GitPreparation.psm1') -Force
Test-PreparedSdk -SourceRoot $SourceRoot -RootCommit $RootCommit -NamespaceBlob $NamespaceBlob `
    -ExpectedFiles $ExpectedFiles -ExpectedRepositories $ExpectedRepositories | ConvertTo-Json -Depth 5
