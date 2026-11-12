---
layout: default
title: Solución de problemas
---

# Solución de problemas

[Volver a la guía](index.md)

Antes de reintentar, leer los archivos `.err`, `.out` y `simulation.log` del trabajo.
Conservar los intentos fallidos y preparar una carpeta nueva; por ejemplo,
`runs/smoke-002` después de `runs/smoke-001`. No recompilar por un error exclusivo
de análisis ROOT o de envío Slurm.

## ROOT no aparece en Spack

**Síntoma:** `Spec 'root@6.24.08' matches no installed packages`.

En YUCA, ROOT está disponible mediante Environment Modules:

```bash
module avail root
module load root/6.24.08
root-config --version
```

El setup actual ya lo hace. No sustituirlo por `spack load root`.
Si un nodo batch no conoce `module`, ajustar `MODULE_INIT` en `env/setup.sh` a
la ruta de inicialización de módulos correspondiente al sitio.

## Descarga de geometrías agotada

**Síntoma:** `geometries-data: download FAILED: 28` tras unos 500 segundos.

Este error detiene CMake antes de compilar; no es un TIMEOUT de Slurm.
Que exista `geometries.tar.gz` con muchos MB no demuestra que sea un archivo válido:

```bash
tar -tzf build/molecular/geometries.tar.gz > /dev/null
echo $?
```

Un código diferente de cero, `unrecognized format` o un error de final de archivo
significan que no se puede usar ese archivo como geometría completa.
La solución usada en YUCA fue copiar `geometries/` de otra compilación funcional:

```bash
# Sustituir /ruta/compilacion-anterior por una ruta real.
# Usar este comando solo si build/molecular/geometries todavía no existe.
cp -a /ruta/compilacion-anterior/geometries build/molecular/
python3 scripts/local_example.py verify
sbatch --account=p067 slurm/build.slurm
```

No extraer un archivo dañado ni combinar una carpeta parcial con otra sin revisar
su contenido. No borrar una carpeta que estén usando simulaciones activas.
Con `geometries/` completa en el directorio de compilación, CMake omite la descarga.

## Cuenta Slurm o QOS

**Síntoma:** `QOSMaxSubmitJobPerUserLimit` o rechazo por política de contabilidad.

```bash
sbatch --account=p067 slurm/build.slurm
squeue -u "$USER" -o '%.18i %.10a %.12q %.10T %.30R'
```

Las pruebas originales usaron `p002`. Los ejemplos actuales usan `p067`;
indica siempre el proyecto asignado a tu cuenta. En las pruebas, el envío de compilación fue
aceptado al indicarla explícitamente. El escritorio Open OnDemand también aparece
como trabajo: no cancelarlo para intentar corregir un envío sin revisar antes.
Si el rechazo persiste con la cuenta correcta, consultar los límites con YUCA.

`JobArrayTaskLimit` como motivo de espera **no es un fallo**: con `%2`, Slurm
mantiene como máximo dos tareas del array en ejecución.

## Variables de memoria incompatibles

**Síntoma:** `SLURM_MEM_PER_CPU, SLURM_MEM_PER_GPU, and SLURM_MEM_PER_NODE are mutually exclusive`.

Puede ocurrir al enviar desde Open OnDemand, que exporta variables de su propia
asignación. El runner actual limpia `SLURM_MEM_PER_CPU` y `SLURM_MEM_PER_GPU`
solo para `srun`, y conserva la memoria por nodo solicitada con `--mem`.
Actualizar el repositorio y preparar otra campaña; no cambiar la geometría.

## Python no encontrado por srun

**Síntoma:** `execve(): python3: No such file or directory`.

```bash
python3 -c 'import sys; print(sys.executable)'
```

El envío actual pasa la ruta absoluta del intérprete y usa `srun --export=ALL`.
En la prueba funcional se utilizó Python 3.11.9 de `/shared/spack/`.
Si la ruta no está disponible en los nodos, elegir una instalación compartida.
Actualizar los scripts y preparar otra campaña. La ausencia de `simulation.log`
en este caso es esperable: molecularDNA aún no había arrancado.

## TIMEOUT de simulación

**Síntoma:** Slurm informa `TIMEOUT` y no se genera un cierre correcto.

```bash
sacct -j ID --format=JobID,State,ExitCode,Elapsed,Timelimit,MaxRSS
sinfo -o '%P %l %a'
```

Las alfas usan ahora un límite inicial de **12 horas por tarea**. No garantiza que
una configuración cualquiera termine. Revisar el avance de eventos, memoria y
el máximo permitido por la partición; después aumentar tiempo o reducir eventos
por tarea y repartirlos en más réplicas. Cada tarea repite la inicialización.
No tratar archivos ROOT parciales como si contuvieran todos los eventos solicitados.

## Al actualizar, electrons.json aparece como archivo local que se sobrescribiría

Si se creó manualmente antes de que estuviera incluido en el repositorio,
conservarlo con un nombre local antes de actualizar:

```bash
mv config/electrons.json config/electrons.local.json
git pull --ff-only
diff -u config/electrons.json config/electrons.local.json
```

El archivo local queda excluido de Git. No se alteran los manifests ni los jobs
ya enviados. Para campañas futuras se puede preparar desde cualquiera de esos JSON.

## Falta electrons.json o manifest.json

Actualizar el repositorio: `config/electrons.json` ya está incluido. Comprobar:

```bash
ls config/electrons.json
python3 scripts/campaign.py prepare config/electrons.json runs/electrons-001
```

`manifest.json` se crea con `prepare`. No ejecutar `submit` si la preparación
falló. Si se cambia un JSON después de preparar, crear otra campaña: el manifest
conserva la configuración original.

## Variable SD_SSBm o errores nan en gráficas

Las macros actuales corrigieron la declaración faltante y retiraron las fórmulas
heredadas de incertidumbre que podían producir varianzas negativas.
También se evita mostrar como cero el cociente SSB/DSB cuando DSB es cero.

`uncertainty: N/D` significa **no determinada**, no incertidumbre nula.
Las figuras muestran valores centrales sin barras de error. Aumentar estadística
no corrige por sí solo una fórmula incorrecta. Conservar réplicas para estimar
incertidumbres por evento o entre ejecuciones independientes.

Después de actualizar, repetir únicamente el análisis:

```bash
python3 scripts/plot_task.py runs/smoke-003 0
```

No hace falta recompilar ni volver a simular por estos errores de macro.

[Volver a la guía](index.md)
