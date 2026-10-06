# Use: . .\cap10\carregar_chave_sessao.ps1
# Lê uma chave já obtida pelo fluxo seguro do provedor; não cria chave ou arquivo.
$segredoCap10 = Read-Host 'Cole a chave de API (entrada oculta)' -AsSecureString
$ponteiroCap10 = [IntPtr]::Zero
try {
    $ponteiroCap10 = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($segredoCap10)
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ponteiroCap10)
    if ([string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
        Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
        throw 'Chave vazia; nada foi configurado.'
    }
    Write-Host 'Chave configurada somente no ambiente desta sessão. Valor não exibido.'
}
finally {
    if ($ponteiroCap10 -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ponteiroCap10)
    }
    $segredoCap10.Dispose()
    Remove-Variable segredoCap10, ponteiroCap10 -ErrorAction SilentlyContinue
}
