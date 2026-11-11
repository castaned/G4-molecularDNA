# Graficación con las macros del ejemplo

Las macros de esta carpeta adaptan **los scripts oficiales de molecularDNA de
Geant4 v11.3.0**. Conservan sus cuatro paneles: especies, clases de daño,
SSB por origen y DSB por origen. No son un análisis independiente del ejemplo.

| Partícula GPS | Macro adaptada | Base oficial |
| --- | --- | --- |
| `e-` | `human_cell_electron.C` | `human_cell.C` |
| `alpha` | `human_cell_alphas.C` | `human_cell_alphas.C` |
| `proton` | `human_cell_proton.C` | `human_cell.C` |

## Uso recomendado desde la raíz del repositorio

```bash
source env/setup.sh
python3 scripts/plot_task.py runs/smoke-001 0
python3 scripts/plot_task.py runs/alphas-001 0
```

La selección se hace a partir de la partícula del manifest. Cada invocación usa
una sola tarea y produce PNG/PDF dentro de `task_NNNNN/plots/`. Si hay archivos de
workers, se fusionan solamente los que registra esa tarea; no se mezclan partículas,
energías o réplicas. Se comprueba el número de primarios antes de graficar.
No usar datos incompletos de un trabajo que terminó por TIMEOUT.

Uso directo si ya se tiene un archivo completo de una combinación conocida:

```bash
root -l -b -q 'analysis/human_cell_electron.C("electron.root","plots/electron")'
root -l -b -q 'analysis/human_cell_alphas.C("alpha.root","plots/alpha")'
root -l -b -q 'analysis/human_cell_proton.C("proton.root","plots/proton")'
```

En modo directo se debe comprobar manualmente que el archivo corresponda a la
partícula de la macro y que contenga todos los primarios previstos.

## Adaptaciones

- Entrada y salida por argumentos, función ROOT con nombre y exportación PNG/PDF.
- Sin `hadd` implícito dentro de la macro ni `gROOT->Reset()`.
- Semiejes de la región `human_cell`: 7100, 2500 y 7100 nm para todas las partículas.
  La macro alfa original usaba HTB177; no se usa esa masa con `human_cell.mac`.
- Longitud de referencia: 6405.886128 Mbp, tomada del `human_cell.C` oficial.
  Verificar el valor que imprime la geometría. Se puede cambiar con `--dna-mbp`.
  No usar estas macros sin adaptar masa/ADN para HTB177, MCF7 u otra geometría.
- Acumuladores inicializados, comprobación de árboles y de dosis positiva;
  se evitan lecturas de `Primary` en un buffer de un solo carácter.
- Se omite el panel de fragmentos del original, que ordenaba posiciones de
  diferentes eventos/cadenas conjuntamente. Requiere un análisis separado.

Se conservan las convenciones de dosis y rendimientos del ejemplo original.
**Solo se muestran valores centrales, sin barras de error**. Se retiraron las
fórmulas de incertidumbre heredadas: acumulan contribuciones de filas de daño,
pero las normalizan usando el número de primarios, lo que puede producir una
varianza negativa incluso cuando el rendimiento no es cero. Además, un porcentaje
relativo a un rendimiento cero no está definido. Se imprime `uncertainty: N/D`
(no determinada); no significa incertidumbre cero.
Para estimar incertidumbres hace falta un análisis por evento o réplicas independientes,
incluyendo la normalización de dosis. `SSB/DSB` también se muestra como `N/D` si DSB es cero.
Las gráficas cuentan interacciones
con ADN de las especies, no todas las especies químicas producidas en el agua.
La adaptación todavía requiere ejecución y comprobación numérica en ROOT/YUCA.

Autoría y licencia: se conservan las cabeceras de Konstantinos Chatzipapas y el
equipo molecularDNA. Las partes derivadas del ejemplo están sujetas a la licencia
Geant4 reproducida en `GEANT4-LICENSE.txt`. Las fuentes originales se copian
desde la instalación local a `vendor/moleculardna/`, sin modificarlas.
