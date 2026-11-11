---
layout: default
title: Fuentes y atribución
---

# Fuentes y atribución

La versión inicial se basa en las siguientes fuentes primarias:

- [Geant4 v11.3.0: molecularDNA](https://github.com/Geant4/geant4/tree/v11.3.0/examples/advanced/dna/moleculardna).
- [README oficial](https://github.com/Geant4/geant4/blob/v11.3.0/examples/advanced/dna/moleculardna/README): compilación, física, resultados y bibliografía.
- [human_cell.mac](https://github.com/Geant4/geant4/blob/v11.3.0/examples/advanced/dna/moleculardna/human_cell.mac): macro base.
- [CMakeLists.txt](https://github.com/Geant4/geant4/blob/v11.3.0/examples/advanced/dna/moleculardna/CMakeLists.txt): descarga y checksum de geometrías.
- [molecular.cc](https://github.com/Geant4/geant4/blob/v11.3.0/examples/advanced/dna/moleculardna/molecular.cc): opciones `-m`, `-t`, `-p` y modo batch.
- [Documentación molecularDNA](https://geant4-dna.github.io/molecular-docs/).
- [Constructores de física Geant4-DNA](https://geant4-dna.in2p3.fr/styled-3/styled-9/index.html).
- [Procesos y modelos](https://geant4-dna.in2p3.fr/styled-3/styled-8/index.html).
- [Slurm sbatch](https://slurm.schedmd.com/sbatch.html) y [job arrays](https://slurm.schedmd.com/job_array.html).
- [GitHub Pages: fuente de publicación](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

El setup Spack procede de la configuración de referencia de YUCA.
Se confirmó ROOT 6.24/08 mediante el módulo `root/6.24.08`, cuenta Slurm `p002`
y ejecución de electrones en la partición `cpu` durante las pruebas del 11 de noviembre
de 2026. Las asignaciones, límites y recursos deben revisarse para cada campaña.

Las fuentes y datos descargados mantienen sus licencias originales. Consultar
[la licencia Geant4](https://github.com/Geant4/geant4/blob/v11.3.0/LICENSE) y citar
las publicaciones que solicita el README oficial al publicar resultados físicos.
Este repositorio no reclama autoría del código ni del modelo molecularDNA.

[Volver al tutorial](index.md)
