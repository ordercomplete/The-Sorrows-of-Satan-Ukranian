$errors = $null
$tokens = $null
[System.Management.Automation.Language.Parser]::ParseFile($args[0], [ref]$tokens, [ref]$errors) | Out-Null
if ($errors.Count -eq 0) {
    Write-Output "SYNTAX OK: $($args[0])"
} else {
    foreach ($e in $errors) {
        Write-Output ("ERROR at line {0}: {1}" -f $e.Extent.StartLineNumber, $e.Message)
    }
}
