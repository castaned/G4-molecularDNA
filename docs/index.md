---
layout: default
title: molecularDNA en YUCA — empieza aquí
---

# Generar resultados con molecularDNA en YUCA

<div class="dna-hero">
<div>
<div class="dna-label">YUCA · GEANT4 · MOLECULARDNA</div>
<h2>De la simulación al daño en el ADN</h2>
<p>Prepara el entorno, ejecuta tus simulaciones y obtén gráficas paso a paso.</p>
</div>
{% for asset in site.static_files %}{% if asset.path == '/assets/images/dna-simulation.jpg' %}<img class="dna-simulation" src="{{ '/assets/images/dna-simulation.jpg' | relative_url }}" alt="Visualización molecular del ADN con trayectorias de partículas en Geant4" width="160" height="140">{% endif %}{% endfor %}
</div>

<div class="recipe-grid">
<a class="recipe-card" href="#preparacion-inicial"><div class="recipe-step">01 · PREPARAR</div><strong>Preparación inicial</strong><span>Obtén los archivos y compila el ejemplo una sola vez.</span></a>
<a class="recipe-card" href="{{ '/electrons.html' | relative_url }}"><div class="recipe-step">02 · ELECTRONES</div><strong>Tu primera campaña</strong><span>Genera 1,000 eventos, combina las salidas y obtén las gráficas.</span></a>
<a class="recipe-card" href="{{ '/alphas.html' | relative_url }}"><div class="recipe-step">03 · ALFAS</div><strong>Explora varias energías</strong><span>Simula 1, 5 y 10 MeV y revisa los resultados por energía.</span></a>
</div>

Esta guía utiliza el clúster **YUCA** para simular el daño en el ADN con
molecularDNA. Ejecuta los comandos en una terminal de YUCA.

Copia cada bloque y comprueba el resultado antes de continuar.

<a id="preparacion-inicial"></a>
## Preparación inicial: una sola vez

Completa los pasos 1 a 4 en tu cuenta de YUCA. Cuando la compilación termine
correctamente, podrás generar nuevas simulaciones sin repetir esta preparación.

### 1. Obtener los archivos

~~~bash
git clone https://github.com/castaned/G4-molecularDNA.git
cd G4-molecularDNA
~~~

**Debe ocurrir:** al ejecutar ls aparecen las carpetas env, scripts, config y slurm.

### 2. Cargar las herramientas

~~~bash
source env/setup.sh
~~~

**Debe ocurrir:** aparecen las versiones de GCC, CMake, Geant4 y ROOT, sin errores.

**Este paso sí se repite en cada terminal nueva.** El entorno carga todas las
herramientas necesarias.

### 3. Copiar el ejemplo

~~~bash
bash scripts/copy_example.sh
~~~

**Debe ocurrir:** aparece el mensaje Ejemplo copiado.

Si dice que las geometrías están pendientes, continúa con el paso 4.
Si ya tenías una carpeta geometries de otra compilación, consulta
[cómo reutilizarla](troubleshooting.md#descarga-de-geometrías-agotada).

### 4. Compilar

Copia este bloque en la misma terminal:

~~~bash
BUILD_JOB=$(sbatch --parsable --account=p002 slurm/build.slurm)
echo "Número del trabajo: $BUILD_JOB"
~~~

**Debe ocurrir:** aparece un número. La compilación continúa aunque la terminal
vuelva a mostrar el cursor.

Consulta si terminó:

~~~bash
sacct -j "$BUILD_JOB" --format=JobID,State,ExitCode
tail -n 8 "slurm-$BUILD_JOB.out"
~~~

**Espera hasta ver COMPLETED y 0:0.** El final del archivo debe incluir:

~~~text
[100%] Built target molecular
Compilación terminada. Preparar la campaña smoke.json.
~~~

Si aparece FAILED o TIMEOUT, no continúes: abre la
[solución de problemas](troubleshooting.md).

<a id="alfas"></a>
<a id="combinar"></a>
## Generar resultados

| Quiero… | Seguir esta receta |
| --- | --- |
| Probar con dos eventos antes de una campaña | [Prueba rápida](electrons.md#prueba) |
| Simular 1,000 electrones y graficarlos | [Electrones](electrons.md#campana) |
| Simular alfas de varias energías con dos eventos por job | [Alfas](alphas.md) |

No necesitas recompilar para cambiar entre estas recetas.

## Al iniciar una nueva sesión en YUCA

Desde una terminal nueva de YUCA:

~~~bash
cd ~/G4-molecularDNA
source env/setup.sh
~~~

Después abre la receta que quieras usar. No repitas la copia ni la compilación
si ya terminaron correctamente.

<details>
<summary>Actualizar los archivos del repositorio</summary>

~~~bash
git pull --ff-only
~~~

Si Git avisa de que sobrescribiría config/electrons.json, conserva el archivo
creado manualmente y vuelve a actualizar:

~~~bash
mv -i config/electrons.json config/electrons.local.json
git pull --ff-only
~~~

Esto no modifica los resultados de campañas ya enviadas.

</details>

---

Solo si lo necesitas: [Errores y soluciones](troubleshooting.md) ·
[Explicación técnica](advanced.md) · [Resultados de la prueba realizada](validation.md).
