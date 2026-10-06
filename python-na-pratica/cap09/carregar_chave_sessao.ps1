# Use: . .\cap09\carregar_chave_sessao.ps1
# Lê uma chave já obtida pelo fluxo seguro do provedor; não cria chave ou arquivo.
$segredoCap09 = Read-Host 'Cole a chave de API (entrada oculta)' -AsSecureString
$ponteiroCap09 = [IntPtr]::Zero
try {
    $ponteiroCap09 = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($segredoCap09)
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ponteiroCap09)
    if ([string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
        Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
        throw 'Chave vazia; nada foi configurado.'
    }
    Write-Host 'Chave configurada somente no ambiente desta sessão. Valor não exibido.'
}
finally {
    if ($ponteiroCap09 -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ponteiroCap09)
    }
    $segredoCap09.Dispose()
    Remove-Variable segredoCap09, ponteiroCap09 -ErrorAction SilentlyContinue
}
