"""Run the proton ROOT analysis and plot classified damage versus LET."""
import argparse
import csv
import json
import math
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


def read_points(index):
    points = []
    with index.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            energy = float(row["energy_mev"])
            let = float(row["let_kev_um"])
            source = row["let_source"].strip()
            path = (index.parent / row["root_file"]).resolve()
            if not all(math.isfinite(x) and x > 0 for x in (energy, let)):
                raise ValueError("Energy and LET must be finite and positive")
            if not source or not path.is_file():
                raise ValueError(f"Missing LET source or ROOT file: {path}")
            points.append((let, energy, source, path))
    if len(points) < 2 or len({p[1] for p in points}) != len(points):
        raise ValueError("Provide at least two points, one row per energy")
    if len({p[3] for p in points}) != len(points):
        raise ValueError("Use a separate ROOT file for each energy")
    return sorted(points)


def summarize(points):
    macro = Path(__file__).resolve().parents[1] / "analysis/human_cell_proton.C"
    rows = []
    with TemporaryDirectory() as temp:
        scratch = Path(temp)
        for i, (let, energy, source, path) in enumerate(points):
            summary = scratch / f"point-{i}.csv"
            args = [path.as_posix(), (scratch / f"plots-{i}").as_posix()]
            call = ",".join([*(json.dumps(a) for a in args), "6405.886128",
                             json.dumps(summary.as_posix())])
            subprocess.run(["root", "-l", "-b", "-q", f"{macro.as_posix()}({call})"],
                           check=True)
            if not summary.is_file():
                raise ValueError(f"ROOT did not export a summary for {path}")
            with summary.open(newline="") as stream:
                row, = csv.DictReader(stream)
            ssb, dsb = int(row["ssb_count"]), int(row["dsb_count"])
            exposure = float(row["dose_gy"]) * float(row["dna_gbp"])
            if not math.isfinite(exposure) or exposure <= 0 or min(ssb, dsb) < 0:
                raise ValueError(f"Invalid dose, DNA length or counts for {path}")
            rows.append(dict(energy_mev=energy, let_kev_um=let, let_source=source,
                             root_file=str(path), **row, ssb_yield=ssb / exposure,
                             dsb_yield=dsb / exposure, ssb_dsb=ssb / dsb if dsb else None))
    return rows


def plot(root, rows, output):
    root.gROOT.SetBatch(True)
    canvas = root.TCanvas("proton_let", "Proton damage versus LET", 1100, 850)
    canvas.Divide(2, 2)
    graphs = []
    panels = [
        ("ssb_yield", "SSB yield (Gy^{-1} Gbp^{-1})"),
        ("dsb_yield", "DSB yield (Gy^{-1} Gbp^{-1})"),
        ("ssb_dsb", "SSB / DSB"),
    ]
    for pad, (key, label) in enumerate(panels, 1):
        canvas.cd(pad)
        root.gPad.SetLeftMargin(0.16)
        graph = root.TGraph()
        for row in rows:
            if row[key] is not None:
                graph.SetPoint(graph.GetN(), row["let_kev_um"], row[key])
        if graph.GetN():
            graph.SetTitle(f";LET in water (keV/#mum);{label}")
            graph.SetMarkerStyle(20)
            graph.SetMarkerColor(root.kBlue + 1)
            graph.Draw("AP")
            graphs.append(graph)
        else:
            note = root.TLatex()
            note.SetNDC()
            note.DrawLatex(0.15, 0.5, "SSB / DSB undefined: DSB = 0")
            graphs.append(note)
    canvas.SaveAs(str(output / "proton_damage_vs_let.png"))
    canvas.SaveAs(str(output / "proton_damage_vs_let.pdf"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        import ROOT
        rows = summarize(read_points(args.index))
        args.output.mkdir(parents=True, exist_ok=True)
        with (args.output / "proton_let.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        plot(ROOT, rows, args.output)
    except (ImportError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
