#!/usr/bin/env python3
"""Preparar una copia de molecularDNA 11.3 para visualizar, sin tocar vendor."""
from pathlib import Path
import argparse
import re
import shutil

REPO = Path(__file__).resolve().parents[1]


def configure_view(repo=REPO, segment="straight"):
    """Una sola colocación centrada; solo macros y datos de la copia visual."""
    if segment not in ("straight", "turn", "turntwist"):
        raise ValueError("Segmento desconocido")
    target = repo / "build/visualization-source"
    if not (target / "CMakeLists.txt").is_file():
        raise ValueError("Primero preparar la copia visual")
    lines = []
    placements = 0
    for line in (repo / "vendor/moleculardna/human_cell.mac").read_text(encoding="utf-8").splitlines():
        command = line.split("#", 1)[0].strip()
        fields = command.split()
        key = fields[0] if fields else ""
        if key == "/run/beamOn" or key.startswith("/vis/") or key == "/dnageom/drawCellVolumes":
            continue
        if key == "/control/execute":
            raise ValueError("La plantilla contiene otra macro")
        if key == "/dnageom/placementVolume":
            if len(fields) < 3 or fields[1] != segment:
                continue
            placements += 1
        if key == "/dnageom/definitionFile":
            line = "/dnageom/definitionFile single_segment.txt"
        elif key == "/world/worldSize":
            line = "/world/worldSize 1 um"
        elif key == "/cell/radiusSize":
            line = "/cell/radiusSize 150 150 150 nm"
        elif key == "/chromosome/add":
            line = "/chromosome/add cell ellipse 100 100 100 0 0 0 nm 0 0 0"
        elif key == "/run/initialize":
            lines.append("/dnageom/drawCellVolumes false")
        lines.append(line)
    if placements != 1:
        raise ValueError("No se encontró una definición única del segmento")
    macro = "\n".join(lines) + "\n"
    definition = "# IDX KIND POS_X POS_Y POS_Z EUL_PSI EUL_THETA EUL_PHI\n"
    definition += f"0 {segment} 0 0 0 0 0 0\n"
    view = (repo / "visualization/human_cell_view.mac").read_text(encoding="utf-8")
    show = (repo / "visualization/show_dna.mac").read_text(encoding="utf-8")
    show = show.replace("/vis/geometry/set/visibility straight 0 true",
                        f"/vis/geometry/set/visibility {segment} 0 true")
    startup = "/control/execute human_cell_geometry.mac\n/control/execute human_cell_view.mac\n"
    for folder in (target, repo / "build/visualization"):
        if folder.is_dir():
            for name, text in (("human_cell_geometry.mac", macro), ("single_segment.txt", definition),
                               ("human_cell_view.mac", view), ("show_dna.mac", show), ("vis.mac", startup)):
                (folder / name).write_text(text, encoding="utf-8")
    print(f"Vista de un solo segmento {segment}, centrado en el origen; sin eventos")


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
    configure_view(repo)
    print("Copia visual preparada en build/visualization-source")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Actualizar macros de una copia visual existente, sin recompilar")
    parser.add_argument("--segment", choices=("straight", "turn", "turntwist"), default="straight")
    args = parser.parse_args()
    try:
        if args.refresh:
            configure_view(segment=args.segment)
        else:
            prepare()
            if args.segment != "straight":
                configure_view(segment=args.segment)
    except (OSError, ValueError) as error:
        raise SystemExit(f"ERROR: {error}")
