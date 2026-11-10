---
layout: default
title: Publicación y cambios
---

# Publicación y cambios

## Crear el repositorio desde Windows

Instalar GitHub CLI y autenticar desde PowerShell normal de Windows:

```powershell
winget install --id GitHub.cli --exact
# Abrir otra ventana de PowerShell tras instalar.
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
gh auth status
```

Desde la raíz local del proyecto ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish.ps1
```

El script verifica la cuenta `castaned`, crea el repositorio público si no existe,
conecta `origin`, sube `main` y configura GitHub Pages desde `main /docs`.
No fuerza pushes ni elimina contenido remoto. Si ya existe un repositorio con
contenido distinto, detenerse y revisar su historial antes de integrar cambios.

Si Git no tiene identidad configurada, el script pide configurarla para este
repositorio. No almacena tokens en archivos del proyecto.

La página esperada después del despliegue es:
[castaned.github.io/G4-molecularDNA](https://castaned.github.io/G4-molecularDNA/).
La URL solo estará disponible después de crear y publicar el repositorio.

Alternativa para Pages: en GitHub abrir **Settings → Pages → Build and deployment**,
seleccionar **Deploy from a branch**, rama `main`, carpeta `/docs`, y guardar.
Consultar el trabajo de despliegue en **Actions** si aún no aparece la página.

## Mantener cambios locales y remotos

```powershell
git status
git pull --ff-only
# Editar y verificar cambios.
git add .
git commit -m "Describe el cambio"
git push
```

Si ChatGPT puede editar archivos pero su terminal no tiene red, los cambios locales
se pueden revisar y subir con `git push` desde PowerShell normal. La autenticación
del conector GitHub de ChatGPT y la de GitHub CLI local son independientes.
No compartir tokens ni contraseñas en el chat.

## Comprobaciones automáticas

GitHub Actions ejecuta comprobación sintáctica Bash y pruebas Python del generador.
Estas pruebas no compilan Geant4 ni ejecutan física; la aceptación final requiere
una prueba en YUCA siguiendo el tutorial.

[Volver al tutorial](index.md)
