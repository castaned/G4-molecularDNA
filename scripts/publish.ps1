param([string]$Owner = 'castaned', [string]$Name = 'G4-molecularDNA')
# En Windows PowerShell 5 los errores stderr de comandos nativos usados como
# sondeo no deben convertirse en excepciones antes de revisar LASTEXITCODE.
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path -Parent $PSScriptRoot) -ErrorAction Stop
$gh = (Get-Command gh -ErrorAction SilentlyContinue).Source
if (-not $gh -and (Test-Path 'C:\Program Files\GitHub CLI\gh.exe')) { $gh = 'C:\Program Files\GitHub CLI\gh.exe' }
if (-not $gh) { throw 'Instalar GitHub CLI y abrir otra ventana de PowerShell.' }
function Run-Gh {
    & $gh @args
    if ($LASTEXITCODE -ne 0) { throw 'Falló el comando GitHub CLI; revisar el mensaje anterior.' }
}
$loginName = & $gh api user --jq .login
if ($LASTEXITCODE -ne 0) { throw 'No se pudo verificar la cuenta. Revisar conexión y gh auth status.' }
if ($loginName -ne $Owner) { throw "Cuenta actual: $loginName; se esperaba $Owner." }
Run-Gh auth setup-git
$changes = git status --porcelain
if ($changes) { throw 'Hay cambios sin commit. Revisarlos y hacer git add . y git commit antes de publicar.' }
$commit = git rev-parse --verify HEAD 2>$null
if ($LASTEXITCODE -ne 0) { throw 'Primero crear el commit inicial.' }
$originUrl = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    & $gh repo view "$Owner/$Name" --json name 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        git remote add origin "https://github.com/$Owner/$Name.git"
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo configurar origin.' }
        git push -u origin main
        if ($LASTEXITCODE -ne 0) { throw 'No se subió main; revisar historial remoto sin forzar push.' }
    } else {
        Run-Gh repo create "$Owner/$Name" --public --source . --remote origin --push --description 'Guía reproducible de molecularDNA con Geant4 11.3 y Slurm en YUCA'
    }
} else {
    if ($originUrl -notin @("https://github.com/$Owner/$Name.git", "git@github.com:$Owner/$Name.git")) {
        throw "origin apunta a otro destino: $originUrl"
    }
    git push -u origin main
    if ($LASTEXITCODE -ne 0) { throw 'Falló git push; revisar el mensaje anterior.' }
}
$pagesBody = @{ source = @{ branch = 'main'; path = '/docs' } } | ConvertTo-Json -Compress
& $gh api "repos/$Owner/$Name/pages" --jq .html_url 2>$null
if ($LASTEXITCODE -eq 0) {
    $pagesBody | & $gh api --method PUT "repos/$Owner/$Name/pages" --input -
} else {
    $pagesBody | & $gh api --method POST "repos/$Owner/$Name/pages" --input -
}
if ($LASTEXITCODE -ne 0) { throw 'Repositorio subido. Configurar Pages en Settings > Pages: main /docs.' }
Write-Host "Repositorio: https://github.com/$Owner/$Name"
Write-Host "Página (cuando termine el despliegue): https://$Owner.github.io/$Name/"
