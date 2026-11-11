---
layout: default
title: molecularDNA en YUCA — empieza aquí
---

# Generar resultados con molecularDNA

**Esta guía es una receta. Copia un bloque, ejecútalo y comprueba el resultado
antes de pasar al siguiente.**

Abre una terminal de **YUCA**. Todos los comandos de esta página se ejecutan allí,
no en PowerShell de Windows.

**¿Ya compilaste el ejemplo?** Ve directamente a una receta:

- [Electrones: generar 1,000 eventos y obtener las gráficas](electrons.md).
- [Alfas: generar resultados para 1, 5 y 10 MeV](alphas.md).

## 1. Obtener los archivos

Solo la primera vez:

~~~bash
git clone https://github.com/castaned/G4-molecularDNA.git
cd G4-molecularDNA
~~~

**Debe ocurrir:** al ejecutar ls aparecen las carpetas env, scripts, config y slurm.

## 2. Cargar las herramientas

~~~bash
source env/setup.sh
~~~

**Debe ocurrir:** aparecen las versiones de GCC, CMake, Geant4 y ROOT, sin errores.

Hazlo una vez cada vez que abras una terminal nueva. No necesitas cargar nada más
por separado.

## 3. Copiar el ejemplo

Solo la primera vez:

~~~bash
bash scripts/copy_example.sh
~~~

**Debe ocurrir:** aparece el mensaje Ejemplo copiado.

Si dice que las geometrías están pendientes, continúa con el paso 4.
Si ya tenías una carpeta geometries de otra compilación, consulta
[cómo reutilizarla](troubleshooting.md#descarga-de-geometrías-agotada).

## 4. Compilar

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
## 5. Elegir qué simular

| Quiero… | Seguir esta receta |
| --- | --- |
| Probar con dos eventos antes de una campaña | [Prueba rápida](electrons.md#prueba) |
| Simular 1,000 electrones y graficarlos | [Electrones](electrons.md#campana) |
| Simular alfas de varias energías con dos eventos por job | [Alfas](alphas.md) |

No necesitas recompilar para cambiar entre estas recetas.

## Si vuelves otro día

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
