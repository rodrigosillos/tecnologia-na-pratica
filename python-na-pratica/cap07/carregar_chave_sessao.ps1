# Use: . .\cap07\carregar_chave_sessao.ps1
# Lê uma chave já obtida pelo fluxo seguro do provedor; não cria chave ou arquivo.
$segredoCap07 = Read-Host 'Cole a chave de API (entrada oculta)' -AsSecureString
$ponteiroCap07 = [IntPtr]::Zero
try {
    $ponteiroCap07 = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($segredoCap07)
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ponteiroCap07)
    if ([string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
        Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
        throw 'Chave vazia; nada foi configurado.'
    }
    Write-Host 'Chave configurada somente no ambiente desta sessão. Valor não exibido.'
}
finally {
    if ($ponteiroCap07 -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ponteiroCap07)
    }
    $segredoCap07.Dispose()
    Remove-Variable segredoCap07, ponteiroCap07 -ErrorAction SilentlyContinue
}
