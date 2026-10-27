[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $InputPath,

    [string] $OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Text([object] $Value, [string] $Name) {
    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string] $Value)) {
        throw "'$Name' is required."
    }
    return ([string] $Value).Trim()
}

if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
    throw "Input file was not found: $InputPath"
}

$request = Get-Content -LiteralPath $InputPath -Raw | ConvertFrom-Json
$name = Require-Text $request.name 'name'
$description = Require-Text $request.description 'description'
$baseUrl = Require-Text $request.baseUrl 'baseUrl'

$parsedUri = $null
if (-not [Uri]::TryCreate($baseUrl, [UriKind]::Absolute, [ref] $parsedUri)) {
    throw "'baseUrl' must be an absolute URL."
}

$auth = if ($null -eq $request.auth) { [pscustomobject]@{ type = 'none' } } else {
    $authType = Require-Text $request.auth.type 'auth.type'
    if ($authType -notin @('none', 'bearer', 'apiKey', 'basic')) {
        throw "Unsupported auth.type '$authType'. Use none, bearer, apiKey, or basic."
    }
    [pscustomobject]@{ type = $authType }
}

if ($auth.type -eq 'none' -and $null -ne $request.auth.secret) {
    throw 'Secrets must not be included in the request manifest.'
}

$operations = @($request.operations)
if ($operations.Count -eq 0) {
    throw 'At least one operation is required.'
}

$tools = @()
$operationIndex = 0
foreach ($operation in $operations) {
    $operationName = Require-Text $operation.name 'operations[].name'
    $method = (Require-Text $operation.method 'operations[].method').ToUpperInvariant()
    if ($method -notin @('GET', 'POST', 'PUT', 'PATCH', 'DELETE')) {
        throw "Unsupported HTTP method '$method' for operation '$operationName'."
    }

    $path = Require-Text $operation.path 'operations[].path'
    if (-not $path.StartsWith('/')) {
        throw "Operation path must start with '/': $path"
    }

    $tools += [pscustomobject]@{
        name = $operationName
        description = Require-Text $operation.description "operations[$operationIndex].description"
        inputSchema = if ($null -eq $operation.inputSchema) {
            [pscustomobject]@{ type = 'object'; properties = [pscustomobject]@{} }
        } else { $operation.inputSchema }
        http = [pscustomobject]@{ method = $method; path = $path }
    }
    $operationIndex++
}

$manifest = [ordered]@{
    schemaVersion = '0.1'
    kind = 'mcp-api-connector'
    name = $name
    description = $description
    transport = [ordered]@{
        baseUrl = $baseUrl.TrimEnd('/')
        auth = $auth
    }
    tools = @($tools)
    safety = [ordered]@{
        secretsStored = $false
        networkRequired = $true
        requiresUserApproval = $true
    }
}

$json = $manifest | ConvertTo-Json -Depth 20
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $json
} else {
    $json | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Output "Manifest written to $OutputPath"
}
