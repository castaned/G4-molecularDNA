import importlib.util
import json
from pathlib import Path
import shutil
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("plot_task", ROOT / "scripts/plot_task.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class PlotTaskTests(unittest.TestCase):
    def setUp(self):
        self.folder = ROOT / "tests" / ("scratch_" + uuid.uuid4().hex)
        self.folder.mkdir()
        self.task = self.folder / "task_00000"
        self.task.mkdir()
        (self.folder / "manifest.json").write_text(json.dumps({"tasks": [{"particle": "alpha", "events": 10}]}))

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_reject_timeout_without_finished_record(self):
        with self.assertRaisesRegex(ValueError, "TIMEOUT"), patch.object(p.subprocess, "run") as runner:
            p.plot(self.folder, 0, 6405.886128)
        runner.assert_not_called()

    def test_alpha_selection_and_merge_only_recorded_shards(self):
        files = ["molecular-dna_t0.root", "molecular-dna_t1.root"]
        for name in files + ["unrelated.root"]:
            (self.task / name).write_bytes(b"fake fixture, not a ROOT file")
        (self.task / "finished.json").write_text(json.dumps({"success": True, "root_files": files}))
        def simulate_command(args, **kwargs):
            if args[0] == "root" and "human_cell_alphas.C" in args[-1]:
                (self.task / "plots/human_cell_alphas.png").write_bytes(b"fixture")
        with patch.object(p.subprocess, "run", side_effect=simulate_command) as runner:
            p.plot(self.folder, 0, 6405.886128)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertEqual(commands[0][0], "hadd")
        self.assertEqual(commands[0][3:], [str(self.task / name) for name in files])
        self.assertIn(",10)", commands[1][-1])
        self.assertIn("human_cell_alphas.C", commands[2][-1])
        self.assertNotIn("unrelated.root", str(commands))

    def test_failed_task_is_rejected(self):
        (self.task / "finished.json").write_text(json.dumps({"success": False}))
        with self.assertRaisesRegex(ValueError, "incompleta"):
            p.plot(self.folder, 0, 6405.886128)

    def test_alpha_budget(self):
        cfg = json.loads((ROOT / "config/alphas.json").read_text())
        self.assertEqual(cfg["particles"], ["alpha"])
        self.assertEqual(cfg["resources"]["time"], "12:00:00")
