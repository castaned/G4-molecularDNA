#!/usr/bin/env python3
"""Copiar y verificar molecularDNA local, sin descargas."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

REPO = Path(__file__).resolve().parents[1]
REQUIRED_GEOMETRY = (
    "cube-centred-X-8.txt", "turned_solenoid_750_withHistone.txt",
    "turned_twisted_solenoid_750_withHistone.txt", "straight_solenoid_750_withHistone.txt",
)


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def inventory(folder):
    return {p.relative_to(folder).as_posix(): digest(p)
            for p in sorted(folder.rglob("*"))
            if p.is_file() and "geometries" not in p.relative_to(folder).parts
            and p.name != "geometries.tar.gz"}


def discover(prefix):
    paths = [prefix / "examples/advanced/dna/moleculardna",
             prefix / "examples/extended/medical/dna/moleculardna"]
    for pattern in ("share/Geant4*/examples/advanced/dna/moleculardna",
                    "share/Geant4*/examples/extended/medical/dna/moleculardna"):
        paths.extend(prefix.glob(pattern))
    found = sorted({p.resolve() for p in paths if (p / "molecular.cc").is_file()})
    if len(found) != 1:
        raise ValueError("No se encontró un único ejemplo instalado. Pasar la ruta explícita: bash scripts/copy_example.sh /ruta/moleculardna [/ruta/geometries]")
    return found[0]


def check_geometry(folder):
    missing = [name for name in REQUIRED_GEOMETRY if not (folder / name).is_file() or (folder / name).stat().st_size == 0]
    if missing:
        raise ValueError("Faltan geometrías locales: " + ", ".join(missing) + ". Indicar un directorio geometries o archivo geometries.tar.gz local; no se descargará nada.")


def copy_example(prefix, source=None, geometry=None):
    source = source.resolve() if source else discover(prefix)
    for name in ("CMakeLists.txt", "molecular.cc", "human_cell.mac", "src", "include"):
        if not (source / name).exists():
            raise ValueError(f"Ejemplo local incompleto: falta {source / name}")
    target = REPO / "vendor/moleculardna"
    metadata = REPO / "vendor/source.json"
    if target.exists() or metadata.exists():
        raise ValueError("Ya existe una copia local. No se sobrescribe; conservarla y revisar antes de cambiar de fuente.")
    geometry = geometry.resolve() if geometry else None
    if geometry is None:
        for candidate in (source / "geometries", source / "geometries.tar.gz", REPO / "build/molecular/geometries"):
            if candidate.exists():
                geometry = candidate
                break
    if geometry is not None and not geometry.exists():
        raise ValueError("La ruta de geometrías indicada no existe")
    build = REPO / "build/molecular"
    geom_dest = build / "geometries"
    build.mkdir(parents=True, exist_ok=True)
    if geometry is None:
        print("Geometrías pendientes: CMake las prepara durante la configuración.")
    elif geom_dest.exists():
        # No combinar archivos de distintas geometrías silenciosamente.
        if geometry.resolve() != geom_dest.resolve():
            raise ValueError("Ya existe build/molecular/geometries; indicarlo explícitamente para reutilizarlo tras verificar su procedencia.")
    elif geometry.is_dir():
        check_geometry(geometry)
        shutil.copytree(geometry, geom_dest)
    else:
        with tarfile.open(geometry, "r:gz") as archive:
            # Extraer solo archivos/directorios bajo geometries, sin enlaces.
            members = archive.getmembers()
            for member in members:
                relative = Path(member.name)
                if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "geometries" or not (member.isfile() or member.isdir()):
                    raise ValueError("Archivo local de geometrías con rutas o tipos no permitidos")
            archive.extractall(build, members=members)
    if geometry is not None:
        check_geometry(geom_dest)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    data = dict(source_kind="local-geant4-installation", source_path=str(source),
                geant4_prefix=str(prefix.resolve()), geometry_source=str(geometry) if geometry else None,
                files_sha256=inventory(target))
    metadata.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Ejemplo copiado: {target}\nGeometrías: {geom_dest}\nNo se realizaron descargas.")


def verify(sources_only=False):
    metadata = json.loads((REPO / "vendor/source.json").read_text(encoding="utf-8"))
    if inventory(REPO / "vendor/moleculardna") != metadata["files_sha256"]:
        raise ValueError("Las fuentes copiadas cambiaron; registrar una nueva copia antes de compilar")
    if not sources_only:
        check_geometry(REPO / "build/molecular/geometries")
    print("Copia local verificada" if sources_only else "Copia local y geometrías verificadas")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("copy")
    p.add_argument("--prefix", required=True, type=Path)
    p.add_argument("--source", type=Path)
    p.add_argument("--geometry", type=Path)
    p = sub.add_parser("verify")
    p.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.action == "copy":
            copy_example(args.prefix, args.source, args.geometry)
        else:
            verify(args.sources_only)
    except (ValueError, OSError, KeyError, tarfile.TarError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
