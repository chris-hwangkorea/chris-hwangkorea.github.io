$watchFolder = "$env:USERPROFILE\Desktop"
$repoFolder = "D:\project\github-pages"
$files = @("ebook_library.html", "projects.html")

$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $watchFolder
$watcher.Filter = "*.html"
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite
$watcher.EnableRaisingEvents = $true

$action = {
    $changedFile = $Event.SourceEventArgs.Name
    if ($changedFile -in @("ebook_library.html", "projects.html")) {
        Start-Sleep -Seconds 2
        foreach ($file in @("ebook_library.html", "projects.html")) {
            $src = "$env:USERPROFILE\Desktop\$file"
            $dst = "D:\project\github-pages\$file"
            if (Test-Path $src) {
                Copy-Item $src $dst -Force
            }
        }
        Set-Location "D:\project\github-pages"
        git add . 2>&1 | Out-Null
        $status = git status --porcelain 2>&1
        if ($status) {
            git commit -m "자동 업데이트: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>&1 | Out-Null
            git push 2>&1 | Out-Null
        }
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null

while ($true) {
    Start-Sleep -Seconds 10
}
