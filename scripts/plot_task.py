#!/usr/bin/env python3
"""Graficar una tarea completa con las macros adaptadas del ejemplo molecularDNA."""
import argparse
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[1]
MACROS = {"e-": "human_cell_electron.C", "alpha": "human_cell_alphas.C", "proton": "human_cell_proton.C"}


def root_call(macro, *args):
    # Las rutas se pasan como literales C++ a ROOT, nunca a un shell.
    values = [json.dumps(str(a).replace("\\", "/")) if isinstance(a, (str, Path)) else str(a) for a in args]
    return f"{macro.as_posix()}({','.join(values)})"


def plot(campaign, index, dna_mbp):
    manifest = json.loads((campaign / "manifest.json").read_text(encoding="utf-8"))
    if not 0 <= index < len(manifest["tasks"]):
        raise ValueError("Índice fuera de la campaña")
    record = manifest["tasks"][index]
    macro = REPO / "analysis" / MACROS[record["particle"]]
    task = campaign / f"task_{index:05d}"
    state_file = task / "finished.json"
    if not state_file.exists():
        raise ValueError("Falta finished.json: la tarea puede seguir ejecutándose o haber terminado por TIMEOUT; revisar sacct")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    if not state.get("success"):
        raise ValueError("No graficar una tarea fallida o incompleta")
    names = state["root_files"]
    if not names or len(set(names)) != len(names) or any(Path(n).name != n or not n.endswith(".root") for n in names):
        raise ValueError("Inventario ROOT inválido")
    files = [task / n for n in names]
    if any(not p.is_file() or p.stat().st_size == 0 for p in files):
        raise ValueError("Faltan archivos ROOT de la tarea")
    output = task / "plots"
    output.mkdir(exist_ok=True)
    if len(files) == 1:
        input_file = files[0]
    else:
        input_file = output / "molecular-dna-merged.root"
        subprocess.run(["hadd", "-f", str(input_file), *map(str, files)], check=True)
    # La suma de primarios debe coincidir antes de calcular rendimientos.
    subprocess.run(["root", "-l", "-b", "-q", root_call(REPO / "analysis/inspect_output.C", input_file, record["events"])], check=True)
    subprocess.run(["root", "-l", "-b", "-q", root_call(macro, input_file, output, dna_mbp)], check=True)
    if not (output / (macro.stem + ".png")).exists():
        raise ValueError("ROOT no produjo la figura; revisar mensajes de la macro")
    print(f"Figuras PNG/PDF en {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("index", type=int)
    parser.add_argument("--dna-mbp", type=float, default=6405.886128,
                        help="Longitud ADN de human_cell, verificar contra el log de geometría")
    args = parser.parse_args()
    try:
        if not 0 < args.dna_mbp < float("inf"):
            raise ValueError("La longitud ADN debe ser finita y positiva")
        plot(args.campaign.resolve(), args.index, args.dna_mbp)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
