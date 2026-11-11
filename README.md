# G4-molecularDNA

Guía y scripts para reproducir simulaciones de daño al ADN
con **molecularDNA, Geant4 11.3.0 y Slurm en YUCA (Universidad de Sonora)**.

**Comenzar en [la guía paso a paso](docs/index.md).** Está preparada para publicarse
como página con GitHub Pages desde `main /docs`.

## Flujo

1. Clonar este repositorio en YUCA.
2. Cargar Spack, GCC, CMake, Geant4 y ROOT con `source env/setup.sh`.
3. Copiar molecularDNA desde la instalación local de Geant4.
4. Configurar y compilar `molecular` mediante Slurm; CMake prepara las geometrías.
5. Preparar `smoke.json`: una tarea de dos eventos, sin visualización.
6. Validar los archivos ROOT, graficar con las macros del ejemplo y configurar campañas.

```bash
source env/setup.sh
bash scripts/copy_example.sh
sbatch slurm/build.slurm
# Esperar a que termine la compilación sin errores.
python3 scripts/campaign.py prepare config/smoke.json runs/smoke-001
python3 scripts/campaign.py submit runs/smoke-001 --dry-run
python3 scripts/campaign.py submit runs/smoke-001
```

La cuenta Slurm configurada es **`p002`**, tanto para compilar como para las campañas.
Si YUCA exige una partición específica, ver la guía antes de enviar. Los recursos de ejemplo
son valores iniciales por medir, no asignaciones verificadas del clúster.

## Contenido

| Ruta | Función |
| --- | --- |
| `env/setup.sh` | Único setup: GCC/CMake/Geant4 por Spack; ROOT mediante `module load root/6.24.08` |
| `scripts/copy_example.sh` | Copia local desde la instalación Geant4, sin descargar |
| `scripts/local_example.py` | Localización, copia y verificación de fuentes/geometrías |
| `scripts/build.sh` | Compilación sin interfaz gráfica |
| `scripts/campaign.py` | Generación de macros, semillas, envío y ejecución |
| `slurm/` | Compilación y array genérico para `human_cell` |
| `config/smoke.json` | Prueba de dos electrones a 0.662 MeV |
| `config/electrons.json` | 1,000 electrones: diez tareas de cien eventos y dos simultáneas |
| `config/scan.json` | Protones y alfas a 1, 5 y 10 MeV; dos réplicas |
| `config/alphas.json` | Campaña de alfas con límite de 12 horas por tarea |
| `analysis/human_cell_electron.C` | Gráficas adaptadas de `human_cell.C` |
| `analysis/human_cell_alphas.C` | Gráficas de alfas adaptadas a la geometría `human_cell` |
| `analysis/human_cell_proton.C` | Gráficas del ejemplo adaptadas a protones |
| `scripts/plot_task.py` | Selección de macro y graficación por tarea completa |
| `analysis/inspect_output.C` | Comprobación estructural de las salidas ROOT |
| `docs/` | Tutorial en español para GitHub Pages |
| `docs/troubleshooting.md` | Errores encontrados y soluciones durante las pruebas |
| `tests/` | Pruebas de generación y envío simulado, sin Geant4 |

## Estado de validación

La automatización puede probarse sin Geant4 con `python3 -m unittest discover -s tests -v`.
El 11 de noviembre de 2026 se verificaron en YUCA el setup, compilación, simulación
Slurm de dos electrones, lectura de los árboles ROOT y generación de PNG/PDF.
El trabajo de prueba terminó en 1 min 11 s; ese tiempo no se extrapola a otras
configuraciones. La campaña de 1,000 electrones se completó, se fusionó y se
comprobó el total de primarios; también se generaron las figuras PNG/PDF.
Ver [registro de resultados](docs/validation.md). Estas comprobaciones del flujo
no sustituyen la validación física del modelo, de la normalización ni de las incertidumbres.

## Procedencia

El ejemplo se copia desde la instalación local de Geant4 en YUCA al espacio de
trabajo del usuario (`vendor/moleculardna`), sin descargarlo de Internet.
Se registra su ubicación e inventario SHA-256; la compilación y las campañas
comprueban que se usa esa copia. Incluye adaptaciones de las macros de análisis,
con atribución y licencia en `analysis/`, basadas en Geant4 `v11.3.0`.
La geometría, química y fuente espacial de `human_cell.mac` se conservan.
Solo se parametrizan partícula, energía, eventos, semillas y archivo de salida.
Consultar [fuentes y atribución](docs/references.md) y [publicación](docs/publishing.md).
