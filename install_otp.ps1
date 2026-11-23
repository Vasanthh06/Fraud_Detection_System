Set-Location E:\ShopZone\Shopzone
$content = Get-Clipboard -Raw
if ($content -notmatch 'ShopZone OTP installer') {
    Write-Host "Clipboard does not contain the script. Copy the full script first." -ForegroundColor Red
} else {
    Set-Content -Path .\install_otp.ps1 -Value $content -Encoding UTF8 -NoNewline
    Write-Host "Wrote install_otp.ps1 ($($content.Length) chars)." -ForegroundColor Green
    Get-Item .\install_otp.ps1 | Select-Object Name, Length, LastWriteTime
}