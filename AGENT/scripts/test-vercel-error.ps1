$marker = Join-Path $env:TEMP 'vercel-test-marker.txt'
if (Test-Path $marker) {
    Remove-Item $marker -Force
    Write-Host "Agent started, previous failure marker found - working normally now..."
    for ($i = 1; $i -le 3; $i++) {
        Write-Host "Agent is working normally (iteration $i)..."
        Start-Sleep -Milliseconds 800
    }
    Write-Host "Agent finished normally."
    exit 0
} else {
    Set-Content -Path $marker -Value 'fail-once'
    Write-Error "Failed to create stream: inference request failed: failed to generate stream from Vercel: failed to invoke model 'private/longcat-2.0' with streaming: failed to send request: POST https://ai-gateway.vercel.sh/v1/chat/completions giving up after 4 attempt(s)"
    Write-Host "Agent errored. Simulating crash..."
    exit 1
}