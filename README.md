# G4-molecularDNA

Guía y scripts para reproducir simulaciones de daño al ADN
con **molecularDNA, Geant4 11.3.0 y Slurm en YUCA (Universidad de Sonora)**.

**Comenzar en [la guía paso a paso](docs/index.md).** Está preparada para publicarse
como página con GitHub Pages desde `main /docs`.

## Flujo

1. Clonar este repositorio en YUCA.
2. Cargar Spack, GCC y Geant4 con `source env/setup.sh`.
3. Descargar el ejemplo oficial fijado a Geant4 11.3.0 y su geometría.
4. Compilar el ejecutable `molecular` mediante Slurm.
5. Preparar `smoke.json`: una tarea de dos eventos, sin visualización.
6. Validar los archivos ROOT, graficar con las macros del ejemplo y configurar campañas.

```bash
source env/setup.sh
bash scripts/fetch_example.sh
sbatch slurm/build.slurm
# Esperar a que termine la compilación sin errores.
python3 scripts/campaign.py prepare config/smoke.json runs/smoke-001
python3 scripts/campaign.py submit runs/smoke-001 --dry-run
python3 scripts/campaign.py submit runs/smoke-001
```

Si YUCA exige partición/cuenta, ver la guía antes de enviar. Los recursos de ejemplo
son valores iniciales por medir, no asignaciones verificadas del clúster.

## Contenido

| Ruta | Función |
| --- | --- |
| `config/yuca.sh` | Setup de referencia de YUCA |
| `env/setup.sh` | Entorno C/C++, CMake, Geant4 y opcionalmente ROOT |
| `scripts/fetch_example.sh` | Fuentes oficiales y geometrías |
| `scripts/build.sh` | Compilación sin interfaz gráfica |
| `scripts/campaign.py` | Generación de macros, semillas, envío y ejecución |
| `slurm/` | Compilación y array genérico para `human_cell` |
| `config/smoke.json` | Prueba de dos electrones a 0.662 MeV |
| `config/scan.json` | Protones y alfas a 1, 5 y 10 MeV; dos réplicas |
| `config/alphas.json` | Campaña de alfas con límite de 12 horas por tarea |
| `analysis/human_cell_electron.C` | Gráficas adaptadas de `human_cell.C` |
| `analysis/human_cell_alphas.C` | Gráficas de alfas adaptadas a la geometría `human_cell` |
| `analysis/human_cell_proton.C` | Gráficas del ejemplo adaptadas a protones |
| `scripts/plot_task.py` | Selección de macro y graficación por tarea completa |
| `analysis/inspect_output.C` | Comprobación estructural de las salidas ROOT |
| `docs/` | Tutorial en español para GitHub Pages |
| `tests/` | Pruebas de generación y envío simulado, sin Geant4 |

## Estado de validación

La automatización puede probarse sin Geant4 con `python3 -m unittest discover -s tests -v`.
La compilación, disponibilidad de paquetes Spack, recursos Slurm y simulación real
**requieren una primera validación en YUCA**. No se presentan resultados físicos
ni tiempos de ejecución como si ya hubieran sido medidos.

## Procedencia

El repositorio descarga las fuentes y datasets oficiales. Incluye adaptaciones de
sus macros de análisis, con atribución y licencia en `analysis/`.
Versión: `v11.3.0`, commit `32390e802bd84a8b85ac02a90a3d31cf205dd5b7`.
La geometría, química y fuente espacial de `human_cell.mac` se conservan.
Solo se parametrizan partícula, energía, eventos, semillas y archivo de salida.
Consultar [fuentes y atribución](docs/references.md) y [publicación](docs/publishing.md).
