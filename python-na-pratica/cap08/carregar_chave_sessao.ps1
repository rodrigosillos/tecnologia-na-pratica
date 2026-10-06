# Use: . .\cap08\carregar_chave_sessao.ps1
# Lê uma chave já obtida pelo fluxo seguro do provedor; não cria chave ou arquivo.
$segredoCap08 = Read-Host 'Cole a chave de API (entrada oculta)' -AsSecureString
$ponteiroCap08 = [IntPtr]::Zero
try {
    $ponteiroCap08 = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($segredoCap08)
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ponteiroCap08)
    if ([string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
        Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
        throw 'Chave vazia; nada foi configurado.'
    }
    Write-Host 'Chave configurada somente no ambiente desta sessão. Valor não exibido.'
}
finally {
    if ($ponteiroCap08 -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ponteiroCap08)
    }
    $segredoCap08.Dispose()
    Remove-Variable segredoCap08, ponteiroCap08 -ErrorAction SilentlyContinue
}
