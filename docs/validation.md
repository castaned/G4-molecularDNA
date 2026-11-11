---
layout: default
title: Prueba de 1,000 electrones en YUCA
---

# Prueba de 1,000 electrones en YUCA

[Volver a la guía](index.md#combinar)

Registro de la ejecución y salida comunicadas durante la prueba del
**11 de noviembre de 2026**. Permite comprobar qué parte del flujo ya funcionó
en el clúster. Los valores numéricos son resultados de esa realización;
no son valores universales ni un benchmark de validación física.

## Configuración ejecutada

| Parámetro | Valor |
| --- | --- |
| Campaña Slurm | `2240071` |
| Directorio | `runs/electrons-001/` |
| Geometría | `human_cell` |
| Partícula / energía cinética | Electrones, 0.662 MeV |
| Tareas / eventos por tarea | 10 / 100 |
| Total solicitado | 1,000 primarios |
| Semillas | Base 60001, dos semillas por tarea sin superposición |
| CPU / memoria por tarea | 1 / 8 GB |
| Máximo de tareas simultáneas | 2 |
| Límite de tiempo por tarea | 4 horas |
| Cuenta | `p002` |
| Archivo fusionado | `runs/electrons-001/electrons_1000.root` |

Se conservaron los archivos de las tareas individuales y se combinaron los
workers `molecular-dna_t0.root` de esta misma condición física. No se combinaron
partículas o energías distintas.

## Comprobación del archivo ROOT combinado

```bash
root -l -b -q 'analysis/inspect_output.C("runs/electrons-001/electrons_1000.root",1000)'
```

Salida observada:

```text
tuples/primary_source: 1000 filas
tuples/chromosome_hits: 1000 filas
tuples/classification: 640 filas
tuples/source: 640 filas
tuples/damage: 2852 filas
```

**Resultado:** el archivo combinado es legible y contiene los **1,000 primarios**
solicitados. No es necesario que todos los árboles tengan el mismo número de filas:
registran entidades diferentes. Las 640 filas de clasificación/origen no se deben
interpretar como primarios procesados, y los 2,852 registros de daño no equivalen
necesariamente a 2,852 rupturas de cadena.

## Graficación ejecutada

```bash
root -l -b -q 'analysis/human_cell_electron.C("runs/electrons-001/electrons_1000.root","runs/electrons-001/plots_combined")'
```

ROOT confirmó la creación de:

- `runs/electrons-001/plots_combined/human_cell_electron.png`
- `runs/electrons-001/plots_combined/human_cell_electron.pdf`

La macro reportó estos valores centrales:

| Magnitud | Valor observado | Unidad |
| --- | --- | --- |
| Primarios | 1,000 | electrones |
| Dosis absorbida reportada | 0.175188 | Gy |
| SSB total, suma de categorías | 210.295 | Gy⁻¹ Gbp⁻¹ |
| DSB total, suma de categorías | 8.01972 | Gy⁻¹ Gbp⁻¹ |
| SSB directo | 8.91079 | Gy⁻¹ Gbp⁻¹ |
| SSB indirecto | 195.146 | Gy⁻¹ Gbp⁻¹ |
| SSB mixto | 6.23756 | Gy⁻¹ Gbp⁻¹ |
| DSB indirecto | 6.23756 | Gy⁻¹ Gbp⁻¹ |
| DSB híbrido | 1.78216 | Gy⁻¹ Gbp⁻¹ |
| Cociente SSB/DSB reportado | 26.2222 | adimensional |

La diferencia entre 8.01972 y 8.01971 al sumar DSB por categoría u origen se
encuentra en el último decimal impreso. Se conservan los valores de la salida,
sin atribuirles más precisión ni utilizarlos como una validación de normalización.

## Qué significa que el flujo pasó

- El setup y la compilación produjeron un ejecutable funcional.
- Las simulaciones se ejecutaron por Slurm y sus ROOT se pudieron combinar.
- Se recuperaron los 1,000 primarios esperados en el archivo combinado.
- La macro generó los cuatro paneles y exportó PNG/PDF.

Esto **no comprueba por sí solo** la validez física del rendimiento, su
normalización de masa/ADN o sus incertidumbres. Para comparar científicamente,
conservar configuración, versión, semillas y réplicas, y contrastar con las
referencias del ejemplo.

## Sobre los errores porcentuales nan de esa salida

El registro aportado todavía incluía `error %: -nan` y el mensaje
`NOTE: inherited error estimates are exploratory`. Esto identifica el cálculo
heredado de incertidumbres, no un fallo de ejecución o de creación de figuras.

**No utilizar esos porcentajes como incertidumbres físicas.** Algunos incluyen
divisiones por un rendimiento cero; también se observaron valores no finitos
para rendimientos no nulos por fórmulas de momentos incompatibles con la
agrupación de registros. La corrección de las macros retira esas fórmulas y
muestra valores centrales sin barras de error, con `uncertainty: N/D`.

Si todavía aparece el mensaje heredado, publicar los cambios locales desde
Windows con `git push`, actualizar en YUCA con `git pull --ff-only` y repetir
solo el comando ROOT de graficación. No hace falta repetir los 1,000 eventos.
Estimar incertidumbres requiere un análisis por evento o entre réplicas.

[Volver a combinar y graficar](index.md#combinar) · [Solución de problemas](troubleshooting.md)
