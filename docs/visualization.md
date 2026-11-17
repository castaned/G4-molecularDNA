---
layout: default
title: Visualizar human_cell en YUCA
---

# Visualizar la geometría de human_cell

[Volver al inicio](index.md)

**Objetivo:** abrir la geometría del modelo de fibroblasto y explorar sus
segmentos de cromatina en el escritorio remoto de YUCA. No se simulan eventos.

## 1. Abrir el escritorio YUCA

Inicia una sesión de escritorio en Open OnDemand y abre su terminal.
La ventana gráfica necesita ese escritorio; el envío habitual de un array no la abre.
La preparación normal del ejemplo y sus geometrías debe haber terminado.

~~~bash
cd ~/G4-molecularDNA
git pull --ff-only
source env/setup.sh
~~~

## 2. Preparar una copia para visualización — una sola vez

~~~bash
python3 scripts/prepare_visualization.py
~~~

**Debe ocurrir:** aparece Copia visual preparada en build/visualization-source.
Si ya existe, continúa con la compilación; no necesitas repetir la preparación.

El script activa estas flags **solo en la copia**:

| Archivo | Valor para visualizar |
| --- | --- |
| src/DetectorConstruction.cc | G4bool useParallelPhysicsWorld = true; |
| src/PhysicsList.cc | G4bool useParallelPhysicsWorld = true; |

También crea human_cell_geometry.mac a partir de human_cell.mac, sin beamOn,
y un vis.mac que carga la geometría y la vista. No edites vendor/moleculardna:
las campañas comprueban la integridad de esas fuentes.

## 3. Compilar con soporte gráfico — una sola vez

En la terminal del escritorio, usando los recursos asignados a esa sesión:

~~~bash
bash scripts/build_visualization.sh
~~~

**Debe ocurrir:** aparece Built target molecular y el mensaje Visualización compilada.
La opción de CMake es **WITH_GEANT4_UIVIS=ON**. Se compila en
build/visualization; build/molecular conserva el ejecutable de las campañas.
Las geometrías se reutilizan mediante un enlace, sin volver a descargarlas.

## 4. Abrir la geometría

~~~bash
cd ~/G4-molecularDNA/build/visualization
./molecular -t 1 -p 2
~~~

**Debe ocurrir:** se abre el visor OpenGL y aparece la consola de Geant4.
La carga y el dibujo de toda la geometría pueden tardar. No escribas beamOn
para esta práctica de geometría.

Estos comandos se escriben **en la consola de Geant4**, no en Bash.

### Ver el conjunto y cambiar el ángulo

~~~text
/vis/viewer/zoomTo 1
/vis/viewer/panTo 0 0 nm
/vis/viewer/set/viewpointThetaPhi 90 180
~~~

**Qué esperar:** una vista del conjunto. A esta escala no distinguirás bases individuales.

### Acercarse a una región

~~~text
/vis/viewer/zoomTo 150
/vis/viewer/panTo -720 -320 nm
~~~

Es el encuadre usado como referencia en la macro visual del ejemplo 11.3;
si tu vista queda vacía, vuelve al conjunto y desplázate gradualmente.
Para ajustar el encuadre:

~~~text
/vis/viewer/zoom 1.5
/vis/viewer/pan 50 0 nm
/vis/viewer/set/viewpointThetaPhi 60 120
~~~

zoom amplía respecto a la vista actual; zoomTo establece un valor absoluto.
pan desplaza respecto a la posición actual; panTo establece el desplazamiento.

### Recuperar la vista inicial

~~~text
/vis/viewer/zoomTo 1
/vis/viewer/panTo 0 0 nm
/vis/viewer/set/viewpointThetaPhi 90 180
/vis/viewer/flush
~~~

## 5. Qué estás observando

human_cell representa un modelo geométrico de ADN organizado en cromatina
dentro de una región nuclear. Los segmentos rectos, curvos y retorcidos se
repiten para construir la organización de mayor escala. Al acercarte puedes
distinguir los componentes moleculares y las histonas; el aspecto depende de
la escala y del volumen visible. Es un modelo de simulación, no una fotografía
de una célula ni una predicción del daño por sí mismo.

## Si la ventana no abre o no se ve ADN

| Síntoma | Comprobación |
| --- | --- |
| Falta DISPLAY o no abre OpenGL | Ejecutar desde una terminal del escritorio YUCA |
| No encuentra DNAWorld | Usar build/visualization/molecular y comprobar que ambas flags estén en true |
| Solo aparecen volúmenes grandes | Comprobar /dnageom/drawCellVolumes false antes de /run/initialize |
| Vista vacía al acercarse | Recuperar zoomTo 1 y panTo 0 0 nm |
| El dibujo tarda mucho | No confundir la renderización del ADN completo con simulación de eventos |

Si el visor OGL no está disponible, consulta /vis/list en Geant4 y comparte
los drivers disponibles. No se requiere cambiar la energía de las partículas
para visualizar una geometría sin eventos.

## Volver a las simulaciones

Cierra el visor y vuelve a la raíz del repositorio. Las recetas de
[electrones](electrons.md), [protones](protons.md) y [alfas](alphas.md) siguen
usando el ejecutable normal. No uses el ejecutable visual para producir sus campañas.

<details>
<summary>Archivos y referencia de los cambios</summary>

La preparación está diseñada para las fuentes de Geant4 11.3.0 y se detiene
si no encuentra las flags esperadas. La receta y el soporte gráfico todavía
deben comprobarse en una sesión gráfica de YUCA.

Referencias del código original:
[DetectorConstruction.cc](https://github.com/Geant4/geant4/blob/v11.3.0/examples/advanced/dna/moleculardna/src/DetectorConstruction.cc),
[PhysicsList.cc](https://github.com/Geant4/geant4/blob/v11.3.0/examples/advanced/dna/moleculardna/src/PhysicsList.cc),
[vis.mac](https://github.com/Geant4/geant4/blob/v11.3.0/examples/advanced/dna/moleculardna/vis.mac).
Se conserva la licencia Geant4 en las fuentes copiadas.

</details>
