#!/usr/bin/env python3
"""Preparar una copia de molecularDNA 11.3 para visualizar, sin tocar vendor."""
from pathlib import Path
import re
import shutil

REPO = Path(__file__).resolve().parents[1]


def prepare(repo=REPO):
    source = repo / "vendor/moleculardna"
    target = repo / "build/visualization-source"
    geometry = repo / "build/molecular/geometries"
    if not (geometry / "cube-centred-X-8.txt").is_file():
        raise ValueError("Primero completar la compilación normal y sus geometrías")
    if target.exists():
        raise ValueError("Ya existe build/visualization-source; para recompilar usar build_visualization.sh")
    patched = {}
    for name in ("DetectorConstruction.cc", "PhysicsList.cc"):
        relative = "src/" + name
        text = (source / relative).read_text(encoding="utf-8")
        text, count = re.subn(r"G4bool\s+useParallelPhysicsWorld\s*=\s*false\s*;",
                             "G4bool useParallelPhysicsWorld = true;", text)
        if count != 1:
            raise ValueError(f"{relative}: no coincide con la flag esperada de Geant4 11.3")
        patched[relative] = text
    cmake = (source / "CMakeLists.txt").read_text(encoding="utf-8")
    old = 'if (EXISTS "${GEOMETRY_FOlDER_NAME}")'
    if cmake.count(old) != 2:
        raise ValueError("CMakeLists.txt no coincide con las dos comprobaciones de geometrías esperadas")
    patched["CMakeLists.txt"] = cmake.replace(
        old, 'if (EXISTS "${PROJECT_BINARY_DIR}/${GEOMETRY_FOlDER_NAME}")')
    lines = []
    initialize = 0
    for line in (source / "human_cell.mac").read_text(encoding="utf-8").splitlines():
        command = line.split("#", 1)[0].strip()
        key = command.split()[0] if command else ""
        if key == "/run/beamOn" or key.startswith("/vis/"):
            continue
        if key == "/control/execute":
            raise ValueError("human_cell.mac contiene otra macro; revisar antes de visualizar")
        if key == "/run/initialize":
            lines.append("/dnageom/drawCellVolumes false")
            initialize += 1
        lines.append(line)
    if initialize != 1:
        raise ValueError("human_cell.mac debe contener una sola inicialización")
    # Validar todos los cambios antes de crear la copia.
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("geometries", "geometries.tar.gz"))
    for relative, text in patched.items():
        (target / relative).write_text(text, encoding="utf-8")
    (target / "human_cell_geometry.mac").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copy2(repo / "visualization/human_cell_view.mac", target / "human_cell_view.mac")
    # molecular.cc ejecuta vis.mac automáticamente al iniciar sin -m.
    (target / "vis.mac").write_text(
        "/control/execute human_cell_geometry.mac\n/control/execute human_cell_view.mac\n",
        encoding="utf-8")
    print("Copia visual preparada en build/visualization-source")


if __name__ == "__main__":
    try:
        prepare()
    except (OSError, ValueError) as error:
        raise SystemExit(f"ERROR: {error}")
