import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
import uuid
import shutil
from contextlib import contextmanager
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("campaign", ROOT / "scripts/campaign.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
TEMPLATE = """/world/worldSize 50 um
/dnageom/definitionFile geometries/cube-centred-X-8.txt
/run/initialize
/gps/pos/type Plane
/gps/particle e-
/gps/energy 0.662 MeV
/run/beamOn 2
"""


@contextmanager
def workspace_temp():
    # mkdir con permisos normales evita ACL restrictivas de mkdtemp en Windows.
    folder = ROOT / "tests" / ("scratch_" + uuid.uuid4().hex)
    folder.mkdir()
    try:
        yield str(folder)
    finally:
        shutil.rmtree(folder)


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "config/smoke.json").read_text())

    def test_reject_unsafe_and_nonphysical_config(self):
        for key, value in [("name", "../outside"), ("events_per_job", 0),
                           ("seed_base", 2147483646), ("energies", [float("nan")]),
                           ("particles", ["ion"]), ("physics_option", True)]:
            cfg = copy.deepcopy(self.cfg)
            cfg[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                c.validate(cfg)

    def test_macro_keeps_geometry_and_initializes_before_beam(self):
        text = c.macro_text(TEMPLATE, "alpha", 5, "MeV", 17, (12001, 12002))
        self.assertIn("/dnageom/definitionFile geometries/cube-centred-X-8.txt", text)
        self.assertIn("/gps/energy 5 MeV", text)
        self.assertEqual(text.count("/run/beamOn"), 1)
        self.assertLess(text.index("/run/initialize"), text.index("/run/beamOn"))
        self.assertTrue(text.startswith("/random/setSeeds"))

    def test_reject_template_with_nested_execution(self):
        with self.assertRaises(ValueError):
            c.macro_text(TEMPLATE + "/control/execute vis.mac\n", "e-", 1, "MeV", 2, (1, 2))

    def test_prepare_grid_seeds_and_submission(self):
        with workspace_temp() as tmp:
            repo = Path(tmp)
            src = repo / "vendor/moleculardna"
            src.mkdir(parents=True)
            (src / "human_cell.mac").write_text(TEMPLATE)
            build = repo / "build/molecular"
            (build / "geometries").mkdir(parents=True)
            (build / "geometries/cube-centred-X-8.txt").write_text("test geometry")
            (build / "molecular").write_text("placeholder, never executed")
            metadata = {"source_kind": "local-geant4-installation", "files_sha256": {"human_cell.mac": c.digest(src / "human_cell.mac")}}
            c.save_json(repo / "vendor/source.json", metadata)
            c.save_json(build / "source.json", metadata)
            cfg = copy.deepcopy(self.cfg)
            cfg.update(particles=["proton", "alpha"], energies=[1, 5], replicas=3)
            config = repo / "config.json"
            c.save_json(config, cfg)
            destination = repo / "runs/test"
            with patch.object(c, "REPO", repo):
                c.prepare(config, destination)
                manifest = json.loads((destination / "manifest.json").read_text())
                self.assertEqual(len(manifest["tasks"]), 12)
                seeds = [s for task in manifest["tasks"] for s in task["seeds"]]
                self.assertEqual(len(set(seeds)), 24)
                with self.assertRaises(FileExistsError):
                    c.prepare(config, destination)
                with patch.object(subprocess, "check_output", return_value="98765\n") as sbatch:
                    c.submit(destination, False)
                    args = sbatch.call_args.args[0]
                    self.assertIn("--array=0-11%1", args)
                    self.assertIn("--cpus-per-task=1", args)
                    self.assertTrue((destination / "submission.json").exists())
                    with self.assertRaises(ValueError):
                        c.submit(destination, False)


if __name__ == "__main__":
    unittest.main()
