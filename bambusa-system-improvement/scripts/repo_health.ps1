[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$RepoRoot = ".",

    [ValidateRange(1, 100)]
    [int]$Top = 20,

    [string]$Since = "1 year ago"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedInput = (Resolve-Path -LiteralPath $RepoRoot).Path
$gitRoot = (& git -C $resolvedInput rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($gitRoot)) {
    throw "The supplied path is not inside a Git repository: $resolvedInput"
}
$gitRoot = [System.IO.Path]::GetFullPath($gitRoot.Trim())

function Invoke-RepoGit {
    param([Parameter(Position = 0, ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $output = & git -C $gitRoot @Arguments 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($Arguments -join ' ')"
    }
    return @($output)
}

function Get-TopFiles {
    param([string[]]$Paths)
    return @(
        $Paths |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
            Group-Object |
            Sort-Object Count -Descending |
            Select-Object -First $Top |
            ForEach-Object {
                [ordered]@{ file = $_.Name; changes = $_.Count }
            }
    )
}

$commitCount = [int](Invoke-RepoGit -Arguments @('rev-list', '--count', 'HEAD') | Select-Object -First 1)
$firstCommit = Invoke-RepoGit -Arguments @('log', '--reverse', '--format=%ad', '--date=short') | Select-Object -First 1
$latestCommit = Invoke-RepoGit -Arguments @('log', '-1', '--format=%ad', '--date=short') | Select-Object -First 1
$branches = @(Invoke-RepoGit -Arguments @('branch', '-a')).Count
$status = @(Invoke-RepoGit -Arguments @('status', '--short'))
$contributors = @(
    Invoke-RepoGit -Arguments @('shortlog', '-sn', '--no-merges', 'HEAD') |
        Select-Object -First 10 |
        ForEach-Object { $_.Trim() }
)

$hotspotPaths = Invoke-RepoGit -Arguments @('log', '--format=', '--name-only', "--since=$Since")
$bugPaths = Invoke-RepoGit -Arguments @('log', '-i', '-E', '--grep=fix|bug|broken|timeout|performance', '--name-only', '--format=', "--since=$Since")

$largeSourceFiles = @(
    Get-ChildItem -LiteralPath $gitRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch '[\\/](node_modules|dist|build|coverage|\.git)[\\/]' -and
            $_.Extension -in @('.ts', '.tsx', '.js', '.jsx', '.sql')
        } |
        Sort-Object Length -Descending |
        Select-Object -First $Top |
        ForEach-Object {
            [ordered]@{
                file = [System.IO.Path]::GetRelativePath($gitRoot, $_.FullName)
                bytes = $_.Length
            }
        }
)

$packageScripts = [ordered]@{}
$packagePath = Join-Path $gitRoot 'package.json'
if (Test-Path -LiteralPath $packagePath) {
    $package = Get-Content -Raw -LiteralPath $packagePath | ConvertFrom-Json
    if ($null -ne $package.scripts) {
        foreach ($property in $package.scripts.PSObject.Properties) {
            $packageScripts[$property.Name] = [string]$property.Value
        }
    }
}

$result = [ordered]@{
    repository = $gitRoot
    generated_at = (Get-Date).ToString('o')
    window = $Since
    commits = $commitCount
    first_commit = $firstCommit
    latest_commit = $latestCommit
    branches = $branches
    dirty_entries = $status.Count
    status = $status
    top_contributors = $contributors
    hotspots = @(Get-TopFiles -Paths $hotspotPaths)
    bug_magnets = @(Get-TopFiles -Paths $bugPaths)
    largest_source_files = $largeSourceFiles
    package_scripts = $packageScripts
}

$result | ConvertTo-Json -Depth 8
