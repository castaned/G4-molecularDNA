#!/usr/bin/env python3
"""Campañas molecularDNA: solo biblioteca estándar de Python >= 3.9."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[1]
PARTICLES = {"e-", "proton", "alpha"}
UNITS = {"eV", "keV", "MeV", "GeV"}


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def positive_int(value, name):
    if type(value) is not int or value < 1:
        raise ValueError(f"{name}: se requiere entero positivo")
    return value


def validate(cfg):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", cfg["name"]):
        raise ValueError("name: usar letras, números, guion o guion bajo")
    if not cfg["particles"] or any(p not in PARTICLES for p in cfg["particles"]):
        raise ValueError("particles: lista no vacía de e-, proton, alpha")
    if len(set(cfg["particles"])) != len(cfg["particles"]):
        raise ValueError("Hay partículas repetidas")
    if not cfg["energies"]:
        raise ValueError("energies no puede estar vacía")
    for e in cfg["energies"]:
        if type(e) not in (int, float) or not math.isfinite(e) or e <= 0:
            raise ValueError("energía: número finito positivo")
    if len(set(cfg["energies"])) != len(cfg["energies"]):
        raise ValueError("Hay energías repetidas")
    if cfg["unit"] not in UNITS:
        raise ValueError("unit: eV, keV, MeV o GeV")
    for name in ("events_per_job", "replicas", "seed_base"):
        positive_int(cfg[name], name)
    if type(cfg["physics_option"]) is not int or cfg["physics_option"] not in (2, 4, 6):
        raise ValueError("physics_option: 2, 4 o 6")
    n = len(cfg["particles"]) * len(cfg["energies"]) * cfg["replicas"]
    if cfg["seed_base"] + 2 * n >= 2147483647:
        raise ValueError("Semillas fuera del intervalo elegido")
    r = cfg["resources"]
    positive_int(r["cpus"], "cpus")
    positive_int(r["max_concurrent"], "max_concurrent")
    if not re.fullmatch(r"[1-9][0-9]*[KMGTP]?", r["memory"]):
        raise ValueError("memory: por ejemplo 8G")
    if not re.fullmatch(r"(?:[0-9]+-)?[0-9]{1,3}:[0-5][0-9]:[0-5][0-9]", r["time"]):
        raise ValueError("time: [dias-]horas:minutos:segundos")
    for key in ("partition", "account"):
        if not re.fullmatch(r"[A-Za-z0-9_.-]*", r.get(key, "")):
            raise ValueError(f"{key}: valor inválido")
    return n


def macro_text(template, particle, energy, unit, events, seeds):
    # Mantener geometría/química/fuente espacial oficiales; reemplazar solo
    # partícula, energía, beamOn y nombre de salida. Rechazar macros ambiguas.
    counts = {"/gps/particle": 0, "/gps/energy": 0, "/run/beamOn": 0, "/run/initialize": 0}
    lines = [f"/random/setSeeds {seeds[0]} {seeds[1]}"]
    for line in template.splitlines():
        command = line.split("#", 1)[0].strip()
        key = command.split()[0] if command else ""
        if key in counts:
            counts[key] += 1
        if key in ("/gps/particle", "/gps/energy", "/run/beamOn", "/analysisDNA/fileName"):
            continue
        if key.startswith("/vis/") or key == "/control/execute":
            raise ValueError("La plantilla no debe incluir visualización ni otras macros")
        lines.append(line)
    if any(c != 1 for c in counts.values()):
        raise ValueError(f"Plantilla inesperada: {counts}")
    lines += [f"/gps/particle {particle}", f"/gps/energy {energy} {unit}",
              "/analysisDNA/fileName molecular-dna", f"/run/beamOn {events}", ""]
    return "\n".join(lines)


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare(config, destination):
    cfg = json.loads(config.read_text(encoding="utf-8"))
    n = validate(cfg)
    src = REPO / "vendor/moleculardna"
    build = REPO / "build/molecular"
    binary = build / "molecular"
    template = src / "human_cell.mac"
    geometry = build / "geometries"
    if not binary.is_file() or not template.is_file() or not geometry.is_dir():
        raise ValueError("Primero copiar y compilar el ejemplo local de Geant4")
    provenance_file = REPO / "vendor/source.json"
    provenance = json.loads(provenance_file.read_text(encoding="utf-8"))
    current_files = {p.relative_to(src).as_posix(): digest(p) for p in sorted(src.rglob("*"))
                     if p.is_file() and "geometries" not in p.relative_to(src).parts and p.name != "geometries.tar.gz"}
    if not current_files or current_files != provenance["files_sha256"]:
        raise ValueError("La copia local del ejemplo cambió después de registrarla")
    if digest(build / "source.json") != digest(provenance_file):
        raise ValueError("Recompilar molecularDNA: la procedencia del binario no coincide con las fuentes")
    template_string = template.read_text(encoding="utf-8")
    # Validar antes de crear carpetas.
    macro_text(template_string, cfg["particles"][0], cfg["energies"][0], cfg["unit"], cfg["events_per_job"], (1, 2))
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "logs").mkdir()
    shutil.copy2(binary, destination / "molecular")
    shutil.copy2(template, destination / "human_cell.original.mac")
    # Inventario de geometría para comprobar integridad antes de cada trabajo.
    geometry_hashes = {str(p.relative_to(geometry)): digest(p) for p in sorted(geometry.rglob("*")) if p.is_file()}
    tasks = []
    for particle in cfg["particles"]:
        for energy in cfg["energies"]:
            for replica in range(cfg["replicas"]):
                i = len(tasks)
                seeds = [cfg["seed_base"] + 2 * i, cfg["seed_base"] + 2 * i + 1]
                folder = destination / f"task_{i:05d}"
                folder.mkdir()
                macro = folder / "run.mac"
                macro.write_text(macro_text(template_string, particle, energy, cfg["unit"], cfg["events_per_job"], seeds), encoding="utf-8")
                tasks.append(dict(id=i, particle=particle, energy=energy, unit=cfg["unit"], replica=replica,
                                  events=cfg["events_per_job"], seeds=seeds, macro_sha256=digest(macro)))
    save_json(destination / "manifest.json", dict(config=cfg, tasks=tasks, source_provenance=provenance,
        created_utc=datetime.now(timezone.utc).isoformat(), binary_sha256=digest(destination / "molecular"),
        template_sha256=digest(template), geometry=str(geometry.resolve()), geometry_sha256=geometry_hashes))
    print(f"Preparadas {n} tareas en {destination}")


def submit(destination, dry_run):
    manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    validate(manifest["config"])
    r = manifest["config"]["resources"]
    command = ["sbatch", "--parsable", "--nodes=1", "--ntasks=1", f"--cpus-per-task={r['cpus']}",
        f"--mem={r['memory']}", f"--time={r['time']}", f"--array=0-{len(manifest['tasks'])-1}%{r['max_concurrent']}",
        f"--job-name=g4dna-{manifest['config']['name']}", f"--chdir={REPO}",
        f"--output={destination}/logs/%A_%a.out", f"--error={destination}/logs/%A_%a.err"]
    for key in ("partition", "account"):
        if r.get(key):
            command.append(f"--{key}={r[key]}")
    command += [str(REPO / "slurm/run_human_cell_array.slurm"), str(REPO), str(destination)]
    print(shlex.join(command))
    if not dry_run:
        if (destination / "submission.json").exists():
            raise ValueError("Esta campaña ya fue enviada; preparar otra carpeta para repetir")
        result = subprocess.check_output(command, text=True).strip()
        save_json(destination / "submission.json", dict(job=result, command=command, manifest_sha256=digest(destination / "manifest.json")))
        print(f"Enviada campaña: {result}")


def run_task(destination, index):
    manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    if not 0 <= index < len(manifest["tasks"]):
        raise ValueError("Índice fuera del array")
    record = manifest["tasks"][index]
    task = destination / f"task_{index:05d}"
    if (task / "started.json").exists():
        raise ValueError("Tarea ya iniciada; conservar resultados y preparar otra campaña")
    binary = destination / "molecular"
    if digest(binary) != manifest["binary_sha256"] or digest(task / "run.mac") != record["macro_sha256"]:
        raise ValueError("Cambió el ejecutable o la macro después de preparar")
    geometry = Path(manifest["geometry"])
    if not manifest["geometry_sha256"]:
        raise ValueError("Inventario de geometría vacío")
    for filename, checksum in manifest["geometry_sha256"].items():
        if digest(geometry / filename) != checksum:
            raise ValueError(f"Cambió la geometría: {filename}")
    link = task / "geometries"
    if not link.exists():
        link.symlink_to(geometry, target_is_directory=True)
    elif link.resolve() != geometry.resolve():
        raise ValueError("Enlace geometries incorrecto")
    cpus = int(os.environ.get("SLURM_CPUS_PER_TASK", "1"))
    if cpus != manifest["config"]["resources"]["cpus"]:
        raise ValueError("Los CPU asignados difieren de la configuración")
    command = [str(binary), "-m", "run.mac", "-t", str(cpus), "-p", str(manifest["config"]["physics_option"])]
    metadata = dict(record, command=command, hostname=os.environ.get("HOSTNAME", ""),
        slurm_job=os.environ.get("SLURM_JOB_ID", ""), cpus=cpus, started_utc=datetime.now(timezone.utc).isoformat())
    save_json(task / "started.json", metadata)
    with open(task / "simulation.log", "w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=task, stdout=log, stderr=subprocess.STDOUT)
    logtext = (task / "simulation.log").read_text(encoding="utf-8", errors="replace")
    files = [p for p in task.glob("molecular-dna*.root") if p.stat().st_size > 0]
    # molecular.cc no propaga siempre el error de ApplyCommand al exit code.
    ui_error = bool(re.search(r"COMMAND NOT FOUND|command refused|illegal application state|Cannot open macro file|G4Exception-START|\*{3,} COMMAND", logtext, re.I))
    success = result.returncode == 0 and bool(files) and not ui_error
    save_json(task / "finished.json", dict(returncode=result.returncode, success=success,
        ui_error=ui_error, root_files=[p.name for p in files], finished_utc=datetime.now(timezone.utc).isoformat()))
    if not success:
        raise ValueError(f"Falló task_{index:05d}; revisar simulation.log")
    print(f"Tarea {index}: ejecución terminada, {len(files)} archivo(s) ROOT; validar con inspect_output.C")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("config", type=Path)
    p.add_argument("destination", type=Path)
    p = sub.add_parser("submit")
    p.add_argument("destination", type=Path)
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("run-task")
    p.add_argument("destination", type=Path)
    p.add_argument("index", type=int)
    args = parser.parse_args()
    try:
        destination = args.destination.resolve()
        if args.action == "prepare":
            prepare(args.config.resolve(), destination)
        elif args.action == "submit":
            submit(destination, args.dry_run)
        else:
            run_task(destination, args.index)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
